#!/usr/bin/env python3
"""Stage-2 ablation baselines: budget-matched competitors to the full method.

Plan: doc/rubric_evolution_plan_2026-07-06.md §5 (消融矩阵). The full method
(run_judge_rubric_stage1.py) combines P1–P6: structured rubric + typed edits,
aggregated diagnosis-driven proposals, screen→full staging, and cluster-bootstrap
significance acceptance with regression ablation. This script runs the three
reference lines the ablation table compares it against, each on the SAME frozen
eval slice, judged by the SAME judge (glm-5.2), scored by the SAME paired
cluster-bootstrap CI vs the v1 incumbent — so the only variable is the search
procedure:

- ``manual`` (手工 J2b): one hand-authored structured rubric per line, written
  from general rubric best-practice (behavioral label anchors + a solve/reason-
  first instruction), BLIND to the eval-slice diagnosis and to the method's
  discovered clauses. A single design point (no search), evaluated once. Answers:
  what does careful human rubric design achieve without diagnostic search?
- ``genk`` (生成-K-选优, weak automation): one reflection call emits K free-text
  judging rules given ONLY the dimension definition + labels — NO confusion
  matrix, NO error examples, NO diagnosis. Each rule is evaluated on the full
  eval slice and the best is picked by RAW kappa (no screening, no significance
  gate, selecting on the very slice it reports). Isolates the value of diagnosis
  (P5) + statistical acceptance (P2/P3): its "best" is a winner's-curse upper
  bound whose paired CI we also report.
- ``gepa`` (GEPA 原味, strong automation): vanilla reflective free-text prompt
  evolution. A champion free-text rules block is mutated wholesale each iteration
  by reflecting on the champion's RAW disagreement cases (no aggregated
  diagnosis), greedily kept if it beats the champion's kappa on a held-out
  validation subset V (pool, disjoint from eval), for a budget-matched number of
  iterations; then the champion is evaluated once on the eval slice. Isolates
  structure (P1), aggregated diagnosis (P5), and significance-gated acceptance
  (P2/P3) while matching compute.

Budget: each SEARCH baseline (genk/gepa) is given the SAME number of judge calls
the full method actually spent on that line (measured, MEASURED_BUDGET). manual
is a single non-search design point (one full-slice pass). All judge + mutation
calls use glm-5.2 via the gateway (STAGE1_JUDGE_MODEL=glm-5.2 must be set so the
shared OUT_BASE resolves to stage1_glm-5.2/). Resumable via responses.jsonl.

Usage (judge + mutator = glm-5.2):
    STAGE1_JUDGE_MODEL=glm-5.2 python3 run_judge_rubric_ablation.py \
        --benchmark mrbench --dimension Providing_Guidance --baseline all --concurrency 6
"""

from __future__ import annotations

import argparse
import json
import random
import threading
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable

from eval.base import prompt_sha256
from eval.providers import build_client
from eval.stats import kappa_stat
from run_judge_rubric_stage1 import (
    BASELINE_DIRS,
    JUDGE_MODEL,
    JUDGE_SLUGS,
    OUT_BASE,
    REFLECT_MODEL,
    ROOT,
    Renderer,
    _read_jsonl,
    _write_json,
    apply_edits,
    cached_v1_pool_data,
    empty_rubric,
    paired_eval,
    pool_subsample,
    run_candidate,
)

# The method's ACTUAL per-line judge-call spend (sum of all responses.jsonl rows
# under stage1_glm-5.2/<line>/), measured 2026-07-09. Each search baseline gets
# the same budget so the ablation is equal-compute.
MEASURED_BUDGET: dict[tuple[str, str], int] = {
    ("mrbench", "Providing_Guidance"): 8731,
    ("bea2025", "Providing_Guidance"): 5643,
    ("mrbench", "Coherence"): 8566,
}

GEPA_VAL_TARGET = 200          # held-out validation subset size for GEPA selection
GEPA_MAX_EXTRA_CHARS = 15000   # generous ceiling; GEPA is *allowed* to bloat (P1)
GEPA_REFLECT_ERRORS = 12       # raw error cases shown to the mutator each iteration


