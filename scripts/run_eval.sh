#!/usr/bin/env bash
# 一键评测 C1 主测 benchmark。
#   ./scripts/run_eval.sh                      # 跑全部 (mmlu_pro agieval olympiadbench)
#   ./scripts/run_eval.sh mmlu_pro             # 只跑指定的一个/多个
#   LIMIT=200 ./scripts/run_eval.sh agieval    # 小样本试跑 (LIMIT=0 或不设=全量)
# 后台启动: nohup ./scripts/run_eval.sh > eval.log 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."
export PYTHONUNBUFFERED=1   # 让 print 实时写入日志，方便 tail -f

LIMIT="${LIMIT:-0}"
BENCHMARKS="${*:-mmlu_pro agieval olympiadbench}"

for b in $BENCHMARKS; do
  if [ "$b" = "olympiadbench" ]; then
    # 主环境出预测，再用 uv 临时环境(antlr 4.11)判分
    python scripts/eval_benchmark.py --benchmark olympiadbench --model MiniMax-M3 --concurrency 4 --limit "$LIMIT" --skip-extract
    uv run --no-project --with sympy --with 'antlr4-python3-runtime==4.11' \
      python scripts/eval_benchmark.py --benchmark olympiadbench --model MiniMax-M3 --limit "$LIMIT" --score-only
  else
    python scripts/eval_benchmark.py --benchmark "$b" --model MiniMax-M3 --concurrency 4 --limit "$LIMIT"
  fi
done
