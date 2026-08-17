#!/usr/bin/env python3
"""Build AgenticEdu Continuum - the interactive atomic-ability explorer (v6 mapping, R25).

Reads the frozen rebenchmark artifacts plus the v6 measurement model and the
benchmark profile archive, embeds everything as one JSON payload, and emits a
single self-contained HTML page with four cross-linked views:

    overview    model x ability heat matrix
    model       radar over the 20 abilities + facet/benchmark drill-down
    ability     what a P measures, how it is measured, who scores well on it
    benchmark   profile card, confidence weight, which P facets it feeds,
                and the per-subdimension model leaderboard

No scores are recomputed here - this is a presentation layer over
`reports/atomic_ability_rebenchmark/`. Idempotent: rerunning
overwrites the output byte-for-byte.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
REBENCH = ROOT / "reports" / "atomic_ability_rebenchmark"
MAPPING_JSON = ROOT / "data" / "mapping_measurement_model_v6.json"
MAPPING_DOC = ROOT / "doc" / "atomic_ability_mapping_v6_2026-07-19.md"
PROFILE_DIR = ROOT / "doc" / "benchmark_profiles"
ABILITY_PROFILE_DIR = ROOT / "doc" / "ability_profiles"
OUT_PATH = ROOT / "html_report" / "atomic_ability_explorer_2026-07-19.html"

GROUP_LABELS = {
    "SRG": "任务理解与多模态交互",
    "FDR": "知识推理与可靠执行",
    "LAD": "学习诊断与教育测评",
    "CLM": "学习者建模与适应性教学",
    "CEG": "教育安全与学术规范",
}
GROUP_ORDER = ["SRG", "FDR", "LAD", "CLM", "CEG"]

# The two tiers above the five groups. Source of truth is
# `doc/atomic_ability_mapping_v6_2026-07-19.md` §大类划分 - a presentation-layer
# split that does **not** enter the measurement model: weights, facet structure
# and aggregation are unchanged by it. This only makes that table machine
# readable so the website can section by it. No tier-level score exists.
TIER_LABELS = {
    "BASE": "通用基础能力",
    "EDU": "教育专属能力",
}
TIER_ORDER = ["BASE", "EDU"]
GROUP_TIER = {"SRG": "BASE", "FDR": "BASE", "LAD": "EDU", "CLM": "EDU", "CEG": "EDU"}

# Every benchmark_id now owns a profile file; the map only covers ids whose
# filename differs. It used to fold 17 sub-task ids onto 5 family files, which
# made a sub-task page show the whole family's task table - 8 of 9 rows about
# some other cell - while the family's mapping notes contradicted the sub-task's
# actual P list. mathtutorbench.md / eduguard_bench.md / mrbench.md /
# bea2025.md / p08_selfbuilt.md stay in the archive as family background and are
# no longer read by the build.
PROFILE_MAP = {
    "mooccube_prereq": "mooccube",
}

MODEL_DISPLAY = {
    "claude-sonnet-4.6": "Claude Sonnet 4.6",
    "deepseek-r1-0528-qwen3-8b": "DeepSeek-R1-0528-Qwen3-8B",
    "deepseek-v3-2": "DeepSeek-V3.2",
    "deepseek-v4-flash": "DeepSeek-V4-Flash",
    "deepseek-v4-pro": "DeepSeek-V4-Pro",
    "doubao-seed-2-0-lite": "Doubao-Seed-2.0-Lite",
    "doubao-seed-2-0-pro": "Doubao-Seed-2.0-Pro",
    "glm-5.1": "GLM-5.1",
    "glm-5.2": "GLM-5.2",
    "gpt-5.4": "GPT-5.4",
    "gpt-5.5": "GPT-5.5",
    "kimi-k2-6": "Kimi-K2.6",
    "kimi-k2-7-code": "Kimi-K2.7-Code",
    "minimax-m2.7": "MiniMax-M2.7",
    "minimax-m3": "MiniMax-M3",
    # Self-hosted vLLM runs. Their keys come from the run directory name
    # (`Qwen/Qwen3.5-4B` -> `qwen-qwen3-5-4b`), so they carry the vendor prefix
    # the API-routed models do not. Missing entries fall back to the raw key
    # silently, which is how these two shipped a slug as a display name.
    "qwen-qwen3-5-4b": "Qwen3.5-4B",
    "qwen-qwen3-8b": "Qwen3-8B",
    "qwen3-14b": "Qwen3-14B",
    "qwen3-5-122b-a10b": "Qwen3.5-122B-A10B",
    "qwen3-5-27b": "Qwen3.5-27B",
    "qwen3-5-35b-a3b": "Qwen3.5-35B-A3B",
    "qwen3-6-35b-a3b": "Qwen3.6-35B-A3B",
    "qwen3-vl-235b": "Qwen3-VL-235B",
    "qwen3.7-max": "Qwen3.7-Max",
}


AGG_SCRIPT = ROOT / "scripts" / "build_atomic_ability_rebenchmark_artifacts.py"


def read_panel_keys() -> list[str]:
    """Read PANEL_MODEL_KEYS off the aggregation script.

    Only the panel list is mirrored here (to label the release panel).  Since
    R26 the page no longer re-derives any missing-cell rule client-side — the
    aggregation script decides 未测过 vs 能力不具备记 0 分 and the page just
    renders what it emitted.
    """
    src = AGG_SCRIPT.read_text(encoding="utf-8")
    block = re.search(r"PANEL_MODEL_KEYS\s*=\s*\((.*?)\)", src, re.S)
    return re.findall(r'"([^"]+)"', block.group(1)) if block else []


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def parse_ability_definitions(text: str) -> dict[str, str]:
    """Pull the one-line P definitions out of the two tables in section 1."""
    defs = {}
    for row in re.finditer(r"^\|\s*(P\d{2})\s*\|([^|]+)\|([^|]+)\|", text, re.M):
        defs[row.group(1)] = row.group(3).strip()
    return defs


def parse_boundaries(text: str) -> list[dict[str, str]]:
    """Pull the pairwise disambiguation bullets under `### 边界口径`."""
    block = re.search(r"### 边界口径\n(.*?)\n## ", text, re.S)
    if not block:
        return []
    out = []
    for line in block.group(1).splitlines():
        line = line.strip()
        if not line.startswith("- "):
            continue
        body = line[2:]
        head = re.match(r"\*\*(.+?)\*\*[:：](.*)", body)
        if head:
            out.append({"title": head.group(1).strip(), "text": strip_markdown(head.group(2))})
        else:
            out.append({"title": "", "text": strip_markdown(body)})
    return out


def strip_markdown(text: str) -> str:
    """Flatten inline markdown to plain text - the page renders its own styling."""
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = text.replace("**", "").replace("`", "")
    return text.strip()


def parse_profile(path: Path) -> dict[str, Any]:
    """Split a benchmark profile into its `##` sections.

    The `当前映射` section is deliberately dropped: it uses pre-R20 P numbering
    and predates R25, so live mapping is recomputed from the v6 JSON instead.
    """
    raw = path.read_text(encoding="utf-8")
    title = ""
    head = re.search(r"^# (.+)$", raw, re.M)
    if head:
        title = strip_markdown(head.group(1))
    one_liner = ""
    hit = re.search(r"\*\*一句话\*\*[:：](.+?)(?:\n\n|\n##)", raw, re.S)
    if hit:
        one_liner = strip_markdown(hit.group(1))
    sections = []
    for match in re.finditer(r"^## (.+?)\n(.*?)(?=^## |\Z)", raw, re.S | re.M):
        heading = match.group(1).strip()
        if heading.startswith("当前映射"):
            continue
        body = match.group(2).strip()
        bullets = []
        in_fence = False
        for line in body.splitlines():
            line = line.strip()
            # Fenced command blocks are run instructions, not prose - drop them
            # rather than spilling "bash" and bare shell lines into the card.
            if line.startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence or line.startswith("|") or line.startswith("#"):
                continue
            if line.startswith("- ") or line.startswith("* "):
                line = line[2:]
            text = strip_markdown(line)
            if text:
                bullets.append(text)
        if bullets:
            sections.append({"heading": heading, "bullets": bullets})
    return {"title": title, "one_liner": one_liner, "sections": sections, "file": path.name}


def build_payload() -> dict[str, Any]:
    doc_text = MAPPING_DOC.read_text(encoding="utf-8")
    model_json = json.loads(MAPPING_JSON.read_text(encoding="utf-8"))
    p_scores = load_jsonl(REBENCH / "09_atomic_p_scores.jsonl")
    evidence = load_jsonl(REBENCH / "09_atomic_p_score_evidence.jsonl")
    untested = load_jsonl(REBENCH / "09_atomic_p_untested_cells.jsonl")
    group_scores = load_jsonl(REBENCH / "10_group_scores.jsonl")
    bench_map = load_jsonl(REBENCH / "02_benchmark_ability_mapping.jsonl")
    validity = load_jsonl(REBENCH / "13_mapping_validation_cells.jsonl")

    definitions = parse_ability_definitions(doc_text)
    boundaries = parse_boundaries(doc_text)

    # --- abilities -------------------------------------------------------
    p_group = {row["p_code"]: row["group"] for row in p_scores}
    missing_ability_profiles = []
    abilities = []
    for ability in model_json["abilities"]:
        code = ability["p_code"]
        if ability.get("model_type") == "tombstone":
            continue
        facets = []
        for facet in ability.get("facets", []):
            facets.append(
                {
                    "facet_id": facet["facet_id"],
                    "facet_name": facet.get("facet_name", facet["facet_id"]),
                    "facet_description": facet.get("facet_description", ""),
                    "revision_rationale": facet.get("revision_rationale", ""),
                    "coverage_gap": facet.get("coverage_gap"),
                    "cells": [
                        {
                            "benchmark_id": cell["benchmark_id"],
                            "subdimension": cell["subdimension"],
                            "weight": cell["weight"],
                            "revision_rationale": cell.get("revision_rationale", ""),
                        }
                        for cell in facet.get("cells", [])
                    ],
                }
            )
        # Reader-facing prose lives in doc/ability_profiles/<P>.md and uses the
        # same `##` section shape as the benchmark archive, so one parser serves
        # both. Weights are never written there - they are recomputed below.
        profile_path = ABILITY_PROFILE_DIR / f"{code}.md"
        if profile_path.exists():
            profile = parse_profile(profile_path)
            profile["missing"] = False
        else:
            missing_ability_profiles.append(code)
            profile = {"title": "", "one_liner": "", "sections": [], "file": "", "missing": True}
        abilities.append(
            {
                "p_code": code,
                "p_name": ability["p_name"],
                "group": p_group.get(code, ability.get("group", "")),
                "definition": definitions.get(code, ""),
                "model_type": ability.get("model_type", ""),
                "rationale": ability.get("rationale", ""),
                "coverage_gap": ability.get("coverage_gap"),
                "single_source": ability.get("single_source"),
                "facets": facets,
                "profile": profile,
            }
        )
    abilities.sort(key=lambda a: a["p_code"])

    if missing_ability_profiles:
        print(f"WARNING: no ability profile for {len(missing_ability_profiles)} P: "
              f"{', '.join(missing_ability_profiles)}")

    # --- benchmarks ------------------------------------------------------
    evidence_bench_ids = {row["benchmark_id"] for row in evidence}
    bench_meta: dict[str, dict[str, Any]] = {}
    for row in bench_map:
        entry = bench_meta.setdefault(
            row["benchmark_id"],
            {
                "id": row["benchmark_id"],
                "name": row.get("benchmark_name", row["benchmark_id"]),
                "confidence": row.get("default_benchmark_weight"),
                "metric_family": row.get("metric_family", ""),
                "score_direction": row.get("score_direction", ""),
                "source_scope": row.get("source_scope", ""),
                "rationale": row.get("rationale", ""),
            },
        )
        if not entry["rationale"] and row.get("rationale"):
            entry["rationale"] = row["rationale"]

    profile_cache: dict[str, dict[str, Any]] = {}
    missing_profiles = []
    benchmarks = []
    for bid in sorted(evidence_bench_ids):
        meta = bench_meta.get(bid, {"id": bid, "name": bid})
        stem = PROFILE_MAP.get(bid, bid)
        path = PROFILE_DIR / f"{stem}.md"
        if path.exists():
            if stem not in profile_cache:
                profile_cache[stem] = parse_profile(path)
            profile = dict(profile_cache[stem])
            profile["missing"] = False
        else:
            missing_profiles.append(bid)
            profile = {"title": "", "one_liner": "", "sections": [], "file": "", "missing": True}
        entry = {
            "id": bid,
            "name": meta.get("name", bid),
            "confidence": meta.get("confidence"),
            "metric_family": meta.get("metric_family", ""),
            "score_direction": meta.get("score_direction", ""),
            "source_scope": meta.get("source_scope", ""),
            "rationale": meta.get("rationale", ""),
            "profile": profile,
        }
        benchmarks.append(entry)

    if missing_profiles:
        print(f"WARNING: no profile for {len(missing_profiles)} benchmark(s): "
              f"{', '.join(missing_profiles)}")

    # --- cell discriminability, keyed by benchmark_id + subdimension -----
    validity_index = {}
    for row in validity:
        key = f"{row['benchmark_id']}||{row['subdimension']}"
        validity_index[key] = {
            "n_models": row.get("n_models"),
            "mean": row.get("mean_score_10"),
            "sd": row.get("sd_score_10"),
            "flags": row.get("flags") or [],
            "variance_restricted": bool(row.get("variance_restricted")),
            "excluded": row.get("excluded"),
        }

    # --- models ----------------------------------------------------------
    # R26 起 09_atomic_p_scores.jsonl 也收录「未测过」的 P 行（score_10=None），
    # 它们不算覆盖，不能进 covered_p / p_count，否则覆盖率会把空白算成有数据。
    p_scores = [row for row in p_scores if row.get("score_10") is not None]
    covered_p = sorted({row["p_code"] for row in p_scores})
    p_count = {}
    ev_count = {}
    for row in p_scores:
        p_count[row["model_key"]] = p_count.get(row["model_key"], 0) + 1
    for row in evidence:
        ev_count[row["model_key"]] = ev_count.get(row["model_key"], 0) + 1
    panel_keys = read_panel_keys()
    panel_set = set(panel_keys)
    models = []
    for key in sorted(p_count, key=lambda k: (-p_count[k], -ev_count.get(k, 0), k)):
        models.append(
            {
                "key": key,
                "display": MODEL_DISPLAY.get(key, key),
                "p_count": p_count[key],
                "evidence_count": ev_count.get(key, 0),
                # R26：「发布面板」就是 PANEL_MODEL_KEYS 的成员，不再等价于
                # 「每个 P 都有分」——以前两者重合，只是因为缺格被替代值填满了。
                # 覆盖完整度由 p_count 单独呈现，不再混进这个标记。
                "full_panel": key in panel_set,
            }
        )

    # --- compact score + evidence tables ---------------------------------
    slim_scores = [
        {
            "m": row["model_key"],
            "p": row["p_code"],
            "s": round(row["score_10"], 4),
            "facets": {k: round(v, 4) for k, v in (row.get("facet_scores") or {}).items()},
            "n": row.get("evidence_count", 0),
            "zero": row.get("capability_zero_count", 0),
            "zerow": round(row.get("capability_zero_weight_share", 0.0), 4),
            "unt": row.get("untested_cell_count", 0),
            "untc": row.get("untested_cells", []),
            "nf": row.get("facet_count_with_evidence", 0),
            "b": row.get("benchmarks", []),
        }
        for row in p_scores
    ]
    slim_evidence = [
        {
            "m": row["model_key"],
            "p": row["p_code"],
            "f": row["facet_id"],
            "fn": row.get("facet_name", ""),
            "b": row["benchmark_id"],
            "sd": row["subdimension"],
            "rel": row.get("ability_weight"),
            "conf": row.get("row_weight"),
            "eff": row.get("effective_weight"),
            "raw": row.get("raw_value"),
            # 6dp, not 4: the page re-derives P scores from these rows, and
            # 4dp inputs accumulate ~1e-4 of drift through the weighted average.
            "s": round(row["score_10"], 6) if row.get("score_10") is not None else None,
            "metric": row.get("metric", ""),
            "src": row.get("source_type", ""),
            # R26：zero=该格因模型不具备必需能力记 0 分（计分），why=一句话理由。
            "zero": row.get("source_type") == "capability_gap_zero",
            "cap": row.get("missing_capability", ""),
            "why": row.get("coverage_reason", ""),
        }
        for row in evidence
    ]
    slim_untested = [
        {
            "m": row["model_key"],
            "p": row["p_code"],
            "f": row["facet_id"],
            "fn": row.get("facet_name", ""),
            "b": row["benchmark_id"],
            "sd": row["subdimension"],
            "rel": row.get("ability_weight"),
            "conf": row.get("row_weight"),
            "eff": row.get("effective_weight"),
            "why": row.get("coverage_reason", ""),
        }
        for row in untested
    ]
    slim_groups = [
        {
            "m": row["model_key"],
            "g": row["group"],
            "s": round(row["score_10"], 4),
            "np": row.get("p_count_with_evidence", 0),
            "p": row.get("p_codes", []),
        }
        for row in group_scores
    ]

    payload = {
        "meta": {
            "version": model_json.get("version", ""),
            "date": model_json.get("date", ""),
            "source_dir": str(REBENCH.relative_to(ROOT)),
            "n_models": len(models),
            "n_abilities_total": len(abilities),
            "n_abilities_covered": len(covered_p),
            "n_benchmarks": len(benchmarks),
            "n_evidence": len(slim_evidence),
            "full_panel_size": sum(1 for m in models if m["full_panel"]),
            "uncovered_p": [a["p_code"] for a in abilities if a["p_code"] not in covered_p],
            "n_zero_cells": sum(1 for r in slim_evidence if r["zero"]),
            "n_untested_cells": len(slim_untested),
        },
        "panel": panel_keys,
        # Membership lives on the group only (`tier`), never mirrored back into
        # `tiers` - one place to read it, one place to get it wrong.
        "tiers": [{"id": t, "label": TIER_LABELS[t]} for t in TIER_ORDER],
        "groups": [
            {"id": g, "label": GROUP_LABELS[g], "tier": GROUP_TIER[g]} for g in GROUP_ORDER
        ],
        "abilities": abilities,
        "boundaries": boundaries,
        "benchmarks": benchmarks,
        "models": models,
        "scores": slim_scores,
        "evidence": slim_evidence,
        "untested": slim_untested,
        "group_scores": slim_groups,
        "validity": validity_index,
    }
    return payload


def render(payload: dict[str, Any]) -> str:
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    meta = payload["meta"]
    return HTML_TEMPLATE.replace("__DATA__", data).replace("__DATE__", meta["date"])


def main() -> None:
    payload = build_payload()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(render(payload), encoding="utf-8")
    meta = payload["meta"]
    size_kb = OUT_PATH.stat().st_size / 1024
    print(f"wrote {OUT_PATH.relative_to(ROOT)} ({size_kb:.0f} KB)")
    print(
        f"  models={meta['n_models']} (full panel {meta['full_panel_size']}) "
        f"abilities={meta['n_abilities_covered']}/{meta['n_abilities_total']} covered "
        f"benchmarks={meta['n_benchmarks']} evidence={meta['n_evidence']}"
    )
    if meta["uncovered_p"]:
        print(f"  no data for: {', '.join(meta['uncovered_p'])}")


HTML_TEMPLATE = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AgenticEdu Continuum · 教育 AI 原子能力评测</title>
<style>
:root{
  color-scheme: light;
  --plane:#f4f4f1; --surface:#fcfcfb; --raised:#ffffff; --sunken:#efeeea;
  --ink:#0b0b0b; --ink-2:#52514e; --muted:#898781;
  --grid:#e6e5de; --axis:#c3c2b7; --border:rgba(11,11,11,.09);
  --border-2:rgba(11,11,11,.14);
  --s1:#2a78d6; --s2:#008300; --s3:#e87ba4;
  --seq-100:#cde2fb; --seq-200:#9ec5f4; --seq-300:#6da7ec;
  --seq-400:#3987e5; --seq-500:#256abf; --seq-600:#184f95; --seq-700:#0d366b;
  --good:#0ca30c; --warning:#fab219; --warning-ink:#7a5200; --critical:#d03b3b;
  --wash:rgba(42,120,214,.07);
  --sh-1:0 1px 2px rgba(11,11,11,.04);
  --sh-2:0 1px 2px rgba(11,11,11,.05), 0 10px 28px -18px rgba(11,11,11,.30);
  --sh-3:0 2px 6px rgba(11,11,11,.07), 0 18px 44px -22px rgba(11,11,11,.34);
}
:root[data-theme="dark"]{
  color-scheme: dark;
  --plane:#0c0c0c; --surface:#171716; --raised:#1f1f1e; --sunken:#111110;
  --ink:#ffffff; --ink-2:#c3c2b7; --muted:#8d8b85;
  --grid:#2a2a28; --axis:#3d3d3a; --border:rgba(255,255,255,.10);
  --border-2:rgba(255,255,255,.16);
  --s1:#3987e5; --s2:#008300; --s3:#d55181;
  --warning-ink:#fab219;
  --wash:rgba(57,135,229,.12);
  --sh-1:0 1px 2px rgba(0,0,0,.5);
  --sh-2:0 1px 2px rgba(0,0,0,.5), 0 10px 28px -18px rgba(0,0,0,.9);
  --sh-3:0 2px 6px rgba(0,0,0,.55), 0 18px 44px -22px rgba(0,0,0,.95);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    color-scheme: dark;
    --plane:#0c0c0c; --surface:#171716; --raised:#1f1f1e; --sunken:#111110;
    --ink:#ffffff; --ink-2:#c3c2b7; --muted:#8d8b85;
    --grid:#2a2a28; --axis:#3d3d3a; --border:rgba(255,255,255,.10);
    --border-2:rgba(255,255,255,.16);
    --s1:#3987e5; --s2:#008300; --s3:#d55181;
    --warning-ink:#fab219;
    --wash:rgba(57,135,229,.12);
    --sh-1:0 1px 2px rgba(0,0,0,.5);
    --sh-2:0 1px 2px rgba(0,0,0,.5), 0 10px 28px -18px rgba(0,0,0,.9);
    --sh-3:0 2px 6px rgba(0,0,0,.55), 0 18px 44px -22px rgba(0,0,0,.95);
  }
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0; background:var(--plane); color:var(--ink);
  font-family:system-ui,-apple-system,"Segoe UI","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  font-size:14px; line-height:1.62; -webkit-font-smoothing:antialiased;
  text-rendering:optimizeLegibility;
}
a{color:inherit}
::selection{background:var(--wash)}
.link{
  color:var(--s1); cursor:pointer; text-decoration:none;
  border-bottom:1px solid transparent; transition:border-color .12s, color .12s;
}
.link:hover{border-bottom-color:currentColor}

/* ---------- header ---------- */
header{
  position:sticky; top:0; z-index:20;
  background:color-mix(in srgb, var(--surface) 86%, transparent);
  backdrop-filter:saturate(1.6) blur(14px);
  -webkit-backdrop-filter:saturate(1.6) blur(14px);
  border-bottom:1px solid var(--border);
  padding:11px 24px; display:flex; gap:18px; align-items:center; flex-wrap:wrap;
}
.brand{
  font-weight:680; letter-spacing:-.018em; white-space:nowrap; font-size:15px;
  display:flex; flex-direction:column; line-height:1.25;
}
.brand small{
  font-weight:400; font-size:10.5px; color:var(--muted);
  letter-spacing:.02em; margin-top:1px;
}
nav{
  display:flex; gap:2px; background:var(--sunken); padding:3px;
  border-radius:10px; border:1px solid var(--border);
}
nav button{
  border:0; background:transparent; color:var(--ink-2); cursor:pointer;
  padding:6px 15px; border-radius:7px; font:inherit; font-size:13px;
  transition:background .14s, color .14s;
}
nav button:hover{color:var(--ink)}
nav button[aria-current="true"]{
  background:var(--raised); color:var(--ink); font-weight:620; box-shadow:var(--sh-1);
}
.spacer{flex:1}
.search{position:relative}
.search input{
  width:250px; padding:8px 12px; border-radius:9px;
  border:1px solid var(--border); background:var(--sunken); color:var(--ink);
  font:inherit; font-size:13px; transition:border-color .14s, background .14s;
}
.search input::placeholder{color:var(--muted)}
.search input:focus{
  outline:none; border-color:var(--s1); background:var(--raised);
  box-shadow:0 0 0 3px var(--wash);
}
.results{
  position:absolute; top:calc(100% + 6px); right:0; width:340px;
  max-height:360px; overflow:auto; background:var(--raised);
  border:1px solid var(--border-2); border-radius:12px;
  box-shadow:var(--sh-3); padding:5px; display:none; z-index:30;
}
.results.open{display:block}
.results div{
  padding:8px 11px; border-radius:7px; cursor:pointer; font-size:13px;
  display:flex; justify-content:space-between; gap:10px; align-items:center;
}
.results div:hover,.results div.sel{background:var(--wash)}
.results .kind{color:var(--muted); font-size:10.5px; white-space:nowrap}
.iconbtn{
  border:1px solid var(--border); background:var(--sunken); color:var(--ink-2);
  width:36px; height:36px; border-radius:9px; cursor:pointer; font-size:15px;
  transition:background .14s, color .14s;
}
.iconbtn:hover{background:var(--raised); color:var(--ink)}

/* ---------- layout ---------- */
main{max-width:1440px; margin:0 auto; padding:28px 24px 96px}
h2{
  font-size:23px; margin:0 0 5px; letter-spacing:-.022em; font-weight:660;
}
h3{
  font-size:11px; margin:0 0 14px; color:var(--muted); font-weight:640;
  text-transform:uppercase; letter-spacing:.09em;
}
.sub{color:var(--ink-2); font-size:13px; margin:0 0 22px; max-width:80ch}
.card{
  background:var(--surface); border:1px solid var(--border);
  border-radius:14px; padding:20px 22px; margin-bottom:18px;
  box-shadow:var(--sh-1);
}

/* ---------- stat tiles ---------- */
.stats{display:flex; gap:12px; flex-wrap:wrap; margin-bottom:20px}
.stat{
  position:relative; background:var(--surface); border:1px solid var(--border);
  border-radius:13px; padding:15px 18px 14px; min-width:132px; flex:1;
  box-shadow:var(--sh-1); overflow:hidden;
}
.stat::before{
  content:""; position:absolute; inset:0 auto auto 0; width:100%; height:2px;
  background:linear-gradient(90deg,var(--s1),color-mix(in srgb,var(--s1) 25%,transparent));
}
.stat b{
  display:block; font-size:27px; font-weight:660; letter-spacing:-.03em;
  line-height:1.15; margin-bottom:2px;
}
.stat span{color:var(--muted); font-size:11.5px; letter-spacing:.01em}

/* ---------- tables ---------- */
table{border-collapse:separate; border-spacing:0; width:100%; font-size:13px}
th,td{text-align:left; padding:8px 11px; border-bottom:1px solid var(--grid)}
tbody tr:last-child td{border-bottom:0}
th{
  color:var(--muted); font-weight:620; font-size:10.5px; white-space:nowrap;
  text-transform:uppercase; letter-spacing:.07em;
  position:sticky; top:0; background:var(--surface); z-index:2;
  border-bottom:1px solid var(--border-2);
}
th.sortable{cursor:pointer; user-select:none; transition:color .14s}
th.sortable:hover{color:var(--ink)}
td.num,th.num{text-align:right; font-variant-numeric:tabular-nums}
tbody tr{transition:background .1s}
.scroll{
  overflow-x:auto; border:1px solid var(--border); border-radius:14px;
  background:var(--surface); box-shadow:var(--sh-1);
}
.scroll table th:first-child,.scroll table td:first-child{
  position:sticky; left:0; background:var(--surface); z-index:1;
  border-right:1px solid var(--grid); min-width:170px;
}
.scroll table th:first-child{z-index:3}
.scroll tbody tr:hover td{background:var(--wash)}
.scroll tbody tr:hover td:first-child{background:color-mix(in srgb,var(--wash) 100%, var(--surface))}
.rowsep td{
  background:var(--sunken)!important; color:var(--muted); font-size:11px;
  letter-spacing:.04em; padding:7px 11px; border-bottom:1px solid var(--border-2);
}
.gsep{border-right:1px solid var(--border-2)}

/* ---------- heat cells ---------- */
.heat{
  display:inline-block; min-width:42px; padding:4px 8px; border-radius:6px;
  text-align:center; font-variant-numeric:tabular-nums; font-size:12.5px;
  font-weight:560; letter-spacing:-.01em;
}
/* Sequential magnitude ramp. Light mode runs light->dark; dark mode runs the
   other way, so "more" always means "further from the surface" rather than
   darkest-on-dark, which reads as least. */
.h0{background:var(--seq-100);color:#0b0b0b} .h1{background:var(--seq-100);color:#0b0b0b}
.h2{background:var(--seq-200);color:#0b0b0b} .h3{background:var(--seq-200);color:#0b0b0b}
.h4{background:var(--seq-300);color:#0b0b0b} .h5{background:var(--seq-300);color:#0b0b0b}
.h6{background:var(--seq-400);color:#fff}    .h7{background:var(--seq-500);color:#fff}
.h8{background:var(--seq-600);color:#fff}    .h9{background:var(--seq-700);color:#fff}
:root[data-theme="dark"] .h0,:root[data-theme="dark"] .h1{background:var(--seq-700);color:#fff}
:root[data-theme="dark"] .h2,:root[data-theme="dark"] .h3{background:var(--seq-600);color:#fff}
:root[data-theme="dark"] .h4,:root[data-theme="dark"] .h5{background:var(--seq-500);color:#fff}
:root[data-theme="dark"] .h6{background:var(--seq-400);color:#fff}
:root[data-theme="dark"] .h7{background:var(--seq-300);color:#0b0b0b}
:root[data-theme="dark"] .h8{background:var(--seq-200);color:#0b0b0b}
:root[data-theme="dark"] .h9{background:var(--seq-100);color:#0b0b0b}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]) .h0,:root:not([data-theme="light"]) .h1{background:var(--seq-700);color:#fff}
  :root:not([data-theme="light"]) .h2,:root:not([data-theme="light"]) .h3{background:var(--seq-600);color:#fff}
  :root:not([data-theme="light"]) .h4,:root:not([data-theme="light"]) .h5{background:var(--seq-500);color:#fff}
  :root:not([data-theme="light"]) .h6{background:var(--seq-400);color:#fff}
  :root:not([data-theme="light"]) .h7{background:var(--seq-300);color:#0b0b0b}
  :root:not([data-theme="light"]) .h8{background:var(--seq-200);color:#0b0b0b}
  :root:not([data-theme="light"]) .h9{background:var(--seq-100);color:#0b0b0b}
}
td.cell{white-space:nowrap}
td.cell .mark{margin-left:3px}
.mark{color:var(--muted); cursor:help; font-size:11px}
/* the two benchmark-less abilities (P09/P20): present in the grid so the count
   reads as 20, but visibly inert so they never look like a zero score */
th.untestedcol{color:var(--muted); font-weight:520; cursor:help}
td.cell.untestedcol{background:var(--wash)}
td.cell.untestedcol .mark{margin-left:0; font-size:10px; letter-spacing:.02em}

/* ---------- badges ---------- */
.badge{
  display:inline-block; padding:2px 8px; border-radius:999px; font-size:10.5px;
  border:1px solid var(--border-2); color:var(--ink-2); background:var(--sunken);
  white-space:nowrap; font-weight:520; letter-spacing:.01em;
}
.badge.full{border-color:transparent; background:var(--s2); color:#fff}
.badge.warn{
  border-color:color-mix(in srgb,var(--warning) 55%,transparent);
  background:color-mix(in srgb,var(--warning) 14%,transparent);
  color:var(--warning-ink);
}
.tag{
  display:inline-block; font-size:11px; color:var(--ink-2); background:var(--sunken);
  border:1px solid var(--border); border-radius:6px; padding:3px 9px;
  white-space:nowrap; font-variant-numeric:tabular-nums;
}

/* ---------- bars ---------- */
.track{
  height:9px; border-radius:999px; background:var(--sunken);
  overflow:hidden; min-width:90px; box-shadow:inset 0 0 0 1px var(--border);
}
.bar{height:100%; border-radius:0 4px 4px 0; background:var(--s1)}
.bar.hollow{
  background:transparent; border:1.5px solid var(--s1);
  border-left:0; border-radius:0 4px 4px 0;
}

/* ---------- chips ---------- */
.chips{display:flex; gap:8px; flex-wrap:wrap; margin-bottom:18px}
.chip{
  border:1px solid var(--border-2); background:var(--surface); color:var(--ink-2);
  padding:6px 13px; border-radius:999px; cursor:pointer; font:inherit; font-size:12.5px;
  display:inline-flex; align-items:center; gap:7px;
  transition:border-color .14s, background .14s, color .14s;
}
.chip:hover{border-color:var(--axis); background:var(--raised)}
.chip[aria-pressed="true"]{
  background:var(--ink); color:var(--surface); border-color:var(--ink); font-weight:560;
}
.chip .dot{width:8px; height:8px; border-radius:50%; flex:none}
.chip.partial{border-style:dashed}
.chip .cnt{color:var(--muted); font-size:10.5px; font-variant-numeric:tabular-nums}
.chip[aria-pressed="true"] .cnt{color:color-mix(in srgb,var(--surface) 70%,transparent)}

/* ---------- two-column ---------- */
.grid2{display:grid; grid-template-columns:minmax(360px,.95fr) minmax(380px,1.2fr); gap:18px; align-items:start}
@media (max-width:1040px){.grid2{grid-template-columns:1fr}}
.radarwrap{display:flex; flex-direction:column; align-items:center}
.radarwrap svg{width:100%; max-width:620px; height:auto; display:block}
svg{max-width:100%; height:auto; display:block}
.legend{
  display:flex; gap:20px; flex-wrap:wrap; justify-content:center;
  margin-top:14px; font-size:12.5px; padding-top:14px;
  border-top:1px solid var(--grid); width:100%;
}
.legend i{display:inline-block; width:11px; height:11px; border-radius:3px; margin-right:7px; vertical-align:-1px}
.legend .cov{color:var(--muted); font-size:11px; margin-left:6px}

/* ---------- disclosure ---------- */
details{border-top:1px solid var(--grid); padding:10px 0}
details summary{
  cursor:pointer; color:var(--ink-2); font-size:12.5px; list-style:none;
  display:flex; gap:8px; align-items:center; transition:color .14s;
}
details summary:hover{color:var(--ink)}
details summary::-webkit-details-marker{display:none}
details summary::before{content:"▸"; color:var(--muted); transition:transform .16s}
details[open] summary::before{transform:rotate(90deg)}
details .body{padding:10px 0 4px; color:var(--ink-2); font-size:12.5px}
.stale{
  border-left:2px solid var(--warning); padding-left:14px; margin-top:8px;
  color:var(--ink-2); font-size:12.5px;
}
.notice{
  border:1px solid color-mix(in srgb, var(--warning) 45%, transparent);
  background:color-mix(in srgb, var(--warning) 8%, transparent);
  border-radius:11px; padding:12px 16px; margin-bottom:16px;
  font-size:12.5px; color:var(--ink-2); line-height:1.6;
}

/* ---------- ability rows (model view) ---------- */
.prow{
  display:flex; align-items:center; gap:14px; padding:11px 12px;
  border-radius:9px; cursor:pointer; border-bottom:1px solid var(--grid);
  position:relative; transition:background .12s;
}
.prow::before{
  content:""; position:absolute; left:0; top:6px; bottom:6px; width:2px;
  border-radius:2px; background:var(--s1); opacity:0; transition:opacity .14s;
}
.prow:hover{background:var(--wash)}
.prow:hover::before{opacity:1}
.prow .name{flex:1; min-width:0}
.prow .name b{font-weight:620; font-size:13px}
.prow .name span{
  display:block; color:var(--muted); font-size:11.5px;
  overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
}
.prow .val{
  font-variant-numeric:tabular-nums; font-weight:640; width:46px;
  text-align:right; letter-spacing:-.02em; font-size:14px;
}
.drill{
  background:var(--sunken); border:1px solid var(--border);
  border-radius:11px; padding:14px 16px; margin:4px 0 12px;
}
.drill .defn{color:var(--ink-2); font-size:12.5px; margin-bottom:12px}
.drill table{font-size:12px}
.drill th,.drill td{padding:7px 9px}
.facetgrp{margin-bottom:14px}
.facetgrp:last-child{margin-bottom:0}
.facetgrp h4{
  margin:0 0 5px; font-size:12.5px; font-weight:640;
  display:flex; align-items:center; gap:8px; flex-wrap:wrap;
}
.facetgrp p{margin:0 0 8px; color:var(--muted); font-size:11.5px}

/* ---------- 能力不具备记 0 分 / 未测过 ---------- */
tr.capzero td{color:var(--muted)}
tr.capzero{
  background:repeating-linear-gradient(135deg,transparent,transparent 6px,var(--grid) 6px,var(--grid) 7px);
}
tr.untestedrow td{color:var(--muted); opacity:.85}
.untested{color:var(--warning-ink); font-weight:620}

/* ---------- profile card ---------- */
.kv{display:flex; gap:8px; flex-wrap:wrap; margin:12px 0 16px}
.secs{columns:2 310px; column-gap:30px}
.secs section{break-inside:avoid; margin-bottom:16px}
.secs h4{
  margin:0 0 6px; font-size:10.5px; font-weight:640; color:var(--muted);
  text-transform:uppercase; letter-spacing:.08em;
}
.secs ul{margin:0; padding-left:18px; color:var(--ink-2); font-size:12.5px}
.secs li{margin-bottom:4px}
.oneline{font-size:15px; line-height:1.55; margin:0 0 12px; letter-spacing:-.01em}

/* ---------- misc ---------- */
.toolbar{display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin-bottom:16px}
select{
  padding:7px 11px; border-radius:9px; border:1px solid var(--border-2);
  background:var(--surface); color:var(--ink); font:inherit; font-size:13px;
  cursor:pointer; transition:border-color .14s;
}
select:hover{border-color:var(--axis)}
select:focus{outline:none; border-color:var(--s1); box-shadow:0 0 0 3px var(--wash)}
.empty{color:var(--muted); padding:28px; text-align:center; font-size:13px}
.foot{color:var(--muted); font-size:11.5px; margin-top:12px; line-height:1.6}
</style>
</head>
<body>
<header>
  <div class="brand">AgenticEdu Continuum<small>教育 AI 原子能力评测 · v6 · R25 · __DATE__</small></div>
  <nav id="nav">
    <button data-view="overview">总览</button>
    <button data-view="model">模型</button>
    <button data-view="ability">原子能力</button>
    <button data-view="bench">Benchmark</button>
  </nav>
  <div class="spacer"></div>
  <div class="search">
    <input id="q" type="search" placeholder="搜模型 / 能力 / benchmark" autocomplete="off">
    <div class="results" id="qr"></div>
  </div>
  <button class="iconbtn" id="theme" title="切换深浅色">◐</button>
</header>
<main id="app"></main>
<script id="payload" type="application/json">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById('payload').textContent);
const app = document.getElementById('app');

/* ---------- indexes ---------- */
const abilityBy = {}; D.abilities.forEach(a => abilityBy[a.p_code] = a);
const benchBy = {}; D.benchmarks.forEach(b => benchBy[b.id] = b);
const modelBy = {}; D.models.forEach(m => modelBy[m.key] = m);
const groupLabel = {}; D.groups.forEach(g => groupLabel[g.id] = g.label);
const coveredP = D.abilities.map(a => a.p_code).filter(p => !D.meta.uncovered_p.includes(p));
// The full universe of atomic abilities (20). coveredP is the measurable subset;
// allP always spans every P so column/axis counts read as the true total, with
// the two benchmark-less abilities (P09/P20) shown as 未测 rather than dropped.
const allP = D.abilities.map(a => a.p_code);
const isUncovered = p => D.meta.uncovered_p.includes(p);

/* --- R26 缺测口径，页面内复算 ------------------------------------------
   R22 的「缺格取该格已测模型最低分顶替」已废除（用户裁决 2026-08-04）。
   缺格现在由聚合脚本分成两类，页面只如实呈现，不再自己造替代行：
     · 能力不具备（evidence 行 zero=true，分数 0）：整套题都得有某项能力
       （目前只有视觉）才能作答，模型没有——真实能力差距，计分，并按常规
       权重规则传导到这一格挂载的每一个 P。
     · 未测过（在 D.untested 里，不进 evidence）：没跑过，不计分也不进分母。
   下面只把 evidence 行按 facet 加权聚合，结果与 09_atomic_p_scores.jsonl
   逐行一致（见 console 自检输出）。                                      */
const MEASURED = D.evidence.filter(r => !r.zero);
const untestedBy = {};
D.untested.forEach(r => (untestedBy[r.m + '|' + r.p] ||= []).push(r));

function buildScores(){
  const rows = D.evidence.slice();
  const acc = {};
  rows.forEach(r => {
    const s = (acc[r.m + '|' + r.p] ||= {facets: {}, n: 0, zero: 0, zerow: 0, w: 0, b: new Set()});
    const f = (s.facets[r.f] ||= {ws: 0, w: 0});
    f.ws += r.s * r.eff; f.w += r.eff;
    s.n++; s.w += r.eff; s.b.add(r.b);
    if (r.zero){ s.zero++; s.zerow += r.eff; }
  });
  const scores = {};
  Object.keys(acc).forEach(k => {
    const s = acc[k], parts = k.split('|');
    const facets = {}, means = [];
    Object.keys(s.facets).forEach(id => {
      const f = s.facets[id];
      if (f.w){ facets[id] = f.ws / f.w; means.push(f.ws / f.w); }
    });
    if (!means.length) return;
    scores[k] = {
      m: parts[0], p: parts[1], s: means.reduce((a, b) => a + b, 0) / means.length,
      facets: facets, n: s.n, zero: s.zero, zerow: s.w ? s.zerow / s.w : 0,
      unt: (untestedBy[k] || []).length,
      nf: means.length, b: [...s.b].sort()
    };
  });
  const groups = {};
  Object.keys(scores).forEach(k => {
    const r = scores[k], g = abilityBy[r.p].group;
    const slot = (groups[r.m + '|' + g] ||= {sum: 0, n: 0});
    slot.sum += r.s; slot.n++;
  });
  Object.keys(groups).forEach(k => groups[k] = {s: groups[k].sum / groups[k].n, np: groups[k].n});
  return {scores: scores, groups: groups, evidence: rows};
}

let scoreOf, groupScoreOf, evByModelP, evByBench;
function applyMode(){
  const built = buildScores();
  scoreOf = built.scores;
  groupScoreOf = built.groups;
  evByModelP = {}; evByBench = {};
  built.evidence.forEach(r => {
    (evByModelP[r.m + '|' + r.p] ||= []).push(r);
    (evByBench[r.b] ||= []).push(r);
  });
}
applyMode();

// Self-check: the rebuild must reproduce the committed artifact exactly.
(() => {
  let worst = 0, n = 0;
  D.scores.forEach(r => {
    const mine = scoreOf[r.m + '|' + r.p];
    if (mine){ worst = Math.max(worst, Math.abs(mine.s - r.s)); n++; }
  });
  // 已发布的 score_10 本身是 4 位小数，所以 5e-5 是这个比对的理论下限，
  // 阈值只能卡在它之上；真正的逻辑错误会差好几个数量级。
  const msg = `R26 复算自检：${n}/${D.scores.length} 行比对，最大偏差 ${worst.toExponential(1)}`;
  (worst < 2e-4 && n === D.scores.length ? console.log : console.error)(msg);
})();
const benchToCells = {};     // benchmark -> [{p_code,facet,subdimension,weight}]
D.abilities.forEach(a => a.facets.forEach(f => f.cells.forEach(c => {
  (benchToCells[c.benchmark_id] ||= []).push({
    p_code: a.p_code, p_name: a.p_name, facet_id: f.facet_id,
    facet_name: f.facet_name, subdimension: c.subdimension, weight: c.weight
  });
})));

const fullPanel = D.models.filter(m => m.full_panel).map(m => m.key);
const SERIES = ['--s1', '--s2', '--s3'];

/* ---------- helpers ---------- */
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fx = (v, n = 2) => (v === null || v === undefined || Number.isNaN(v)) ? '—' : Number(v).toFixed(n);
const mName = k => (modelBy[k] || {}).display || k;

// Sequential 0-10 -> ramp class; the steps themselves live in CSS so the
// dark-mode ramp can run the opposite direction without a re-render.
function heatClass(v){
  if (v === null || v === undefined) return '';
  return 'h' + Math.max(0, Math.min(9, Math.floor(v)));
}
function markers(row){
  if (!row) return '';
  let out = '';
  if (row.nf < (abilityBy[row.p]?.facets.length || 0)) out += '<span class="mark" title="并非所有 facet 都有证据">◐</span>';
  if (row.zero > 0) out += `<span class="mark" title="含 ${row.zero} 个「能力不具备记 0 分」的格（占有效权重 ${(row.zerow*100).toFixed(0)}%）">✕</span>`;
  if (row.unt > 0) out += `<span class="mark" title="另有 ${row.unt} 个格未测过，未计入分母">·</span>`;
  return out;
}
function go(hash){ location.hash = hash; }
function pLink(p){ return `<span class="link" onclick="go('#/p/${p}')">${p} ${esc(abilityBy[p]?.p_name || '')}</span>`; }
function bLink(b){ return `<span class="link" onclick="go('#/bench/${encodeURIComponent(b)}')">${esc(benchBy[b]?.name || b)}</span>`; }
function mLink(m){ return `<span class="link" onclick="go('#/model/${encodeURIComponent(m)}')">${esc(mName(m))}</span>`; }
// 实测覆盖：只数真跑过的格，「能力不具备记 0 分」的格不算跑过。
const measuredP = {};
MEASURED.forEach(r => (measuredP[r.m] ||= new Set()).add(r.p));

function covBadge(m){
  const mm = modelBy[m];
  const real = (measuredP[m] || new Set()).size;
  const now = coveredP.filter(p => scoreOf[m + '|' + p]).length;
  if (now > real){
    // 只由「能力不具备记 0 分」撑起来的 P，别当成跑过。
    return `<span class="badge warn" title="实测 ${real} 项，另有 ${now - real} 项只有「能力不具备记 0 分」的格">实测 ${real}/${coveredP.length}，另 ${now - real} 项仅 0 分格</span>`;
  }
  return real >= coveredP.length
    ? `<span class="badge full">全覆盖 ${real}/${coveredP.length}</span>`
    : `<span class="badge warn">${real}/${coveredP.length} 项有证据</span>`;
}

/* ---------- charts ---------- */
function radar(series){
  const R = 168, cx = 250, cy = 210, N = allP.length;
  const ang = i => (i / N) * 2 * Math.PI - Math.PI / 2;
  const pt = (i, r) => [cx + Math.cos(ang(i)) * r, cy + Math.sin(ang(i)) * r];
  let g = '';
  for (const lvl of [2, 4, 6, 8, 10]){
    const pts = allP.map((_, i) => pt(i, R * lvl / 10).map(n => n.toFixed(1)).join(',')).join(' ');
    g += `<polygon points="${pts}" fill="none" stroke="var(--grid)" stroke-width="1"/>`;
  }
  g += `<text x="${cx+4}" y="${cy-R+2}" font-size="9" fill="var(--muted)">10</text>`;
  allP.forEach((p, i) => {
    const off = isUncovered(p);
    const [x, y] = pt(i, R);
    g += `<line x1="${cx}" y1="${cy}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}" stroke="var(--grid)" stroke-width="1"/>`;
    const [lx, ly] = pt(i, R + 26);
    const anchor = Math.abs(lx - cx) < 12 ? 'middle' : (lx > cx ? 'start' : 'end');
    g += `<text x="${lx.toFixed(1)}" y="${(ly + 3).toFixed(1)}" text-anchor="${anchor}" font-size="10.5" fill="${off ? 'var(--muted)' : 'var(--ink-2)'}"
            style="cursor:pointer${off ? ';opacity:.65' : ''}" onclick="go('#/p/${p}')"><title>${esc(abilityBy[p].p_name)}${off ? '（暂无 benchmark，未测）' : ''}</title>${p}</text>`;
  });
  series.forEach((s, si) => {
    const col = `var(${SERIES[si % SERIES.length]})`;
    // Missing axes break the ring: draw only contiguous measured runs, never
    // interpolate a model's uncovered ability as if it scored there.
    const vals = allP.map(p => { const r = scoreOf[s.key + '|' + p]; return r ? r.s : null; });
    let run = [];
    const flush = () => {
      if (run.length > 1){
        g += `<polyline points="${run.map(a => a.join(',')).join(' ')}" fill="none"
                stroke="${col}" stroke-width="2" stroke-linejoin="round" opacity=".92"/>`;
      }
      run = [];
    };
    if (vals.every(v => v !== null)){
      const pts = vals.map((v, i) => pt(i, R * v / 10).map(n => n.toFixed(1)));
      // Fill only a lone series - stacked translucent fills mix into a muddy
      // third hue and stop reading as either model.
      const fill = series.length === 1 ? `fill="${col}" fill-opacity=".13"` : 'fill="none"';
      g += `<polygon points="${pts.map(a => a.join(',')).join(' ')}" ${fill}
              stroke="${col}" stroke-width="2" stroke-linejoin="round"/>`;
    } else {
      vals.forEach((v, i) => { if (v === null) flush(); else run.push(pt(i, R * v / 10).map(n => n.toFixed(1))); });
      flush();
    }
    vals.forEach((v, i) => {
      if (v === null) return;
      const [x, y] = pt(i, R * v / 10);
      // 分数过半来自「能力不具备记 0 分」的点画空心：那是能力缺口砸出来的低分，
      // 不是在这套题上量出来的水平，一眼扫过去不该跟实测点长得一样。
      const row = scoreOf[s.key + '|' + allP[i]];
      const mostlyZero = row && row.zerow >= 0.5;
      const note = mostlyZero ? `（其中 ${(row.zerow * 100).toFixed(0)}% 的有效权重来自「能力不具备记 0 分」的格）` : '';
      g += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="4"
              fill="${mostlyZero ? 'var(--surface)' : col}" stroke="${col}" stroke-width="2"
              ><title>${esc(mName(s.key))} · ${allP[i]} ${esc(abilityBy[allP[i]].p_name)}: ${fx(v)}${note}</title></circle>`;
    });
  });
  return `<svg viewBox="0 0 500 440" role="img" aria-label="原子能力雷达图">${g}</svg>`;
}

function bars(rows, maxV = 10){
  return rows.map(r => `
    <tr>
      <td>${mLink(r.key)}
        ${r.facetCov && r.facetCov.have < r.facetCov.total
          ? `<span class="badge warn" title="这项能力有 ${r.facetCov.total} 个 facet，该模型只测了 ${r.facetCov.have} 个，分数不可与全测模型直接比">仅测 ${r.facetCov.have}/${r.facetCov.total} facet</span>`
          : ''}
        ${r.zeroShare > 0
          ? `<span class="badge warn" title="这一分数里有 ${(r.zeroShare*100).toFixed(0)}% 的有效权重来自「能力不具备记 0 分」的格">能力缺口 ${(r.zeroShare*100).toFixed(0)}%</span>`
          : ''}
        ${r.full ? '' : '<span class="badge">全库 ' + modelBy[r.key].p_count + '/' + coveredP.length + '</span>'}</td>
      <td style="width:52%"><div class="track" title="${esc(r.tip || '')}">
        <div class="bar${r.full ? '' : ' hollow'}" style="width:${(r.value / maxV * 100).toFixed(1)}%"></div></div></td>
      <td class="num">${fx(r.value)}${r.mark || ''}</td>
    </tr>`).join('');
}

/* ---------- view: overview ---------- */
let ovSort = {key: '_avg', dir: -1};
function viewOverview(){
  const rowsFor = list => list.map(m => {
    const cells = allP.map(p => {
      if (isUncovered(p))
        return `<td class="num cell untestedcol"><span class="mark" title="${esc(abilityBy[p].p_name)}：暂无 benchmark，全部模型均未测">未测</span></td>`;
      const r = scoreOf[m.key + '|' + p];
      return r
        ? `<td class="num cell"><span class="heat ${heatClass(r.s)}"
             title="${esc(m.display)} · ${p} ${esc(abilityBy[p].p_name)}: ${fx(r.s)}（${r.n} 条证据）">${fx(r.s, 1)}</span>${markers(r)}</td>`
        : `<td class="num cell"><span class="untested" title="该模型这项能力的取分格一个都没跑过；不给分，也不折算成 0">未测过</span></td>`;
    }).join('');
    const gcells = D.groups.map(g => {
      const r = groupScoreOf[m.key + '|' + g.id];
      const last = g.id === D.groups[D.groups.length - 1].id;
      return `<td class="num${last ? ' gsep' : ''}">${r ? fx(r.s, 1) : '<span class="mark">·</span>'}</td>`;
    }).join('');
    return `<tr><td>${mLink(m.key)}<br>${covBadge(m.key)}</td>${gcells}${cells}</tr>`;
  }).join('');

  const sorted = list => {
    const k = ovSort.key;
    return [...list].sort((a, b) => {
      const va = k === '_avg' ? a.p_count : (scoreOf[a.key + '|' + k]?.s ?? -1);
      const vb = k === '_avg' ? b.p_count : (scoreOf[b.key + '|' + k]?.s ?? -1);
      return ovSort.dir === -1 ? vb - va : va - vb;
    });
  };
  const full = sorted(D.models.filter(m => m.full_panel));
  const partial = sorted(D.models.filter(m => !m.full_panel));

  app.innerHTML = `
    <h2>总览</h2>
    <p class="sub">模型 × 原子能力得分矩阵（0–10）。列头可排序；点任意模型名或能力编号进入详情。
      <span class="mark">◐</span> 该能力并非所有 facet 都有证据，<span class="mark">✕</span> 含「能力不具备记 0 分」的格，<span class="mark">·</span> 另有格子未测过。<b>未测过</b>的能力不给分，也不折算成 0。</p>
    <div class="stats">
      <div class="stat"><b>${D.meta.n_models}</b><span>已测模型</span></div>
      <div class="stat"><b>${D.meta.full_panel_size}</b><span>全覆盖模型</span></div>
      <div class="stat"><b>${D.meta.n_abilities_covered}/${D.meta.n_abilities_total}</b><span>有数据的原子能力</span></div>
      <div class="stat"><b>${D.meta.n_benchmarks}</b><span>benchmark 取分维度来源</span></div>
      <div class="stat"><b>${D.meta.n_evidence}</b><span>条证据行</span></div>
    </div>
    <div class="scroll">
      <table>
        <thead><tr>
          <th class="sortable" data-k="_avg">模型</th>
          ${D.groups.map((g, i) => `<th class="num${i === D.groups.length - 1 ? ' gsep' : ''}" title="${esc(g.label)}">${g.id}</th>`).join('')}
          ${allP.map(p => `<th class="num${isUncovered(p) ? ' untestedcol' : ' sortable'}" ${isUncovered(p) ? '' : `data-k="${p}"`} title="${esc(abilityBy[p].p_name)}${isUncovered(p) ? '（暂无 benchmark，未测）' : ''}">${p}</th>`).join('')}
        </tr></thead>
        <tbody>
          <tr class="rowsep"><td colspan="${1 + D.groups.length + allP.length}">
            发布面板 · ${D.panel.length} 个模型 · 共 ${allP.length} 项原子能力，其中 ${coveredP.length} 项有分；${D.meta.uncovered_p.join('、')} 暂无 benchmark 记为「未测」。R26 起缺格不再拿别的模型顶替：能力不具备的格记 0 分照常计分，纯未测的格不计分也不进分母（全库 ${D.meta.n_zero_cells} 个 0 分格、${D.meta.n_untested_cells} 个未测格）</td></tr>
          ${rowsFor(full)}
          <tr class="rowsep"><td colspan="${1 + D.groups.length + allP.length}">
            部分覆盖 · 覆盖面差异很大，跨行比较前务必看徽章上的覆盖率</td></tr>
          ${rowsFor(partial)}
        </tbody>
      </table>
    </div>
    <p class="foot">大类：${D.groups.map(g => `${g.id} ${esc(g.label)}`).join(' · ')}。
      ${D.meta.uncovered_p.length ? D.meta.uncovered_p.join('、') + ' 目前全库无数据，未列入矩阵。' : ''}</p>`;

  app.querySelectorAll('th.sortable').forEach(th => th.onclick = () => {
    const k = th.dataset.k;
    ovSort = {key: k, dir: ovSort.key === k ? -ovSort.dir : -1};
    viewOverview();
  });
}

/* ---------- view: model ---------- */
let picked = [];
let openP = null;
function viewModel(){
  if (!picked.length) picked = fullPanel.slice(0, 2);
  const chips = D.models.map(m => {
    const i = picked.indexOf(m.key);
    const dot = i >= 0 ? `<span class="dot" style="background:var(${SERIES[i]})"></span>` : '';
    // 数实测能力，不数有分能力——只靠「能力不具备记 0 分」撑起来的 P
    // 不该把这个数字撑大。
    const real = (measuredP[m.key] || new Set()).size;
    return `<button class="chip${real >= coveredP.length ? '' : ' partial'}" aria-pressed="${i >= 0}" data-m="${esc(m.key)}"
      title="实测 ${real}/${coveredP.length} 项原子能力">
      ${dot}${esc(m.display)} <span class="cnt">${real}/${coveredP.length}</span></button>`;
  }).join('');

  const series = picked.map(k => ({key: k}));
  const legend = picked.map((k, i) => {
    const real = (measuredP[k] || new Set()).size;
    const now = coveredP.filter(p => scoreOf[k + '|' + p]).length;
    const cov = now > real
      ? `实测 ${real}/${coveredP.length}，另 ${now - real} 项只有「能力不具备记 0 分」的格（空心点＝该项过半权重来自 0 分格）`
      : `${real}/${coveredP.length} 项有证据${real >= coveredP.length ? '' : '（未测过之处断线）'}`;
    return `<span><i style="background:var(${SERIES[i]})"></i>${esc(mName(k))}
      <span class="cov">${cov}</span></span>`;
  }).join('');

  const primary = picked[0];
  const list = allP.map(p => {
    const a = abilityBy[p];
    if (isUncovered(p)) return `<div class="prow" style="opacity:.5" onclick="go('#/p/${p}')">
      <div class="name"><b>${p} ${esc(a.p_name)}</b><span>${esc(a.definition)}</span></div>
      <div class="val"><span class="untested">未测</span></div></div>`;
    const r = scoreOf[primary + '|' + p];
    if (!r) return `<div class="prow" style="opacity:.45" onclick="go('#/p/${p}')">
      <div class="name"><b>${p} ${esc(a.p_name)}</b><span>${esc(a.definition)}</span></div>
      <div class="val">—</div></div>`;
    return `<div class="prow" data-p="${p}">
        <div class="name"><b>${p} ${esc(a.p_name)}</b><span>${esc(a.definition)}</span></div>
        <div class="track" style="width:110px;flex:none"><div class="bar" style="width:${(r.s * 10).toFixed(1)}%"></div></div>
        <div class="val">${fx(r.s)}</div><div style="width:26px">${markers(r)}</div>
      </div>${openP === p ? drill(primary, p) : ''}`;
  }).join('');

  app.innerHTML = `
    <h2>模型视图</h2>
    <p class="sub">雷达图共 ${allP.length} 个轴（全部原子能力）；${D.meta.uncovered_p.join('、')} 暂无 benchmark，任何模型都无数据，对应轴留空断线，不画成 0。最多叠加 3 个模型，部分覆盖的模型缺口处同样断线。点右侧任一能力展开它的证据构成。</p>
    <div class="chips" id="chips">${chips}</div>
    <div class="grid2">
      <div class="card radarwrap">
        <div class="radarwrap">${radar(series)}</div>
        <div class="legend">${legend}</div>
      </div>
      <div class="card">
        <h3>${esc(mName(primary))} 的能力得分 ${covBadge(primary)}</h3>
        <div>${list}</div>
        <p class="foot">数值为 0–10 归一分。表格视图见「总览」，同一批数据。</p>
      </div>
    </div>`;

  app.querySelectorAll('#chips .chip').forEach(c => c.onclick = () => {
    const k = c.dataset.m, i = picked.indexOf(k);
    if (i >= 0){ if (picked.length > 1) picked.splice(i, 1); }
    else { if (picked.length >= 3) picked.shift(); picked.push(k); }
    openP = null; viewModel();
  });
  app.querySelectorAll('.prow[data-p]').forEach(r => r.onclick = () => {
    openP = openP === r.dataset.p ? null : r.dataset.p; viewModel();
  });
}

function drill(model, p){
  const a = abilityBy[p];
  const rows = evByModelP[model + '|' + p] || [];
  const byFacet = {};
  rows.forEach(r => (byFacet[r.f] ||= []).push(r));
  const untRows = untestedBy[model + '|' + p] || [];
  const untByFacet = {};
  untRows.forEach(r => (untByFacet[r.f] ||= []).push(r));
  const sc = scoreOf[model + '|' + p];
  // 未测过的格不进分数，但一定要在同一张表里列出来——否则读者看到的
  // facet 分会显得比它实际的证据面更扎实。
  const untRowHtml = rs => rs.map(r => `<tr class="untestedrow">
            <td>${bLink(r.b)} · ${esc(r.sd)}
              <br><b class="untested">未测过</b>
              <span style="color:var(--muted);font-size:11.5px">——${esc(r.why || '该模型没跑过这一格')}；不计分，也不进分母</span></td>
            <td class="num">${fx(r.rel)}</td><td class="num">${fx(r.conf)}</td><td class="num">${fx(r.eff)}</td>
            <td class="num untested">未测过</td><td class="num untested">未测过</td>
          </tr>`).join('');
  const groups = a.facets.map(f => {
    const rs = byFacet[f.facet_id] || [];
    const us = untByFacet[f.facet_id] || [];
    if (!rs.length) return `<div class="facetgrp">
      <h4>${esc(f.facet_name)} <span class="badge">${us.length ? '全部未测过' : '无证据'}</span></h4>
      <p>${esc(f.facet_description)}</p>
      ${us.length ? `<table><thead><tr>
        <th>benchmark · 取分维度</th><th class="num">相关</th><th class="num">置信</th>
        <th class="num">有效</th><th class="num">原始值</th><th class="num">0–10 分</th>
      </tr></thead><tbody>${untRowHtml(us)}</tbody></table>` : ''}</div>`;
    return `<div class="facetgrp">
      <h4>${esc(f.facet_name)} <span class="badge">facet 分 ${fx(sc.facets[f.facet_id])}</span></h4>
      <p>${esc(f.facet_description)}</p>
      <table><thead><tr>
        <th>benchmark · 取分维度</th><th class="num">相关</th><th class="num">置信</th>
        <th class="num">有效</th><th class="num">原始值</th><th class="num">0–10 分</th>
      </tr></thead><tbody>
      ${rs.map(r => r.zero
        ? `<tr class="capzero">
            <td>${bLink(r.b)} · ${esc(r.sd)}
              <br><b class="untested">能力不具备，记 0 分</b>
              <span style="color:var(--muted);font-size:11.5px">——${esc(r.why || '')}。这是真实的能力差距，照常计分</span></td>
            <td class="num">${fx(r.rel)}</td><td class="num">${fx(r.conf)}</td><td class="num">${fx(r.eff)}</td>
            <td class="num untested">跑不了</td>
            <td class="num"><b>0.00</b><span class="mark" title="能力不具备记 0 分">✕</span></td>
          </tr>`
        : `<tr>
            <td>${bLink(r.b)} · ${esc(r.sd)}
              <br><span style="color:var(--muted);font-size:11.5px">${esc(benchBy[r.b]?.profile.one_liner || '')}</span></td>
            <td class="num">${fx(r.rel)}</td><td class="num">${fx(r.conf)}</td><td class="num">${fx(r.eff)}</td>
            <td class="num">${fx(r.raw, 3)}</td><td class="num"><b>${fx(r.s)}</b></td>
          </tr>`).join('')}
      ${untRowHtml(us)}
      </tbody></table></div>`;
  }).join('');
  const nZero = rows.filter(r => r.zero).length;
  return `<div class="drill">
    <div class="defn"><b>${p} ${esc(a.p_name)}</b>——${esc(a.definition)}
      ${a.single_source ? '<span class="badge warn">单源测量</span>' : ''}</div>
    ${nZero ? `<div class="notice" style="margin-bottom:12px">
      这项分数里有 <b>${nZero} 个格记 0 分</b>，占有效权重 <b>${(sc.zerow * 100).toFixed(0)}%</b>——
      ${esc(mName(model))} 缺这些格必需的能力（当前只有视觉一项），<b>整套题都作答不了</b>。
      这是真实的能力差距而非排期缺口，所以照常计分，并按常规权重规则传导到它挂载的每一个能力。</div>` : ''}
    ${untRows.length ? `<div class="notice" style="margin-bottom:12px">
      另有 <b>${untRows.length} 个格未测过</b>（下表中标黄的行）：${esc(mName(model))} 没跑过，
      <b>不计分也不进分母</b>——不拿别人的分数顶替，也不折算成 0。</div>` : ''}
    ${groups}
    <p class="foot">有效权重 = 相关度 × 置信度；facet 内按有效权重加权平均，P 分为各 facet 的等权平均。
      <span class="link" onclick="go('#/p/${p}')">查看这项能力的完整说明与全模型排名 →</span></p>
  </div>`;
}

/* ---------- view: ability ---------- */
let curP = null;
function viewAbility(){
  if (!curP || !abilityBy[curP]) curP = coveredP[0];
  const a = abilityBy[curP];
  const opts = D.abilities.map(x => `<option value="${x.p_code}" ${x.p_code === curP ? 'selected' : ''}>
    ${x.p_code} ${esc(x.p_name)}${D.meta.uncovered_p.includes(x.p_code) ? '（无数据）' : ''}</option>`).join('');

  // 边界口径 titles look like "P03 / P04" or "P05 与 P06/P17" - match the P code as a token.
  const bounds = D.boundaries.filter(b => new RegExp(curP + '\\b').test(b.title));

  const facetBlocks = a.facets.map(f => `
    <div class="facetgrp">
      <h4>${esc(f.facet_name)}${f.coverage_gap ? ' <span class="badge warn">覆盖缺口</span>' : ''}</h4>
      <p>${esc(f.facet_description)}</p>
      ${f.cells.length ? `<table><thead><tr>
          <th>benchmark · 取分维度</th><th class="num">相关</th><th class="num">置信</th><th class="num">有效</th>
          <th class="num">区分度 n / sd</th></tr></thead><tbody>
        ${f.cells.map(c => {
          const v = D.validity[c.benchmark_id + '||' + c.subdimension] || {};
          const conf = benchBy[c.benchmark_id]?.confidence;
          const flags = (v.flags || []).length ? `<span class="badge warn" title="${esc((v.flags||[]).join('、'))}">${esc((v.flags||[])[0])}</span>` : '';
          return `<tr>
            <td>${bLink(c.benchmark_id)} · ${esc(c.subdimension)}</td>
            <td class="num">${fx(c.weight)}</td><td class="num">${fx(conf)}</td>
            <td class="num">${conf ? fx(c.weight * conf) : '—'}</td>
            <td class="num">${v.n_models ?? '—'} / ${fx(v.sd)} ${flags}</td>
          </tr>`;
        }).join('')}
        </tbody></table>` : '<p class="empty">这个 facet 目前没有挂载任何 benchmark。</p>'}
      ${f.revision_rationale ? `<details><summary>裁决原文（P 编号为旧制，R20 前）</summary>
        <div class="body stale">${esc(f.revision_rationale)}</div></details>` : ''}
      ${f.cells.filter(c => c.revision_rationale).map(c => `<details>
        <summary>${esc(benchBy[c.benchmark_id]?.name || c.benchmark_id)} · ${esc(c.subdimension)} 的定权理由（P 编号为旧制）</summary>
        <div class="body stale">${esc(c.revision_rationale)}</div></details>`).join('')}
    </div>`).join('');

  const ranked = D.models
    .map(m => ({key: m.key, full: m.full_panel, row: scoreOf[m.key + '|' + curP]}))
    .filter(x => x.row)
    .sort((x, y) => y.row.s - x.row.s)
    .map(x => ({
      key: x.key, full: x.full, value: x.row.s, mark: markers(x.row),
      // Facet coverage *within this P* is the honest caveat on a ranking: a model
      // scored on one easy facet can outrank one measured on all three.
      facetCov: {have: x.row.nf, total: a.facets.length},
      zeroShare: x.row.zerow,
      tip: Object.entries(x.row.facets).map(([k, v]) => `${a.facets.find(f => f.facet_id === k)?.facet_name || k}: ${fx(v)}`).join(' · ')
    }));

  app.innerHTML = `
    <h2>原子能力视图</h2>
    <p class="sub">这项能力是什么、怎么测的、谁做得好。</p>
    <div class="toolbar"><select id="psel">${opts}</select>
      <span class="badge">${a.group} ${esc(groupLabel[a.group] || '')}</span>
      <span class="badge">${esc(a.model_type)}</span>
      ${a.single_source ? '<span class="badge warn">单源直接测量</span>' : ''}
      ${D.meta.uncovered_p.includes(curP) ? '<span class="badge warn">暂无任何模型数据</span>' : ''}
    </div>
    <div class="card">
      <h3>它是什么</h3>
      <p style="margin:0 0 12px"><b>${curP} ${esc(a.p_name)}</b>——${esc(a.definition)}</p>
      ${bounds.length ? `<h3 style="margin-top:14px">与相邻能力的边界</h3>
        <ul style="margin:0;padding-left:18px;color:var(--ink-2);font-size:12.5px">
        ${bounds.map(b => `<li><b>${esc(b.title)}</b>：${esc(b.text)}</li>`).join('')}</ul>` : ''}
      ${a.rationale ? `<details><summary>能力级裁决原文（P 编号为旧制，R20 前）</summary>
        <div class="body stale">${esc(a.rationale)}</div></details>` : ''}
    </div>
    <div class="card"><h3>怎么测的</h3>${facetBlocks}
      <p class="foot">相关度五档由 R25 规则推导（1.0 完全一致 / 0.8 强 / 0.5 中等 / 0.2 弱）；
        置信度起点 1.0，判分方式与数据质量各可扣 0.15。区分度 n / sd 取自 13 号映射效度检查。</p>
    </div>
    <div class="card"><h3>谁做得好</h3>
      ${ranked.length ? `<table><tbody>${bars(ranked)}</tbody></table>
        <p class="foot">实心条 = 全覆盖面板模型，描边条 = 部分覆盖模型。悬停条形看 facet 拆解。
          <b>排名要连着覆盖徽章一起读</b>：P 分是各 facet 的等权平均，只测了部分 facet 的模型等于跳过了没测的那几面，
          与全测模型不在同一量尺上。</p>`
        : '<p class="empty">这项能力目前没有任何模型数据。</p>'}
    </div>`;

  document.getElementById('psel').onchange = e => go('#/p/' + e.target.value);
}

/* ---------- view: benchmark ---------- */
let curB = null, curSub = null;
function viewBench(){
  if (!curB || !benchBy[curB]) curB = D.benchmarks[0].id;
  const b = benchBy[curB];
  const rows = evByBench[curB] || [];
  const subs = [...new Set(rows.map(r => r.sd))].sort();
  if (!curSub || !subs.includes(curSub)) curSub = subs[0];

  const opts = D.benchmarks.map(x => `<option value="${esc(x.id)}" ${x.id === curB ? 'selected' : ''}>${esc(x.id)} — ${esc(x.name)}</option>`).join('');
  const cells = benchToCells[curB] || [];

  // A benchmark's leaderboard lists only models actually run on it. Imputed
  // rows carry the *donor* model's raw value, so showing them here would put a
  // number next to a model that was never evaluated - exactly the fabrication
  // this view must not commit. They are listed separately as 未测过.
  const board = rows.filter(r => r.sd === curSub && !r.zero);
  const seen = new Set();
  const uniq = board.filter(r => { if (seen.has(r.m)) return false; seen.add(r.m); return true; })
                    .sort((x, y) => y.s - x.s);
  const untested = D.models.map(m => m.key).filter(k => !seen.has(k));
  const v = D.validity[curB + '||' + curSub] || {};

  app.innerHTML = `
    <h2>Benchmark 视图</h2>
    <p class="sub">它测什么、我们给了多少置信度、喂给了哪些原子能力、所有模型在它上面的表现。</p>
    <div class="toolbar"><select id="bsel">${opts}</select></div>
    <div class="card">
      <h3>${esc(b.name)} <span style="color:var(--muted);font-weight:400">${esc(b.id)}</span></h3>
      ${b.profile.one_liner ? `<p class="oneline">${esc(b.profile.one_liner)}</p>` : ''}
      ${b.profile.missing ? '<span class="badge warn">档案待补 —— 下方仅有摘要，无完整 profile 文档</span>' : ''}
      <div class="kv">
        <span class="tag">置信权重 ${fx(b.confidence)}</span>
        <span class="tag">${esc(b.metric_family)}</span>
        <span class="tag">${esc(b.score_direction)}</span>
        <span class="tag">${esc(b.source_scope)}</span>
        ${b.profile.file ? `<span class="tag">doc/benchmark_profiles/${esc(b.profile.file)}</span>` : ''}
      </div>
      ${b.profile.sections.length ? `<div class="secs">${b.profile.sections.map(s => `
        <section><h4>${esc(s.heading)}</h4><ul>${s.bullets.map(x => `<li>${esc(x)}</li>`).join('')}</ul></section>`).join('')}</div>` : ''}
      ${b.rationale ? `<details><summary>置信权重的定权理由（含 R2x 裁决记号）</summary>
        <div class="body stale">${esc(b.rationale)}</div></details>` : ''}
    </div>
    <div class="card"><h3>喂给了哪些原子能力</h3>
      ${cells.length ? `<table><thead><tr><th>取分维度</th><th>原子能力 · facet</th><th class="num">相关</th><th class="num">有效</th></tr></thead><tbody>
        ${cells.map(c => `<tr>
          <td>${esc(c.subdimension)}</td>
          <td>${pLink(c.p_code)} · ${esc(c.facet_name)}</td>
          <td class="num">${fx(c.weight)}</td>
          <td class="num">${b.confidence ? fx(c.weight * b.confidence) : '—'}</td>
        </tr>`).join('')}</tbody></table>`
        : '<p class="empty">这个 benchmark 在 v6 映射里没有挂载格。</p>'}
    </div>
    <div class="card">
      <h3>模型表现</h3>
      <div class="toolbar"><select id="ssel">${subs.map(s => `<option ${s === curSub ? 'selected' : ''}>${esc(s)}</option>`).join('')}</select>
        <span class="badge">实测 n=${uniq.length}</span>
        <span class="badge">均分 ${fx(v.mean)}</span>
        <span class="badge">sd ${fx(v.sd)}</span>
        ${(v.flags || []).map(f => `<span class="badge warn">${esc(f)}</span>`).join('')}
      </div>
      <table><thead><tr><th>模型</th><th class="num">原始值</th><th></th><th class="num">0–10 分</th></tr></thead><tbody>
        ${uniq.map(r => `<tr>
          <td>${mLink(r.m)}</td>
          <td class="num">${fx(r.raw, 3)}</td>
          <td style="width:42%"><div class="track"><div class="bar${modelBy[r.m].full_panel ? '' : ' hollow'}"
            style="width:${(r.s * 10).toFixed(1)}%"></div></div></td>
          <td class="num"><b>${fx(r.s)}</b></td>
        </tr>`).join('')}
      </tbody></table>
      ${untested.length ? `<p class="foot" style="margin-top:12px">
        <b class="untested">未测过这一维度的 ${untested.length} 个模型</b>：${untested.map(k => mLink(k)).join('、')}。
        榜上只放真跑过的结果。</p>` : ''}
      <p class="foot">原始值为该 benchmark 的原生指标（${esc(b.metric_family)}），0–10 分是归一后进入映射的值。本榜<b>只列实际跑过的模型</b>：未测过的模型不在此列，因能力不具备记 0 分的模型也不在此列（那不是在这套题上量出来的成绩）。
        ${v.variance_restricted ? '⚠️ 13 号效度检查判定这一维度<b>方差受限</b>，当前模型集上排名信息量低。' : ''}</p>
    </div>`;

  document.getElementById('bsel').onchange = e => { curSub = null; go('#/bench/' + encodeURIComponent(e.target.value)); };
  document.getElementById('ssel').onchange = e => { curSub = e.target.value; viewBench(); };
}

/* ---------- search ---------- */
const index = [
  ...D.models.map(m => ({label: m.display, kind: '模型', hash: '#/model/' + encodeURIComponent(m.key), t: m.display + ' ' + m.key})),
  ...D.abilities.map(a => ({label: a.p_code + ' ' + a.p_name, kind: '原子能力', hash: '#/p/' + a.p_code, t: a.p_code + a.p_name + a.definition})),
  ...D.benchmarks.map(b => ({label: b.name + ' · ' + b.id, kind: 'Benchmark', hash: '#/bench/' + encodeURIComponent(b.id), t: b.id + b.name + b.profile.one_liner}))
];
const qEl = document.getElementById('q'), qrEl = document.getElementById('qr');
let hits = [], sel = 0;
qEl.oninput = () => {
  const q = qEl.value.trim().toLowerCase();
  if (!q){ qrEl.classList.remove('open'); return; }
  hits = index.filter(x => x.t.toLowerCase().includes(q)).slice(0, 12);
  sel = 0;
  qrEl.innerHTML = hits.length
    ? hits.map((h, i) => `<div class="${i === 0 ? 'sel' : ''}" data-i="${i}">${esc(h.label)}<span class="kind">${h.kind}</span></div>`).join('')
    : '<div style="color:var(--muted)">无匹配</div>';
  qrEl.classList.add('open');
  qrEl.querySelectorAll('div[data-i]').forEach(d => d.onclick = () => { go(hits[+d.dataset.i].hash); qEl.value = ''; qrEl.classList.remove('open'); });
};
qEl.onkeydown = e => {
  if (!hits.length) return;
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp'){
    e.preventDefault();
    sel = (sel + (e.key === 'ArrowDown' ? 1 : hits.length - 1)) % hits.length;
    qrEl.querySelectorAll('div[data-i]').forEach((d, i) => d.classList.toggle('sel', i === sel));
  } else if (e.key === 'Enter'){
    go(hits[sel].hash); qEl.value = ''; qrEl.classList.remove('open');
  } else if (e.key === 'Escape'){ qrEl.classList.remove('open'); }
};
document.addEventListener('click', e => { if (!e.target.closest('.search')) qrEl.classList.remove('open'); });

/* ---------- theme ---------- */
const themeBtn = document.getElementById('theme');
themeBtn.onclick = () => {
  const cur = document.documentElement.getAttribute('data-theme');
  const next = cur === 'dark' ? 'light' : (cur === 'light' ? 'dark'
    : (matchMedia('(prefers-color-scheme: dark)').matches ? 'light' : 'dark'));
  document.documentElement.setAttribute('data-theme', next);
  render();
};

/* ---------- router ---------- */
function render(){
  const h = location.hash.replace(/^#\/?/, '');
  const [view, arg] = h.split('/');
  let active = 'overview';
  if (view === 'model'){ active = 'model'; if (arg && modelBy[decodeURIComponent(arg)]){ const k = decodeURIComponent(arg); if (!picked.includes(k)) picked = [k]; else picked = [k, ...picked.filter(x => x !== k)].slice(0, 3); openP = null; } viewModel(); }
  else if (view === 'p'){ active = 'ability'; if (arg) curP = arg; viewAbility(); }
  else if (view === 'bench'){ active = 'bench'; if (arg) curB = decodeURIComponent(arg); viewBench(); }
  else viewOverview();
  document.querySelectorAll('#nav button').forEach(b => b.setAttribute('aria-current', String(b.dataset.view === active)));
  window.scrollTo({top: 0});
}
document.querySelectorAll('#nav button').forEach(b => b.onclick = () => {
  const v = b.dataset.view;
  go(v === 'overview' ? '#/overview' : v === 'model' ? '#/model/' + encodeURIComponent(picked[0] || fullPanel[0])
     : v === 'ability' ? '#/p/' + (curP || coveredP[0]) : '#/bench/' + encodeURIComponent(curB || D.benchmarks[0].id));
});
addEventListener('hashchange', render);
render();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
