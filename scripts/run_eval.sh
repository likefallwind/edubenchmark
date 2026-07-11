#!/usr/bin/env bash
# 一键评测主测 benchmark。
#   ./scripts/run_eval.sh                      # 跑全部 C1 (mmlu_pro agieval olympiadbench)
#   ./scripts/run_eval.sh mmlu_pro             # 只跑指定的一个/多个
#   ./scripts/run_eval.sh eduguard_sata eduguard_adversarial   # C5 EduGuard-Bench
#   LIMIT=200 ./scripts/run_eval.sh agieval    # 小样本试跑 (LIMIT=0 或不设=全量)
#   MODEL=doubao-seed-2.0-pro ./scripts/run_eval.sh ...                # 换被测模型
#   EXTRACTOR_MODEL=MiniMax-M2.7 ./scripts/run_eval.sh ...             # 换答案抽取模型(全局，与被测无关)
#   JUDGE_MODEL=glm-5.1 ./scripts/run_eval.sh eduguard_adversarial     # 换对抗 LLM-as-judge(与被测无关)
# MathTutorBench (C4 过程评分/反馈质量, eth-lre/mathtutorbench): 先物化数据(一次性)
#     python scripts/eval/data/fetch_eval_datasets.py --benchmark mathtutorbench
#   闭式任务(无 judge,官方判分): mathtutorbench_{problem_solving,socratic,solution_correctness,mistake_location,mistake_correction}
#     ./scripts/run_eval.sh mathtutorbench_solution_correctness mathtutorbench_mistake_location   # (socratic 需 pip install sacrebleu)
#   开放式教学反馈(LLM-as-judge 成对 win-rate,裁判=JUDGE_MODEL,默认 MiniMax-M3,替代官方 GPU 奖励模型):
#     ./scripts/run_eval.sh mathtutorbench_scaffolding mathtutorbench_pedagogy mathtutorbench_scaffolding_hard mathtutorbench_pedagogy_hard
#   裁判选择先行(被测模型即候选裁判,--model 传候选裁判,与人类偏好一致率越高越好,选一致率最高者作生产裁判):
#     MODEL=MiniMax-M3 ./scripts/run_eval.sh mathtutorbench_judge_calibration
#     MODEL=glm-5.1    ./scripts/run_eval.sh mathtutorbench_judge_calibration   # 对比另一候选裁判
# MRBench (C4 教学反馈质量/错误诊断, kaushal0494/UnifyingAITutorEvaluation): 先物化数据(一次性)
#     python scripts/eval/data/fetch_eval_datasets.py --benchmark mrbench
#   Step 1 裁判校准(被测模型即裁判,逐维度与人工标注比对,extra_metrics 给每维度 agreement/F1/kappa):
#     MODEL=MiniMax-M3 ./scripts/run_eval.sh mrbench_judge
#     MODEL=glm-5.1    ./scripts/run_eval.sh mrbench_judge      # 对比另一候选裁判
#   Step 2 生成+裁判打分(被测模型生成 tutor 回复,固定裁判=JUDGE_MODEL 默认 MiniMax-M3 逐 8 维打标):
#     ./scripts/run_eval.sh mrbench_tutor
#     MODEL=doubao-seed-2.0-pro JUDGE_MODEL=MiniMax-M3 ./scripts/run_eval.sh mrbench_tutor
# BEA 2025 shared task (4 维 pedagogical ability;dev 有人工标签,test 标签隐藏): 先物化数据(一次性)
#     python scripts/eval/data/fetch_eval_datasets.py --benchmark bea2025
#   Step 1 裁判校准(被测模型即候选裁判,先用 LIMIT=20 小样本对齐 human labels):
#     LIMIT=20 MODEL=MiniMax-M3 ./scripts/run_eval.sh bea2025_judge
#   Step 2 生成+裁判打分(固定裁判=JUDGE_MODEL/BEA2025_JUDGE_MODEL;不要默认全量):
#     LIMIT=20 MODEL=doubao-seed-2.0-pro JUDGE_MODEL=MiniMax-M3 ./scripts/run_eval.sh bea2025_tutor
# MMTutorBench (多模态数学 tutoring, Tangchiu/mmtutorbench): 先物化数据(一次性)
#     python scripts/eval/data/fetch_eval_datasets.py --benchmark mmtutorbench
#   小样本 smoke test(固定 rubric judge=JUDGE_MODEL,默认 MiniMax-M3; 不默认跑全量 770):
#     LIMIT=5 MODEL=MiniMax-M3 JUDGE_MODEL=MiniMax-M3 ./scripts/run_eval.sh mmtutorbench
#   若公开数据后续提供逐题 human/expert gold,再跑 judge calibration;当前公开 JSONL 无 human gold:
#     LIMIT=20 MODEL=MiniMax-M3 ./scripts/run_eval.sh mmtutorbench_judge_calibration
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
JUDGE_MODEL="${JUDGE_MODEL:-MiniMax-M3}"           # LLM-as-judge(EduGuard/MathTutorBench/MRBench/BEA2025/MMTutorBench;与被测/抽取模型解耦)
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
    mathtutorbench_scaffolding|mathtutorbench_pedagogy|mathtutorbench_scaffolding_hard|mathtutorbench_pedagogy_hard)
      # 开放式教学反馈：LLM-as-judge 成对 win-rate(对金标教师回应，位置交换去偏)。
      # 裁判经 MATHTUTORBENCH_JUDGE_MODEL 固定、与被测/抽取模型解耦，替代官方需 GPU 的 1.5B 偏好奖励模型。
      MATHTUTORBENCH_JUDGE_MODEL="$JUDGE_MODEL" \
      python scripts/eval_benchmark.py --benchmark "$b" --model "$MODEL" \
        --extractor-model "$EXTRACTOR_MODEL" --concurrency "$CONCURRENCY" --extract-concurrency "$CONCURRENCY" --limit "$LIMIT"
      ;;
    mrbench_tutor)
      # Step 2 生成+裁判打分：被测模型生成 tutor 回复，固定裁判逐 8 维打标。
      # 裁判经 MRBENCH_JUDGE_MODEL 固定、与被测/抽取模型解耦；每条 item 裁判扇出 8 个维度，故抬高抽取并发。
      MRBENCH_JUDGE_MODEL="$JUDGE_MODEL" \
      python scripts/eval_benchmark.py --benchmark mrbench_tutor --model "$MODEL" \
        --extractor-model "$EXTRACTOR_MODEL" --concurrency "$CONCURRENCY" --extract-concurrency "$CONCURRENCY" --limit "$LIMIT"
      ;;
    bea2025_tutor)
      # Step 2 生成+裁判打分：被测模型生成 tutor 回复，固定裁判逐 4 个 BEA 维度打标。
      # 这里把 --extractor-model 设成 JUDGE_MODEL，使 judge token usage 进入 summary.json 的 extraction usage。
      BEA2025_JUDGE_MODEL="$JUDGE_MODEL" \
      python scripts/eval_benchmark.py --benchmark bea2025_tutor --model "$MODEL" \
        --extractor-model "$JUDGE_MODEL" --concurrency "$CONCURRENCY" --extract-concurrency "$CONCURRENCY" --limit "$LIMIT"
      ;;
    mmtutorbench)
      # 多图输入(previous images + current image)生成 tutoring 回复；固定 rubric judge 打 6 个 0/1 维度。
      # 这里把 --extractor-model 设成 JUDGE_MODEL，使 judge token usage 进入 summary.json 的 extraction usage。
      MMTUTORBENCH_JUDGE_MODEL="$JUDGE_MODEL" \
      python scripts/eval_benchmark.py --benchmark mmtutorbench --model "$MODEL" \
        --extractor-model "$JUDGE_MODEL" --concurrency "$CONCURRENCY" --extract-concurrency "$CONCURRENCY" --limit "$LIMIT"
      ;;
    p08_abstention)
      # P08 能力性弃答：UMWP 不可答/可答混合，规则判分（无裁判、抽取不调用 LLM）。
      # 先物化数据：python scripts/eval/data/fetch_eval_datasets.py --benchmark umwp
      # 默认抽 500 题（分层，任意前缀均衡），LIMIT 可覆盖；不默认跑全量 5200。
      P08_ABS_LIMIT="${LIMIT:-500}"; [[ "$P08_ABS_LIMIT" == "0" ]] && P08_ABS_LIMIT=500
      python scripts/eval_benchmark.py --benchmark p08_abstention --model "$MODEL" \
        --extractor-model "$EXTRACTOR_MODEL" --concurrency "$CONCURRENCY" --limit "$P08_ABS_LIMIT"
      ;;
    p08_calibration)
      # P08 置信校准：跑固定难度分层 item_list（非 --limit；先用 build_p08_item_list.py 生成）。
      # 答案抽取主要靠各 delegate 的正则，LLM 兜底极少；抽取模型默认跟随被测模型
      # （P08_EXTRACTOR_MODEL 覆盖），当前仅 MiniMax-M3 可用。
      #   python scripts/eval/data/build_p08_item_list.py   # 一次性生成 item_list
      #   MODEL=MiniMax-M3 ./scripts/run_eval.sh p08_calibration
      ITEM_LIST="${ITEM_LIST:-data/p08_calibration/item_list_v1.txt}"
      P08_EXTRACTOR_MODEL="${P08_EXTRACTOR_MODEL:-$MODEL}"
      python scripts/eval_benchmark.py --benchmark p08_calibration --model "$MODEL" \
        --extractor-model "$P08_EXTRACTOR_MODEL" --concurrency "$CONCURRENCY" --item-list "$ITEM_LIST"
      ;;
    *)
      python scripts/eval_benchmark.py --benchmark "$b" --model "$MODEL" --extractor-model "$EXTRACTOR_MODEL" --concurrency "$CONCURRENCY" --limit "$LIMIT"
      ;;
  esac
done
