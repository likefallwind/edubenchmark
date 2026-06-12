#!/usr/bin/env bash
# 一键评测主测 benchmark。
#   ./scripts/run_eval.sh                      # 跑全部 C1 (mmlu_pro agieval olympiadbench)
#   ./scripts/run_eval.sh mmlu_pro             # 只跑指定的一个/多个
#   ./scripts/run_eval.sh eduguard_sata eduguard_adversarial   # C5 EduGuard-Bench
#   LIMIT=200 ./scripts/run_eval.sh agieval    # 小样本试跑 (LIMIT=0 或不设=全量)
#   MODEL=MiniMax-M3 JUDGE_MODEL=MiniMax-M3 ./scripts/run_eval.sh ...   # 换被测/judge 模型
# 后台启动: nohup ./scripts/run_eval.sh > eval.log 2>&1 &
set -uo pipefail
cd "$(dirname "$0")/.."
export PYTHONUNBUFFERED=1   # 让 print 实时写入日志，方便 tail -f

LIMIT="${LIMIT:-0}"
MODEL="${MODEL:-MiniMax-M3}"          # 被测模型
JUDGE_MODEL="${JUDGE_MODEL:-$MODEL}"  # LLM-as-judge / 答案抽取模型
BENCHMARKS="${*:-mmlu_pro agieval olympiadbench}"

for b in $BENCHMARKS; do
  case "$b" in
    olympiadbench)
      # 主环境出预测，再用 uv 临时环境(antlr 4.11)判分
      python scripts/eval_benchmark.py --benchmark olympiadbench --model "$MODEL" --concurrency 4 --limit "$LIMIT" --skip-extract
      uv run --no-project --with sympy --with 'antlr4-python3-runtime==4.11' \
        python scripts/eval_benchmark.py --benchmark olympiadbench --model "$MODEL" --limit "$LIMIT" --score-only
      ;;
    eduguard_adversarial)
      # 两阶段 LLM-as-judge (每阶段 BoN=3 投票)，judge 走 --extractor-model
      python scripts/eval_benchmark.py --benchmark eduguard_adversarial --model "$MODEL" \
        --extractor-model "$JUDGE_MODEL" --concurrency 4 --extract-concurrency 4 --limit "$LIMIT"
      ;;
    eduguard_sata)
      # 规则评分，默认中英双语都跑 (--language en|zh|both)
      python scripts/eval_benchmark.py --benchmark eduguard_sata --model "$MODEL" --concurrency 4 --limit "$LIMIT"
      ;;
    *)
      python scripts/eval_benchmark.py --benchmark "$b" --model "$MODEL" --concurrency 4 --limit "$LIMIT"
      ;;
  esac
done