# --- hand-authored "manual J2b" rubrics (typed edits; blind to eval diagnosis) ---
# Written from general analytic-rubric practice: behavioral anchors per label +
# a "reason out the correct move first" instruction. Deliberately NOT copied from
# the method's discovered winning clauses. All three dimensions share labels
# ('Yes', 'To some extent', 'No').
MANUAL_EDITS: dict[tuple[str, str], list[dict[str, Any]]] = {
    ("mrbench", "Providing_Guidance"): [
        {"op": "set_label_criterion", "label": "Yes",
         "text": "The reply gives correct, on-point help the student can act on — a hint, an explanation, a worked step, an example, or a focused question aimed at the specific error or next step."},
        {"op": "set_label_criterion", "label": "To some extent",
         "text": "The reply makes a real attempt to guide but it is incomplete, generic, or only partly on target, so it under-specifies what the student should do next."},
        {"op": "set_label_criterion", "label": "No",
         "text": "The reply provides no usable guidance — it only greets, praises, restates the problem, hands over the bare answer, or is irrelevant to the student's need."},
        {"op": "add_clause",
         "text": "First work out for yourself what correct guidance here would be, then judge the reply against that substance rather than its politeness, fluency, or length."},
    ],
    ("bea2025", "Providing_Guidance"): [
        {"op": "set_label_criterion", "label": "Yes",
         "text": "The reply supplies correct and relevant help the student can use — a hint, elaboration, example, explanation, or a supporting question that targets the actual difficulty."},
        {"op": "set_label_criterion", "label": "To some extent",
         "text": "The reply attempts relevant help but it is partial, vague, or only loosely tied to the student's error, leaving the next step under-specified."},
        {"op": "set_label_criterion", "label": "No",
         "text": "The reply offers no real guidance — it merely acknowledges, praises, repeats the task, states the answer outright, or is off the point."},
        {"op": "add_clause",
         "text": "Before choosing a label, reason out what the ideal next tutoring move would be, then score the reply on whether it delivers that help, not on tone or verbosity."},
    ],
    ("mrbench", "Coherence"): [
        {"op": "set_label_criterion", "label": "Yes",
         "text": "The reply follows logically from the conversation, engages with the student's latest turn, and contains no internal contradiction."},
        {"op": "set_label_criterion", "label": "To some extent",
         "text": "The reply is mostly on-topic but has a minor logical jump, mild redundancy, or a small inconsistency a reader can overlook."},
        {"op": "set_label_criterion", "label": "No",
         "text": "The reply contradicts itself or the earlier conversation, ignores the student's latest input, or is a generic remark unrelated to this exchange."},
        {"op": "add_clause",
         "text": "Read the student's most recent turn first and check the reply actually responds to it; a fluent but canned line that does not engage the specific input is not coherent."},
    ],
}


def v1_eval_labels(rnd: Renderer, benchmark: str) -> dict[str, str]:
    """v1 incumbent labels on the eval slice from the judge's cached full run.
    Forced to v1 (ignores any evolved rubric_current.json) — the ablation headline
    is always <baseline> vs v1, matching the method's own 'v1 -> final' headline."""
    slug = JUDGE_SLUGS[JUDGE_MODEL]
    scored = ROOT / "reports" / "eval" / BASELINE_DIRS[benchmark] / slug / "scored.jsonl"
    labels = {
        str(r["item_id"]): str(r["pred_label"])
        for r in _read_jsonl(scored)
        if r.get("score_status") == "scored" and "pred_label" in r and str(r["item_id"]) in rnd.eval_ids
    }
    if not labels:
        raise SystemExit(f"no cached v1 labels for {JUDGE_MODEL} under {scored}")
    return labels


def kappa_on(rnd: Renderer, labels: dict[str, str], items: list[dict[str, Any]]) -> float | None:
    pairs = [(it["human_label"], labels[it["native_item_id"]])
             for it in items if it["native_item_id"] in labels]
    return kappa_stat(pairs)


# ---------------------------------------------------------------- manual --------
def run_manual(rnd: Renderer, args: argparse.Namespace, out_dir: Path, client: Any,
               v1_labels: dict[str, str]) -> dict[str, Any]:
    edits = MANUAL_EDITS[(args.benchmark, args.dimension)]
    rubric = apply_edits(empty_rubric(args.benchmark, args.dimension), edits, rnd.labels)
    template = rnd.render_template(rubric)
    print(f"[manual] template +{len(template) - rnd.v1_template_len} chars vs v1")
    labels = run_candidate(rnd, rubric, rnd.eval_items, out_dir / "responses.jsonl",
                           client, args.concurrency, args.retries)
    res = paired_eval(rnd, labels, v1_labels, rnd.eval_ids, args.n_boot)
    print(f"[manual] v1 {res['point_b']} -> manual {res['point_a']} "
          f"(diff {res['point']} [{res['ci_low']}, {res['ci_high']}] sig={res['significant']}, n={res['n_paired']})")
    return {
        "baseline": "manual_j2b",
        "description": "hand-authored structured rubric (behavioral anchors + solve-first), blind to eval diagnosis",
        "edits": edits,
        "prompt_sha256": prompt_sha256(template),
        "extra_chars": len(template) - rnd.v1_template_len,
        "result_vs_v1": res,
    }


