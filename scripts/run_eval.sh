#!/usr/bin/env bash
# 一键评测 C1 主测 benchmark。后台启动:
#   nohup ./scripts/run_eval.sh > eval.log 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."

python scripts/eval_benchmark.py --benchmark mmlu_pro --concurrency 4 --limit 0
python scripts/eval_benchmark.py --benchmark agieval  --concurrency 4 --limit 0

# OlympiadBench：主环境出预测，再用 uv 临时环境(antlr 4.11)判分
python scripts/eval_benchmark.py --benchmark olympiadbench --model MiniMax-M3 --concurrency 4 --limit 0 --skip-extract
uv run --no-project --with sympy --with 'antlr4-python3-runtime==4.11' \
  python scripts/eval_benchmark.py --benchmark olympiadbench --model MiniMax-M3 --limit 0 --score-only
