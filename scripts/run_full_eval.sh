#!/usr/bin/env bash
# 单模型全量评测：把 37 个 benchmark 跑完。分成两条流水线并行跑。
#
#   # 流水线 1：GPU 全速出预测，不等第三方
#   MODEL=Qwen/Qwen3.8-27B PHASE=predict CONCURRENCY=32 \
#     nohup ./scripts/run_full_eval.sh > /dev/null 2>&1 &
#
#   # 流水线 2：跟在后面吃已完成的预测，只做抽取+判分
#   MODEL=Qwen/Qwen3.8-27B PHASE=score EXTRACT_CONCURRENCY=6 CONCURRENCY=8 \
#     nohup ./scripts/run_full_eval.sh > /dev/null 2>&1 &
#
# **为什么必须拆成两条**：被测模型跑在自建 vLLM 上(A100，几十路随便开)，抽取和裁判打的
# 是 MiniMax 共享 Token Plan(只扛得住个位数并发)。串在一起跑的话，裁判判 3,797 条的那
# 一两个小时里 GPU 完全闲着——而 GPU 才是这次的主要成本。拆开之后 predict 一路向前，
# score 跟在后面捡，两边各自跑满自己的资源。这两个阶段本来就是可断点续跑的
# (predictions.jsonl / extractions.jsonl 都按 item_id 去重)，拆开不影响任何结果。
#
# score 那条怎么知道预测好了没：predict 每完成一个 benchmark 就在 _done_predict/ 下
# 落一个标记文件，score 按同样的顺序等标记出现再动手。predict 全部结束时落 _ALL 标记，
# score 见到它就不再空等。
#
# 顺序也是有讲究的：吃 MiniMax 配额的排前面(A 组)，纯规则判分的排后面(B 组)。第三方配额
# 是整条链路上唯一会枯竭、会限流、会半夜挂掉的资源，先跑掉它们意味着即使后面出问题，
# 最贵最难重来的那部分已经落盘了。
#
# 其它设计点：每个 benchmark 独立一次调用、独立一份日志，失败只记账不中断队列。
#
# 进度：
#   tail -f logs/full_eval_<slug>/_queue_predict.log
#   tail -f logs/full_eval_<slug>/_queue_score.log
#   cat    logs/full_eval_<slug>/_status_{predict,score}.tsv
set -uo pipefail
cd "$(dirname "$0")/.."

# 评测依赖 pandas/datasets/sacrebleu/nltk 等，装在 miniconda 里而不是默认的 apigateway
# venv 里。run_eval.sh 调的是裸 `python`，所以在这里把 PATH 顶到前面。
export PATH="$HOME/miniconda3/bin:$PATH"
export PYTHONUNBUFFERED=1

MODEL="${MODEL:-Qwen/Qwen3.8-27B}"
PHASE="${PHASE:-predict}"                        # predict | score
CONCURRENCY="${CONCURRENCY:-32}"                 # 被测模型(自建 vLLM)
EXTRACT_CONCURRENCY="${EXTRACT_CONCURRENCY:-6}"  # 抽取/裁判(MiniMax 共享配额)
LIMIT="${LIMIT:-0}"                              # 0 = 全量
WAIT_TIMEOUT="${WAIT_TIMEOUT:-172800}"           # score 等单个 benchmark 预测的上限(秒)

case "$PHASE" in
  predict|score) ;;
  *) echo "PHASE 只能是 predict / score" >&2; exit 2 ;;
esac

slug=$(printf '%s' "$MODEL" | sed -e 's/[^A-Za-z0-9._-]\{1,\}/-/g' -e 's/^-*//' -e 's/-*$//')
LOG_DIR="logs/full_eval_${slug}"
DONE_DIR="$LOG_DIR/_done_predict"
mkdir -p "$LOG_DIR/$PHASE" "$DONE_DIR"
QUEUE_LOG="$LOG_DIR/_queue_${PHASE}.log"
STATUS="$LOG_DIR/_status_${PHASE}.tsv"

# A 组：抽取或判分要打 MiniMax。先跑，因为第三方配额是唯一会枯竭的资源。
GROUP_A=(
  edubench                            # 3797  裁判逐题打 12 维
  tutorbench                          # 1473  逐 rubric 加权裁判
  mmtutorbench                        #  770  6 个 0/1 维度裁判(多模态)
  k12vista                            #  600  逐空 0/1 裁判(多模态)
  eduguard_adversarial                #  801  两阶段裁判，每阶段 BoN=3
  mathtutorbench_scaffolding          # 1150  成对 win-rate 裁判
  mathtutorbench_pedagogy             # 1150
  mathtutorbench_scaffolding_hard     #  327
  mathtutorbench_pedagogy_hard        #  327
  longtutor_teaching                  # 1001  rubric 裁判
  longtutor_evidence                  # 3003  抽取模型即裁判
  longtutor_diagnosis                 # 1001  抽取模型即裁判
  bea2025_tutor                       #  300  固定裁判判 4 维
  mrbench_tutor                       #  200  固定裁判判 8 维
  mathvista                           # 1000  官方协议逐题 LLM 抽取
)

