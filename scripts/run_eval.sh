#!/usr/bin/env bash
# 一键评测主测 benchmark。
#   ./scripts/run_eval.sh                      # 跑全部 C1 (mmlu_pro agieval olympiadbench)
#   ./scripts/run_eval.sh mmlu_pro             # 只跑指定的一个/多个
#   ./scripts/run_eval.sh eduguard_sata eduguard_adversarial   # C5 EduGuard-Bench
#   LIMIT=200 ./scripts/run_eval.sh agieval    # 小样本试跑 (LIMIT=0 或不设=全量)
#   MODEL=doubao-seed-2.0-pro ./scripts/run_eval.sh ...                # 换被测模型
#   EXTRACTOR_MODEL=MiniMax-M2.7 ./scripts/run_eval.sh ...             # 换答案抽取模型(全局，与被测无关)
#   JUDGE_MODEL=glm-5.1 ./scripts/run_eval.sh eduguard_adversarial     # 换对抗 LLM-as-judge(与被测无关)
# 语言:eduguard_sata 默认中英双语都跑(--language both)。单语言是该评测独有的刻意选项,
#   本脚本不提供旋钮(其它 benchmark 无此概念),需要时直接调底层工具:
#     python scripts/eval_benchmark.py --benchmark eduguard_sata --model "$MODEL" --language en --limit 0
#   注:官方 SATA 仅有英文作答基线、答案键按英文校准,要对标论文/官方请用 en;both 仅作跨语言一致性分析。
# 日志: 默认把运行输出写入 eval/ 文件夹下带时间戳的日志(eval/ 已 gitignore,不会提交)。
#   自定义路径: LOG_FILE=eval/my.log ./scripts/run_eval.sh ; 关闭自动落盘: NO_LOG=1 ./scripts/run_eval.sh
#   后台启动: nohup ./scripts/run_eval.sh >/dev/null 2>&1 &   (输出已由脚本自行 tee 到 eval/)
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

# 默认把本次运行的全部输出同时打印到终端并落盘到 eval/ 下(NO_LOG=1 关闭)。
LOG_DIR="${LOG_DIR:-eval}"
if [[ -z "${NO_LOG:-}" ]]; then
  mkdir -p "$LOG_DIR"
  LOG_FILE="${LOG_FILE:-$LOG_DIR/eval_$(date +%Y%m%d_%H%M%S).log}"
  exec > >(tee -a "$LOG_FILE") 2>&1
  echo "[run_eval] 日志写入 $LOG_FILE"
fi

LIMIT="${LIMIT:-0}"
CONCURRENCY="${CONCURRENCY:-4}"       # 被测模型调用并发数
MODEL="${MODEL:-MiniMax-M3}"                       # 被测模型
EXTRACTOR_MODEL="${EXTRACTOR_MODEL:-MiniMax-M2.7}" # 答案抽取模型(全局；便宜即可，与被测模型无关)
JUDGE_MODEL="${JUDGE_MODEL:-MiniMax-M3}"           # EduGuard 对抗 LLM-as-judge(与被测/抽取模型解耦)
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
      # 两阶段 LLM-as-judge (每阶段 BoN=3 投票)。judge 经 EDUGUARD_JUDGE_MODEL 固定、与被测/抽取模型解耦。
      EDUGUARD_JUDGE_MODEL="$JUDGE_MODEL" \
      python scripts/eval_benchmark.py --benchmark eduguard_adversarial --model "$MODEL" \
        --extractor-model "$EXTRACTOR_MODEL" --concurrency "$CONCURRENCY" --extract-concurrency "$CONCURRENCY" --limit "$LIMIT"
      ;;
    eduguard_sata)
      # 规则评分，默认中英双语都跑 (--language en|zh|both)
      python scripts/eval_benchmark.py --benchmark eduguard_sata --model "$MODEL" --extractor-model "$EXTRACTOR_MODEL" --concurrency "$CONCURRENCY" --limit "$LIMIT"
      ;;
    *)
      python scripts/eval_benchmark.py --benchmark "$b" --model "$MODEL" --extractor-model "$EXTRACTOR_MODEL" --concurrency "$CONCURRENCY" --limit "$LIMIT"
      ;;
  esac
done
