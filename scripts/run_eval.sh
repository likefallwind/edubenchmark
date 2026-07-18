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
# EduBench (3,797 个可比英文 prompt；12 维 0-10 连续分，非 accuracy):
#     LIMIT=5 MODEL=<model> ./scripts/run_eval.sh edubench
#   默认沿用已有 11 个模型的 deepseek-v3.2 裁判；替换裁判会自动隔离输出目录：
#     EDUBENCH_JUDGE_MODEL=MiniMax-M3 LIMIT=5 MODEL=<model> ./scripts/run_eval.sh edubench
# Pedagogy Benchmark (教师资格考试的教学法知识 MCQ, AI-for-Education/pedagogy-benchmark): 先物化数据(一次性)
#     python scripts/eval/data/fetch_eval_datasets.py --benchmark pedagogy_benchmark
#   数据集是 gated: 先在 HF 数据集页接受条款,并 export HF_TOKEN=<read token>
#   计分 1,119 题(每类目前 3 题是官方 few-shot 示例,不计分;详见 adapter 文档):
#     LIMIT=20 MODEL=glm-5.2 ./scripts/run_eval.sh pedagogy_benchmark
#   PROMPT_VARIANT 默认 colleague:复刻已迁移结果所用的提示词与解析,补跑新模型可与它们直接对比。
#   官方原文变体(与已迁移结果不可比,勿混用):
#     PROMPT_VARIANT=auto|fewshot|zeroshot MODEL=<model> ./scripts/run_eval.sh pedagogy_benchmark
#   两种变体都是规则解析、无 LLM 抽取;bad_format 率>5% 时官方会剔除该模型,本仓库只标记不剔除。
#   解析失败时重问被测模型(复刻同事 --bad-format-retries,默认 2 次;仅本 benchmark 内生效):
#     PEDAGOGY_BAD_FORMAT_RETRIES=0 ...   # 关掉
# ASAP 2.0 (学生议论文整体评分,模型当评分员; github.com/scrosseye/ASAP_2.0): 先物化数据(一次性)
#     python scripts/eval/data/fetch_eval_datasets.py --benchmark asap_2
#   评官方 test 划分 7,421 篇,主指标 QWK(对齐人工评分);accuracy 按设计为 null:
#     LIMIT=20 MODEL=glm-5.2 ./scripts/run_eval.sh asap_2
#   ASAP_PROMPT_VARIANT 默认 colleague:复刻已迁移结果所用提示词(无量规、分数区间取观测值),
#   已逐题验证可复现其发布的 QWK 到浮点精度,补跑新模型可与它们直接对比。
#   本仓库自拟的量规变体(给官方 rubric 全文、固定 1-6、不泄露标签区间;与已迁移结果不可比):
#     ASAP_PROMPT_VARIANT=rubric MODEL=<model> ./scripts/run_eval.sh asap_2
#     WITH_SOURCE=1 ASAP_PROMPT_VARIANT=rubric ...   # 附源文章(仅 rubric 变体;部分源文被上游版权扣留)
#   解析失败时重问被测模型(复刻同事 --bad-format-retries,默认 2 次;仅本 benchmark 内生效):
#     ASAP_BAD_FORMAT_RETRIES=0 ...   # 关掉
#   全量单模型约合数十美元,不要默认跑全量。ASAP 2.0 无官方 LLM 协议,QWK 不等同官方排行榜成绩。
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

echo "[run_eval] model=$MODEL extractor_model=$EXTRACTOR_MODEL judge_model=$JUDGE_MODEL benchmarks=$BENCHMARKS"