# ------------------------------------------------------------------- genk --------
def genk_prompt(rnd: Renderer, k: int) -> str:
    return (
        "You are improving the rubric of an LLM judge that labels AI tutor replies on the "
        f"pedagogical dimension \"{rnd.cfg['title']}\": {rnd.cfg['definition']}\n"
        f"The judge must pick exactly one of: {' / '.join(rnd.labels)}.\n\n"
        f"Propose {k} DISTINCT additional judging rules that would make the judge agree better "
        "with expert human annotators. Each rule is one or two sentences, behavioral (describe "
        "what a reply DOES), and must not merely restate the label names.\n\n"
        "Output ONLY a JSON array of strings, no markdown fences."
    )


def parse_rules(text: str) -> list[str]:
    start, end = text.find("["), text.rfind("]")
    if start < 0 or end <= start:
        raise ValueError("no JSON array")
    arr = json.loads(text[start:end + 1])
    return [str(x).strip() for x in arr if isinstance(x, (str,)) and str(x).strip()]


def run_genk(rnd: Renderer, args: argparse.Namespace, out_dir: Path, client: Any,
             v1_labels: dict[str, str], budget: int) -> dict[str, Any]:
    k = max(1, round(budget / max(1, len(rnd.eval_items))))
    prompt = genk_prompt(rnd, k)
    raw_path = out_dir / "generation_raw.txt"
    rules_path = out_dir / "rules.json"
    if rules_path.exists():
        rules = json.loads(rules_path.read_text(encoding="utf-8"))
    else:
        reflect = build_client(REFLECT_MODEL)
        rules, raws = [], []
        for _ in range(3):
            raw = reflect.chat([{"role": "user", "content": prompt}], model=REFLECT_MODEL)
            raws.append(raw)
            try:
                rules = parse_rules(raw)
            except ValueError:
                rules = []
            if len(rules) >= k:
                break
        raw_path.write_text("\n\n=====\n\n".join(raws), encoding="utf-8")
        rules = rules[:k]
        _write_json(rules_path, rules)
    print(f"[genk] K={k} rules generated (no diagnosis)")

    cands = []
    for i, rule in enumerate(rules, 1):
        rubric = apply_edits(empty_rubric(args.benchmark, args.dimension),
                             [{"op": "add_clause", "text": rule}], rnd.labels)
        labels = run_candidate(rnd, rubric, rnd.eval_items, out_dir / f"cand_{i:02d}" / "responses.jsonl",
                               client, args.concurrency, args.retries)
        kap = kappa_on(rnd, labels, rnd.eval_items)
        cands.append({"i": i, "rule": rule, "kappa_eval": kap, "labels": labels})
        print(f"[genk] rule {i:02d}/{len(rules)} eval-kappa {kap}")

    scored = [c for c in cands if c["kappa_eval"] is not None]
    best = max(scored, key=lambda c: c["kappa_eval"]) if scored else None
    kappas = sorted(c["kappa_eval"] for c in scored)
    # Naive select-best reports the winning candidate's own paired CI vs v1 — this
    # is selection ON the reported slice, i.e. a winner's-curse-inflated upper bound.
    best_res = paired_eval(rnd, best["labels"], v1_labels, rnd.eval_ids, args.n_boot) if best else None
    if best:
        print(f"[genk] best rule #{best['i']} eval-kappa {best['kappa_eval']} "
              f"(v1 {best_res['point_b']}, diff {best_res['point']} [{best_res['ci_low']}, {best_res['ci_high']}] "
              f"sig={best_res['significant']}); mean over K {round(sum(kappas)/len(kappas), 4)}")
    return {
        "baseline": "generate_k_select_best",
        "description": "K free-text rules from one no-diagnosis call; best picked by raw eval kappa (no significance gate)",
        "k": k,
        "v1_kappa_eval": kappa_on(rnd, v1_labels, rnd.eval_items),
        "candidate_kappas": [{"i": c["i"], "kappa_eval": c["kappa_eval"], "rule": c["rule"]} for c in cands],
        "kappa_distribution": {
            "min": kappas[0] if kappas else None,
            "median": kappas[len(kappas) // 2] if kappas else None,
            "max": kappas[-1] if kappas else None,
            "mean": round(sum(kappas) / len(kappas), 4) if kappas else None,
        },
        "naive_best": {
            "i": best["i"] if best else None,
            "rule": best["rule"] if best else None,
            "selected_on": "eval slice (optimistic / winner's-curse upper bound)",
            "result_vs_v1": best_res,
        },
    }


# ------------------------------------------------------------------- gepa --------
def render_freetext(rnd: Renderer, addendum: str, conv_hist: str, response: str) -> str:
    base = rnd.judge_prompt(rnd.dim, conv_hist, response)
    if addendum.strip():
        head, tail = base.rsplit("\n\nChoose", 1)
        base = f"{head}\n\n{addendum.strip()}\n\nChoose{tail}"
    return base


def run_freetext(rnd: Renderer, addendum: str, items: list[dict[str, Any]], resp_path: Path,
                 client: Any, concurrency: int, retries: int) -> dict[str, str]:
    """Judge ``items`` under a free-text addendum (GEPA champion). Mirrors
    run_candidate's resumable/circuit-breaker semantics but bypasses the
    structured Renderer so the mutated block is genuinely unstructured."""
    item_ids = {it["native_item_id"] for it in items}
    done = {r["item_id"]: r for r in _read_jsonl(resp_path) if str(r.get("response") or "").strip()}
    todo = [it for it in items if it["native_item_id"] not in done]
    consecutive_failures = [0]
    lock = threading.Lock()

    def call(it: dict[str, Any]) -> dict[str, Any]:
        prompt = render_freetext(rnd, addendum, rnd.contexts.get(it["conversation_id"], ""), it["response"])
        started, error, text = time.time(), None, ""
        for attempt in range(retries):
            try:
                text = client.chat([{"role": "user", "content": prompt}], model=JUDGE_MODEL)
                error = None
                if text.strip():
                    break
            except Exception as exc:  # noqa: BLE001
                error = str(exc)
            time.sleep(2.0 * (attempt + 1))
        row = {"item_id": it["native_item_id"], "response": text,
               "latency_seconds": round(time.time() - started, 2)}
        if error:
            row["error"] = error
        with lock:
            consecutive_failures[0] = consecutive_failures[0] + 1 if not text.strip() else 0
            if consecutive_failures[0] >= 25:
                raise SystemExit(f"aborting: 25 consecutive failed judge calls (last: {error})")
        return row

    if todo:
        resp_path.parent.mkdir(parents=True, exist_ok=True)
        with ThreadPoolExecutor(max_workers=concurrency) as pool, resp_path.open("a", encoding="utf-8") as fh:
            for row in pool.map(call, todo):
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                fh.flush()
        done = {r["item_id"]: r for r in _read_jsonl(resp_path) if str(r.get("response") or "").strip()}
    return {iid: rnd.normalize(rnd.dim, r["response"]) for iid, r in done.items() if iid in item_ids}


def gepa_mutate_prompt(rnd: Renderer, champion: str, errors: list[dict[str, Any]]) -> str:
    cases = []
    for e in errors:
        cases.append(
            f"- Tutor reply: {str(e['response'])[:360]}\n"
            f"    Judge said: {e['judge']} | Human expert said: {e['human']}"
        )
    return (
        "You are editing the free-text judging-rules block of an LLM judge that labels AI tutor "
        f"replies on \"{rnd.cfg['title']}\": {rnd.cfg['definition']}\n"
        f"The judge picks exactly one of: {' / '.join(rnd.labels)}.\n\n"
        "Current judging-rules block (may be empty):\n"
        f"\"\"\"\n{champion or '(none yet)'}\n\"\"\"\n\n"
        "Cases where this judge disagreed with the human expert:\n"
        + "\n".join(cases)
        + "\n\nRewrite the ENTIRE judging-rules block so the judge would agree with the human "
        "expert on cases like these while staying correct elsewhere. Output ONLY the new "
        "rules-block text (plain prose or bullet points), with no preamble and no code fences."
    )


def run_gepa(rnd: Renderer, args: argparse.Namespace, out_dir: Path, client: Any,
             v1_labels: dict[str, str], budget: int) -> dict[str, Any]:
    val = pool_subsample(rnd, GEPA_VAL_TARGET)
    val_ids = {it["native_item_id"] for it in val}
    assert not (val_ids & rnd.eval_ids), "GEPA validation set overlaps eval slice"
    n_iter = max(1, (budget - len(rnd.eval_items)) // max(1, len(val)))
    reflect = build_client(REFLECT_MODEL)

    state_path = out_dir / "gepa_state.json"
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
    else:
        # Champion 0 = v1 (empty addendum). Its val labels are free from cache.
        v1_val_labels, _ = cached_v1_pool_data(args.benchmark, val_ids)
        champ_kappa = kappa_on(rnd, v1_val_labels, val)
        state = {
            "n_iter": n_iter, "val_n": len(val), "iter_done": 0,
            "champion_addendum": "", "champion_kappa_val": champ_kappa,
            "champion_source": "v1", "history": [],
        }
        _write_json(state_path, state)
    print(f"[gepa] budget={budget} val={len(val)} n_iter={n_iter} "
          f"start_iter={state['iter_done']} champ_val_kappa={state['champion_kappa_val']}")

    for it_no in range(state["iter_done"] + 1, state["n_iter"] + 1):
        # errors of the current champion on val — read from labels that already
        # exist (v1 from cache, or the accepted candidate's own cand_iter file),
        # so re-diagnosing the champion each iteration costs 0 new judge calls.
        if state["champion_source"] == "v1":
            champ_labels, _ = cached_v1_pool_data(args.benchmark, val_ids)
        else:
            n = state["champion_source"].replace("iter", "")
            champ_labels = run_freetext(rnd, state["champion_addendum"], val,
                                        out_dir / f"cand_iter{n}" / "responses.jsonl",
                                        client, args.concurrency, args.retries)
        errors = []
        rng = random.Random(f"gepa:{args.benchmark}:{args.dimension}:{it_no}")
        pool_err = [it for it in val if champ_labels.get(it["native_item_id"]) not in (None, it["human_label"])]
        rng.shuffle(pool_err)
        for it in pool_err[:GEPA_REFLECT_ERRORS]:
            errors.append({"response": it["response"], "judge": champ_labels[it["native_item_id"]],
                           "human": it["human_label"]})
        if not errors:
            print(f"[gepa] iter {it_no}: champion has no val errors — stop")
            break

        mut_prompt = gepa_mutate_prompt(rnd, state["champion_addendum"], errors)
        new_add = ""
        for _ in range(3):
            new_add = reflect.chat([{"role": "user", "content": mut_prompt}], model=REFLECT_MODEL).strip()
            if new_add:
                break
        (out_dir / f"mutation_iter{it_no}.txt").write_text(new_add, encoding="utf-8")
        tmpl_extra = len(render_freetext(rnd, new_add, "{conversation_history}", "{response}")) - rnd.v1_template_len
        rec: dict[str, Any] = {"iter": it_no, "extra_chars": tmpl_extra, "accepted": False}
        if not new_add or tmpl_extra > GEPA_MAX_EXTRA_CHARS:
            rec["skipped"] = "empty" if not new_add else "over_ceiling"
            state["history"].append(rec)
            state["iter_done"] = it_no
            _write_json(state_path, state)
            print(f"[gepa] iter {it_no}: skipped ({rec['skipped']})")
            continue

        cand_labels = run_freetext(rnd, new_add, val, out_dir / f"cand_iter{it_no}" / "responses.jsonl",
                                   client, args.concurrency, args.retries)
        cand_kappa = kappa_on(rnd, cand_labels, val)
        rec["kappa_val"] = cand_kappa
        rec["champion_kappa_val"] = state["champion_kappa_val"]
        if cand_kappa is not None and (state["champion_kappa_val"] is None or cand_kappa > state["champion_kappa_val"]):
            rec["accepted"] = True
            state["champion_addendum"] = new_add
            state["champion_kappa_val"] = cand_kappa
            state["champion_source"] = f"iter{it_no}"
        state["history"].append(rec)
        state["iter_done"] = it_no
        _write_json(state_path, state)
        print(f"[gepa] iter {it_no}/{state['n_iter']}: cand_val_kappa {cand_kappa} "
              f"vs champ {rec['champion_kappa_val']} -> {'ACCEPT' if rec['accepted'] else 'keep'}")

    # final: champion on the eval slice, paired CI vs v1
    if state["champion_addendum"]:
        final_labels = run_freetext(rnd, state["champion_addendum"], rnd.eval_items,
                                    out_dir / "final_eval" / "responses.jsonl",
                                    client, args.concurrency, args.retries)
    else:
        final_labels = dict(v1_labels)  # champion never left v1
    res = paired_eval(rnd, final_labels, v1_labels, rnd.eval_ids, args.n_boot)
    final_tmpl = render_freetext(rnd, state["champion_addendum"], "{conversation_history}", "{response}")
    print(f"[gepa] FINAL v1 {res['point_b']} -> gepa {res['point_a']} "
          f"(diff {res['point']} [{res['ci_low']}, {res['ci_high']}] sig={res['significant']}, n={res['n_paired']})")
    return {
        "baseline": "gepa_vanilla",
        "description": "reflective free-text prompt evolution; wholesale rewrite, raw-error reflection, greedy accept on held-out val (no diagnosis/structure/significance gate)",
        "n_iter_budget": state["n_iter"],
        "iters_run": state["iter_done"],
        "val_n": state["val_n"],
        "champion_source": state["champion_source"],
        "champion_kappa_val": state["champion_kappa_val"],
        "champion_extra_chars": len(final_tmpl) - rnd.v1_template_len,
        "champion_prompt_sha256": prompt_sha256(final_tmpl),
        "champion_addendum": state["champion_addendum"],
        "accept_history": state["history"],
        "result_vs_v1": res,
    }


BASELINES: dict[str, Callable[..., dict[str, Any]]] = {
    "manual": run_manual, "genk": run_genk, "gepa": run_gepa,
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--benchmark", required=True, choices=sorted(BASELINE_DIRS))
    parser.add_argument("--dimension", required=True)
    parser.add_argument("--baseline", required=True, choices=["manual", "genk", "gepa", "all"])
    parser.add_argument("--concurrency", type=int, default=6)
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--n-boot", type=int, default=1000)
    parser.add_argument("--budget", type=int, default=0,
                        help="judge-call budget for search baselines; 0 = measured method spend")
    parser.add_argument("--big-screen", action="store_true", default=True,
                        help="(always on) use the 250-item screening slice for Renderer parity")
    args = parser.parse_args()

    key = (args.benchmark, args.dimension)
    budget = args.budget or MEASURED_BUDGET.get(key, 6000)
    rnd = Renderer(args.benchmark, args.dimension, big_screen=True)
    line_dir = OUT_BASE / f"{args.benchmark}__{args.dimension}" / "ablation"
    line_dir.mkdir(parents=True, exist_ok=True)
    v1_labels = v1_eval_labels(rnd, args.benchmark)
    client = build_client(JUDGE_MODEL)
    v1_kappa = kappa_on(rnd, v1_labels, rnd.eval_items)
    print(f"{args.benchmark}/{args.dimension}: judge={JUDGE_MODEL} eval={len(rnd.eval_ids)} "
          f"v1_kappa={v1_kappa} budget={budget}")

    todo = ["manual", "genk", "gepa"] if args.baseline == "all" else [args.baseline]
    results = {}
    for name in todo:
        out_dir = line_dir / name
        out_dir.mkdir(parents=True, exist_ok=True)
        fn = BASELINES[name]
        if name == "manual":
            results[name] = fn(rnd, args, out_dir, client, v1_labels)
        else:
            results[name] = fn(rnd, args, out_dir, client, v1_labels, budget)
        _write_json(out_dir / "summary.json", results[name])

    agg = {
        "stage": "stage2 ablation baselines",
        "plan": "doc/rubric_evolution_plan_2026-07-06.md §5",
        "benchmark": args.benchmark,
        "dimension": args.dimension,
        "judge_model": JUDGE_MODEL,
        "reflect_model": REFLECT_MODEL,
        "budget_calls": budget,
        "eval_n": len(rnd.eval_ids),
        "v1_kappa_eval": v1_kappa,
        "baselines": {
            name: {k: v for k, v in results[name].items()
                   if k not in ("candidate_kappas", "accept_history", "champion_addendum")}
            for name in results
        },
    }
    _write_json(line_dir / "summary.json", agg)
    print(f"\nwrote {line_dir / 'summary.json'}")


if __name__ == "__main__":
    main()
