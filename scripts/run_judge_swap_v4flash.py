#!/usr/bin/env python3
"""用 deepseek-v4-flash 重判所有"固定 LLM 判官"的 benchmark（面板 5 模型）。

为什么只有这些 benchmark：换判官只对**判官写死**的适配器有意义。
  - 规则判分的（mmlu_pro / ceval / agieval / ifeval / eduguard_sata / olympiadbench /
    asap_2 / sas_bench / pedagogy_benchmark ...）压根没有判官可换；
  - 被测模型自任判官的（mrbench_judge / bea2025_judge /
    mathtutorbench_judge_calibration）换判官等于换被测对象；
  - k12vista / longtutor_* 的判官跟随 ``--extractor-model``，换它会连带改变抽取
    行为，性质不纯。用户 2026-08-13 裁定：**只换 judge，不换 extractor**，故排除。

隔离：输出一律落在 ``reports/eval/<benchmark>/judge-deepseek-v4-flash/<model-slug>/``。
这是 ``eval_benchmark.py`` 在判官 != canonical 时自动选的路径（沿用现有
``judge-deepseek-v3.2/`` 命名），本脚本额外断言一次，确保绝不写回原目录。

预测搬运：``runner.py`` 从 ``out_dir/predictions.jsonl`` 读预测，新目录是空的，所以
每格先把权威源目录的预测复制过去（含分片，并按 item_id 去重——历史重跑在
eduguard_adversarial/glm-5.2 等格留下了重复行，不去重会凭空多判一截）。

    python3 scripts/run_judge_swap_v4flash.py --list
    python3 scripts/run_judge_swap_v4flash.py --smoke            # 一格小样
    python3 scripts/run_judge_swap_v4flash.py --concurrency 8    # 全量
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from eval.predictions_io import read_predictions, write_predictions  # noqa: E402
from eval.judge_dirs import is_judge_dir, judge_dir_name  # noqa: E402
from eval.providers import model_slug  # noqa: E402

JUDGE = "deepseek-v4-flash"
JUDGE_DIR = judge_dir_name(JUDGE)

# 每个适配器读自己的判官环境变量，名字不统一，逐个对。
JUDGE_ENV = {
    "edubench": "EDUBENCH_JUDGE_MODEL",
    "eduguard_adversarial": "EDUGUARD_JUDGE_MODEL",
    "tutorbench": "TUTORBENCH_JUDGE_MODEL",
    "mrbench_tutor": "MRBENCH_JUDGE_MODEL",
    "bea2025_tutor": "BEA2025_JUDGE_MODEL",
    "mmtutorbench": "MMTUTORBENCH_JUDGE_MODEL",
    "mathtutorbench_pedagogy": "MATHTUTORBENCH_JUDGE_MODEL",
    "mathtutorbench_pedagogy_hard": "MATHTUTORBENCH_JUDGE_MODEL",
    "mathtutorbench_scaffolding": "MATHTUTORBENCH_JUDGE_MODEL",
    "mathtutorbench_scaffolding_hard": "MATHTUTORBENCH_JUDGE_MODEL",
}
BENCHMARKS = list(JUDGE_ENV)

PANEL = {"minimax-m3", "minimax-m2.7", "deepseek-v4-pro", "glm-5.2", "doubao-seed-2-0-pro"}


def canonical_model(model: str) -> str:
    """与 build_atomic_ability_rebenchmark_artifacts.canonical_model 保持一致。"""
    key = model.strip().lower().replace("claude sonnet", "claude-sonnet")
    key = key.replace(" ", "-").replace("_", "-").replace(".", "-")
    key = re.sub(r"[^a-z0-9+-]+", "-", key)
    key = re.sub(r"-+", "-", key).strip("-")
    aliases = {
        "minimax-m3": "minimax-m3",
        "minimax-m2-7": "minimax-m2.7",
        "glm-5-2": "glm-5.2",
        "doubao-seed-2-0-pro-260215": "doubao-seed-2-0-pro",
    }
    return aliases.get(key, key)


def discover_cells() -> list[dict]:
    """找出每个 (benchmark, 面板模型) 的权威预测源目录。

    权威 = 去重后 item_id 最多的那份。判官目录（judge-*）也纳入扫描：edubench 的
    面板结果就全在 judge-deepseek-v3.2/ 下。本判官自己的输出目录要排除，否则
    第二次运行会拿自己的结果当源。
    """
    cells: list[dict] = []
    for bench in BENCHMARKS:
        best: dict[str, dict] = {}
        base = ROOT / "reports" / "eval" / bench
        for summary in base.rglob("summary.json"):
            if JUDGE_DIR in summary.parts:
                continue
            try:
                meta = json.loads(summary.read_text())
            except Exception:
                continue
            raw_model = str(meta.get("model") or "")
            key = canonical_model(raw_model)
            if key not in PANEL:
                continue
            src = summary.parent
            if not (src / "predictions.jsonl").exists():
                continue
            try:
                rows = read_predictions(src / "predictions.jsonl")
            except Exception:
                continue
            uniq = len({r.get("item_id") for r in rows})
            if key not in best or uniq > best[key]["unique"]:
                best[key] = {
                    "benchmark": bench,
                    "model_key": key,
                    "model_arg": raw_model,
                    "src": src,
                    "rows": len(rows),
                    "unique": uniq,
                }
        cells.extend(best[k] for k in sorted(best))
    return cells


def stage_predictions(cell: dict) -> Path:
    """把权威预测按 item_id 去重后复制进本判官的隔离目录。"""
    out_dir = ROOT / "reports" / "eval" / cell["benchmark"] / JUDGE_DIR / model_slug(cell["model_arg"])
    # 硬断言：绝不写进 canonical 结果树。
    if JUDGE_DIR not in out_dir.parts:
        raise SystemExit(f"拒绝写入非隔离目录: {out_dir}")
    if out_dir.resolve() == cell["src"].resolve():
        raise SystemExit(f"源目录与输出目录相同,拒绝: {out_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)

    if (out_dir / "predictions.jsonl").exists():
        return out_dir  # 已搬过,断点续跑

    by_item: dict[str, dict] = {}
    for row in read_predictions(cell["src"] / "predictions.jsonl"):
        by_item[row.get("item_id")] = row  # 后出现的覆盖,与 runner._index_by_item 一致
    write_predictions(out_dir / "predictions.jsonl", list(by_item.values()))
    return out_dir


def run_cell(cell: dict, concurrency: int, limit: int | None, dry: bool) -> int:
    out_dir = stage_predictions(cell)
    env = dict(os.environ)
    env[JUDGE_ENV[cell["benchmark"]]] = JUDGE
    cmd = [
        sys.executable,
        "-u",  # 子进程 stdout 是管道,不加 -u 会块缓冲,日志要攒满 4KB 才出现,看着像卡死
        str(ROOT / "scripts" / "eval_benchmark.py"),
        "--benchmark", cell["benchmark"],
        "--model", cell["model_arg"],
        "--out-dir", str(out_dir),
        "--score-only",
        "--extract-concurrency", str(concurrency),
        "--limit", str(limit if limit is not None else 0),
    ]
    label = f"{cell['benchmark']} × {cell['model_key']}"
    print(f"\n===== {label}  ({cell['unique']} 条) -> {out_dir.relative_to(ROOT)} =====", flush=True)
    if dry:
        print("  DRY:", " ".join(cmd), flush=True)
        return 0
    return subprocess.run(cmd, env=env, cwd=ROOT).returncode


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--list", action="store_true", help="只列出待跑的格子")
    ap.add_argument("--smoke", action="store_true", help="只跑最小的一格,限 20 条")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--benchmark", action="append", help="只跑指定 benchmark(可重复)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cells = discover_cells()
    if args.benchmark:
        cells = [c for c in cells if c["benchmark"] in set(args.benchmark)]

    if args.list:
        total = 0
        for c in cells:
            dup = "" if c["rows"] == c["unique"] else f"  (原 {c['rows']} 行,去重后 {c['unique']})"
            print(f"{c['benchmark']:32s} {c['model_key']:20s} {c['unique']:>6d}{dup}")
            total += c["unique"]
        print(f"\n共 {len(cells)} 格 / {total} 条")
        return

    if args.smoke:
        cells = [min(cells, key=lambda c: c["unique"])]
        args.limit = args.limit or 20

    failed = []
    for c in cells:
        rc = run_cell(c, args.concurrency, args.limit, args.dry_run)
        if rc != 0:
            failed.append(f"{c['benchmark']}×{c['model_key']}(exit={rc})")
    print(f"\n===== 完成 {len(cells)} 格,失败 {len(failed)} =====", flush=True)
    for f in failed:
        print("  失败:", f, flush=True)


if __name__ == "__main__":
    main()