for b in $BENCHMARKS; do
  if [[ "$b" == longtutor_* ]]; then
    # LongTutor uses semantic-equivalence and rubric judging; MiniMax-M3 is
    # intentionally the test-stage model and judge unless explicitly overridden.
    MODEL="${MODEL:-MiniMax-M3}" JUDGE_MODEL="${JUDGE_MODEL:-MiniMax-M3}"
  fi
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
      # extractor 与 judge 保持独立；judge 由 BEA2025_JUDGE_MODEL 的专用 client 调用。
      BEA2025_JUDGE_MODEL="$JUDGE_MODEL" \
      python scripts/eval_benchmark.py --benchmark bea2025_tutor --model "$MODEL" \
        --extractor-model "$EXTRACTOR_MODEL" --concurrency "$CONCURRENCY" --extract-concurrency "$CONCURRENCY" --limit "$LIMIT"
      ;;
    mmtutorbench)
      # 多图输入(previous images + current image)生成 tutoring 回复；固定 rubric judge 打 6 个 0/1 维度。
      # extractor 与 judge 保持独立；judge 由 MMTUTORBENCH_JUDGE_MODEL 的专用 client 调用。
      MMTUTORBENCH_JUDGE_MODEL="$JUDGE_MODEL" \
      python scripts/eval_benchmark.py --benchmark mmtutorbench --model "$MODEL" \
        --extractor-model "$EXTRACTOR_MODEL" --concurrency "$CONCURRENCY" --extract-concurrency "$CONCURRENCY" --limit "$LIMIT"
      ;;
    edubench)
      # 与已导入的 3,797 题结果保持相同题单和默认裁判。extractor-model 直接设为
      # judge，确保裁判 token usage 被通用 runner 正确记录。
      EDUBENCH_JUDGE_MODEL="${EDUBENCH_JUDGE_MODEL:-deepseek-v3.2}" \
      python scripts/eval_benchmark.py --benchmark edubench --model "$MODEL" \
        --extractor-model "${EDUBENCH_JUDGE_MODEL:-deepseek-v3.2}" \
        --concurrency "$CONCURRENCY" --extract-concurrency "$CONCURRENCY" --limit "$LIMIT"
      ;;
    p08_abstention)
      # P08 能力性弃答：UMWP 不可答/可答混合，规则判分（无裁判、抽取不调用 LLM）。
      # 先物化数据：python scripts/eval/data/fetch_eval_datasets.py --benchmark umwp
      # 默认抽 500 题（分层，任意前缀均衡），LIMIT 可覆盖；不默认跑全量 5200。
      P08_ABS_LIMIT="${LIMIT:-500}"; [[ "$P08_ABS_LIMIT" == "0" ]] && P08_ABS_LIMIT=500
      python scripts/eval_benchmark.py --benchmark p08_abstention --model "$MODEL" \
        --extractor-model "$EXTRACTOR_MODEL" --concurrency "$CONCURRENCY" --limit "$P08_ABS_LIMIT"
      ;;
    ifeval)
      # IFEval 规则判分（无裁判无抽取 LLM）；先物化数据: fetch_eval_datasets.py --benchmark ifeval
      # 判分依赖 nltk/langdetect/immutabledict（miniconda python 已装）。
      python scripts/eval_benchmark.py --benchmark ifeval --model "$MODEL" --concurrency "$CONCURRENCY" --limit "$LIMIT" --extractor-model "$EXTRACTOR_MODEL"
      ;;
    k12vista)
      # K12Vista 中文 K12 多模态学科推理（P04）；提示与判分照搬官方 prompt.py。
      # 先物化数据 + 生成固定题单（一次性）：
      #   python scripts/eval/data/fetch_eval_datasets.py --benchmark k12vista
      #   python scripts/eval/data/build_k12vista_sample.py --size 600
      # 判分是 LLM 裁判逐空 0/1（官方 rubric），裁判固定为 K12VISTA_JUDGE_MODEL/JUDGE_MODEL
      # （默认跟随 EXTRACTOR_MODEL），与被测模型解耦；被测模型必须是视觉模型。
      K12VISTA_JUDGE_MODEL="${K12VISTA_JUDGE_MODEL:-$JUDGE_MODEL}" \
      python scripts/eval_benchmark.py --benchmark k12vista --model "$MODEL" \
        --extractor-model "$EXTRACTOR_MODEL" --concurrency "$CONCURRENCY" --extract-concurrency "$CONCURRENCY" --limit "$LIMIT"
      ;;
    mooccube_prereq)
      # MOOCCube 先修关系推理（P19 路径规划的知识结构基础）；100% 规则判分，无裁判、无抽取模型。
      # 先物化数据 + 生成固定题单（一次性）：
      #   python scripts/eval/data/fetch_eval_datasets.py --benchmark mooccube
      #   python scripts/eval/data/build_mooccube_item_list.py --size 300
      # 默认跑固定的 300 题题单（200 先修选择 + 100 学习顺序排序），所有模型同题。
      ITEM_LIST="${ITEM_LIST:-data/mooccube/item_list_v1.txt}"
      python scripts/eval_benchmark.py --benchmark mooccube_prereq --model "$MODEL" \
        --extractor-model "$EXTRACTOR_MODEL" --concurrency "$CONCURRENCY" --item-list "$ITEM_LIST"
      ;;
    p07_selfcheck)
      # P07 两轮自查：第一轮答题 + 第二轮无提示复查（extract 阶段调被测模型本身）。
      # 与 p08_calibration 共用同一份难度分层 item_list，P07/P08 同题可比。
      #   MODEL=MiniMax-M3 ./scripts/run_eval.sh p07_selfcheck
      ITEM_LIST="${ITEM_LIST:-data/p08_calibration/item_list_v1.txt}"
      P07_EXTRACTOR_MODEL="${P07_EXTRACTOR_MODEL:-$MODEL}"
      # 第二轮复查发生在 extract 阶段，所以 --extract-concurrency 必须跟着给：
      # 它默认是 1，漏传的话第二轮会单线程爬（550 题要跑一整天）。
      python scripts/eval_benchmark.py --benchmark p07_selfcheck --model "$MODEL" \
        --extractor-model "$P07_EXTRACTOR_MODEL" --concurrency "$CONCURRENCY" \
        --extract-concurrency "$CONCURRENCY" --item-list "$ITEM_LIST"
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
    longtutor_evidence|longtutor_teaching)
      python scripts/eval_benchmark.py --benchmark "$b" --limit "$LIMIT" \
        --model "$MODEL" --extractor-model "$JUDGE_MODEL" \
        --concurrency "$CONCURRENCY" --extract-concurrency "$CONCURRENCY" "${COMMON_ARGS[@]}"
      ;;
    longtutor_diagnosis)
      python scripts/eval_benchmark.py --benchmark "$b" --limit "$LIMIT" \
        --model "$MODEL" --extractor-model "$JUDGE_MODEL" \
        --concurrency "$CONCURRENCY" "${COMMON_ARGS[@]}"
      ;;
    *)
      python scripts/eval_benchmark.py --benchmark "$b" --model "$MODEL" --extractor-model "$EXTRACTOR_MODEL" --concurrency "$CONCURRENCY" --limit "$LIMIT"
      ;;
  esac
done
