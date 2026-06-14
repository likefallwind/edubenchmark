#!/usr/bin/env bash
# 一键评测主测 benchmark。
#   ./scripts/run_eval.sh                      # 跑全部 C1 (mmlu_pro agieval olympiadbench)
#   ./scripts/run_eval.sh mmlu_pro             # 只跑指定的一个/多个
#   ./scripts/run_eval.sh eduguard_sata eduguard_adversarial   # C5 EduGuard-Bench
#   LIMIT=200 ./scripts/run_eval.sh agieval    # 小样本试跑 (LIMIT=0 或不设=全量)
#   MODEL=MiniMax-M3 JUDGE_MODEL=MiniMax-M3 ./scripts/run_eval.sh ...   # 换被测/judge 模型
#   CONCURRENCY=2 JUDGE_MODEL=MiniMax-M3 ./scripts/run_eval.sh eduguard_sata eduguard_adversarial
# 后台启动: nohup ./scripts/run_eval.sh > eval.log 2>&1 &
#
# 限流自愈：连续 RATE_LIMIT_THRESHOLD 个(默认10) 429/限流错误即判定被限流，自动 sleep
#   RATE_LIMIT_SLEEP 秒(默认1800=30min) 后重试被限流的样本(每条最多重排 RATE_LIMIT_MAX_RETRIES 次,默认3)。
#   例: RATE_LIMIT_SLEEP=1800 RATE_LIMIT_THRESHOLD=10 ./scripts/run_eval.sh
#
# 注意：本脚本评测「被测模型在 benchmark 上的得分」。若要评测「judge 本身判得准不准」
# （EduGuard P2 LLM-as-judge 对 Opus 金标的校准），那是另一层实验，独立工具见
#   scripts/experiments/eduguard_judge_eval.py
#   reports/re_benchmark_v1/experiments/eduguard_judge_calibration/README.md
set -uo pipefail
cd "$(dirname "$0")/.."
export PYTHONUNBUFFERED=1   # 让 print 实时写入日志，方便 tail -f

LIMIT="${LIMIT:-0}"
CONCURRENCY="${CONCURRENCY:-4}"       # 被测模型调用并发数
MODEL="${MODEL:-MiniMax-M3}"          # 被测模型
JUDGE_MODEL="${JUDGE_MODEL:-$MODEL}"  # LLM-as-judge / 答案抽取模型
BENCHMARKS="${*:-mmlu_pro agieval olympiadbench}"

for b in $BENCHMARKS; do
  case "$b" in
    olympiadbench)
      # 主环境出预测，再用 uv 临时环境(antlr 4.11)判分
      python scripts/eval_benchmark.py --benchmark olympiadbench --model "$MODEL" --concurrency "$CONCURRENCY" --limit "$LIMIT" --skip-extract
      uv run --no-project --with sympy --with 'antlr4-python3-runtime==4.11' \
        python scripts/eval_benchmark.py --benchmark olympiadbench --model "$MODEL" --limit "$LIMIT" --score-only
      ;;
    eduguard_adversarial)
      # 两阶段 LLM-as-judge (每阶段 BoN=3 投票)，judge 走 --extractor-model
      python scripts/eval_benchmark.py --benchmark eduguard_adversarial --model "$MODEL" \
        --extractor-model "$JUDGE_MODEL" --concurrency "$CONCURRENCY" --extract-concurrency "$CONCURRENCY" --limit "$LIMIT"
      ;;
    eduguard_sata)
      # 规则评分，默认中英双语都跑 (--language en|zh|both)
      python scripts/eval_benchmark.py --benchmark eduguard_sata --model "$MODEL" --concurrency "$CONCURRENCY" --limit "$LIMIT"
      ;;
    *)
      python scripts/eval_benchmark.py --benchmark "$b" --model "$MODEL" --concurrency "$CONCURRENCY" --limit "$LIMIT"
      ;;
  esac
done