# B 组：规则判分 / 被测模型自己当裁判 / 抽取靠正则。不吃 MiniMax 配额。
# k12bench 排最后：全场最大的一项，放末尾便于随时砍掉或限量而不影响其余结果。
GROUP_B=(
  mmlu_pro                            # 12032  正则为主，LLM 兜底极少
  ceval                               #  1346  官方 5-shot，无抽取
  agieval                             #  7272  官方解析 + sympy 等价判定
  olympiadbench                       #  6728  两段式，判分在 uv 环境跑 sympy
  ifeval                              #   541  官方 checker 规则判分
  pedagogy_benchmark                  #  1119  官方 REPAT 正则
  eduguard_sata                       #  5270  选项集合精确匹配(中英双语)
  mooccube_prereq                     #   300  固定题单，规则判分
  p08_abstention                      #   500  规则判分(脚本内部固定取 500)
  p08_calibration                     #   550  固定题单，抽取=被测模型
  p07_selfcheck                       #   550  两轮自查，第二轮=被测模型
  mathtutorbench_problem_solving      #  1319
  mathtutorbench_socratic             #  1319  sacrebleu
  mathtutorbench_solution_correctness #  2004
  mathtutorbench_mistake_location     #  2004
  mathtutorbench_mistake_correction   #  1002
  mathtutorbench_judge_calibration    #   964  被测模型即裁判
  mrbench_judge                       # 13240  被测模型即裁判
  bea2025_judge                       #  9904  被测模型即裁判
  sas_bench                           #  4109  QWK/CCS 群体统计
  asap_2                              #  7421  规则解析，QWK
  k12bench                            # 23640  多选 MCQ
)

QUEUE=("${GROUP_A[@]}" "${GROUP_B[@]}")

# olympiadbench 在 run_eval.sh 里自带 --skip-extract / --score-only 两段式(判分是本地
# sympy，要切 uv 环境、不调任何 LLM)，PHASE 注入会跳过它。也就是说它在 predict 那趟就
# 已经连判分一起做完了，score 这趟再跑一遍纯属重复空转，所以直接排除。
SCORE_SKIP=" olympiadbench "

{
  echo "===================================================================="
  echo "[full_eval/$PHASE] 开始 $(date -Is)"
  echo "[full_eval/$PHASE] model=$MODEL concurrency=$CONCURRENCY extract_concurrency=$EXTRACT_CONCURRENCY limit=$LIMIT"
  echo "[full_eval/$PHASE] 队列 ${#QUEUE[@]} 项"
  echo "===================================================================="
} | tee -a "$QUEUE_LOG"

[[ -f "$STATUS" ]] || printf 'benchmark\tstatus\tseconds\tfinished_at\n' > "$STATUS"

i=0
for b in "${QUEUE[@]}"; do
  i=$((i + 1))

  if [[ "$PHASE" == "score" ]]; then
    if [[ "$SCORE_SKIP" == *" $b "* ]]; then
      echo "[full_eval/score] ($i/${#QUEUE[@]}) $b 跳过(predict 阶段已自带判分)" | tee -a "$QUEUE_LOG"
      printf '%s\t%s\t%s\t%s\n' "$b" "skipped" 0 "$(date -Is)" >> "$STATUS"
      continue
    fi
    # 等 predict 把这个 benchmark 做完。predict 全部收工后会落 _ALL，
    # 见到它就说明不会再有新预测了，不必继续空等。
    waited=0
    while [[ ! -f "$DONE_DIR/$b" ]]; do
      if [[ -f "$DONE_DIR/_ALL" ]]; then
        echo "[full_eval/score] ($i/${#QUEUE[@]}) $b predict 已收工但无此标记，仍尝试判分" | tee -a "$QUEUE_LOG"
        break
      fi
      if (( waited >= WAIT_TIMEOUT )); then
        echo "[full_eval/score] ($i/${#QUEUE[@]}) $b 等待预测超时($WAIT_TIMEOUT s)，跳过" | tee -a "$QUEUE_LOG"
        printf '%s\t%s\t%s\t%s\n' "$b" "wait_timeout" "$waited" "$(date -Is)" >> "$STATUS"
        continue 2
      fi
      [[ $waited -eq 0 ]] && echo "[full_eval/score] ($i/${#QUEUE[@]}) $b 等待 predict 完成…" | tee -a "$QUEUE_LOG"
      sleep 30; waited=$((waited + 30))
    done
  fi

  t0=$(date +%s)
  echo "[full_eval/$PHASE] ($i/${#QUEUE[@]}) $b 开始 $(date -Is)" | tee -a "$QUEUE_LOG"

  # NO_LOG=1：让本脚本掌管日志落盘，不再让 run_eval.sh 另外往 eval/ 写一份。
  NO_LOG=1 \
  PHASE="$PHASE" \
  MODEL="$MODEL" \
  LIMIT="$LIMIT" \
  CONCURRENCY="$CONCURRENCY" \
  EXTRACT_CONCURRENCY="$EXTRACT_CONCURRENCY" \
    ./scripts/run_eval.sh "$b" > "$LOG_DIR/$PHASE/$b.log" 2>&1
  rc=$?

  t1=$(date +%s); dt=$((t1 - t0))
  if [[ $rc -eq 0 ]]; then st=ok; else st="fail(rc=$rc)"; fi
  # 标记无论成败都落：失败多半是数据/依赖问题，重跑也是同样结果，
  # 让 score 那条继续往下走，不要被卡住。
  [[ "$PHASE" == "predict" ]] && touch "$DONE_DIR/$b"
  printf '%s\t%s\t%s\t%s\n' "$b" "$st" "$dt" "$(date -Is)" >> "$STATUS"
  echo "[full_eval/$PHASE] ($i/${#QUEUE[@]}) $b $st 用时 ${dt}s" | tee -a "$QUEUE_LOG"
done

[[ "$PHASE" == "predict" ]] && touch "$DONE_DIR/_ALL"
echo "[full_eval/$PHASE] 全部结束 $(date -Is)" | tee -a "$QUEUE_LOG"
awk -F'\t' 'NR>1 && $2!="ok" && $2!="skipped"' "$STATUS" | tee -a "$QUEUE_LOG"
