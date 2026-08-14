#!/usr/bin/env bash
# PHASE=score 的跟随器：等某个 benchmark 的预测跑完，再对它做抽取+裁判+判分。
#
# 为什么需要它：predict 和 score 两个阶段可以并行跑(前者吃 GPU、后者吃第三方配额),
# 但 score 不能跑在 predict 前面——对着不存在的预测跑 --score-only 会产出一份
# 全是 no_prediction 的假 summary.json,看起来像正常完成。
#
#   MODEL=Qwen/Qwen3.5-4B EXTRACT_CONCURRENCY=4 \
#     ./scripts/run_eval_score_follower.sh mrbench_tutor edubench ...
#
# 就绪判据是"predictions 行数连续 STABLE_POLLS 次不变"。之所以不用"行数==题目总数",
# 是因为各 benchmark 的实际题量受 --item-list / 各自的 limit 影响(p07/p08 是 550/500,
# 不是 adapter 全量),没有一个可靠的期望值。行数稳定是更朴素但更可靠的信号。
set -uo pipefail
cd "$(dirname "$0")/.."

MODEL="${MODEL:-MiniMax-M3}"
POLL_SECONDS="${POLL_SECONDS:-120}"
STABLE_POLLS="${STABLE_POLLS:-3}"      # 连续几次行数不变才算跑完
MAX_WAIT_HOURS="${MAX_WAIT_HOURS:-72}" # 单个 benchmark 等待上限,超时就跳过

SLUG="$(python3 -c "import sys;sys.path.insert(0,'scripts');from eval.providers import model_slug;print(model_slug('$MODEL'))")"
echo "[follower] model=$MODEL slug=$SLUG 待处理: $*"

# 预测可能分片(predictions.jsonl / predictions.part2.jsonl ...),要全部计入。
#
# 目录并不总是 reports/eval/<benchmark>/<slug>:edubench 会按裁判分目录,预测落在
# reports/eval/edubench/_judge-deepseek-v3.2/<slug>/。只认默认目录会永远数到 0,
# 一直等到 MAX_WAIT_HOURS 超时,把后面所有 benchmark 的判分全堵住。
# 所以默认目录没有预测时,回落到 _judge-*/<slug>/ 找。
predictions_dir() {
  local b="$1" d="reports/eval/$b/$SLUG" c
  compgen -G "$d/predictions*.jsonl" >/dev/null && { echo "$d"; return; }
  for c in "reports/eval/$b"/_judge-*/"$SLUG"; do
    compgen -G "$c/predictions*.jsonl" >/dev/null && { echo "$c"; return; }
  done
  echo "$d"
}

count_predictions() {
  local dir="$1" total=0 f
  for f in "$dir"/predictions*.jsonl; do
    [[ -f "$f" ]] && total=$(( total + $(wc -l < "$f") ))
  done
  echo "$total"
}

# 行数稳定还不够:断点续跑时 predict 进程要先加载题目(大 benchmark 要几分钟),
# 这期间上一轮留下的 predictions 文件一动不动,看着就像"跑完了"。follower 一旦
# 抢先判分,predict 收尾时会拿它启动时读到的(空的)抽取状态把 scored.jsonl /
# summary.json / report.html 重写成全 no_extraction 的空壳——抽取白跑,结果被覆盖。
# (2026-08-13 mmlu_pro 实际踩过一次。)所以再加一条:该 benchmark 的 predict 进程
# 还活着就不算就绪。
predict_running() {
  pgrep -f "eval_benchmark.py --benchmark $1 .*--skip-extract" >/dev/null
}

for b in "$@"; do
  echo "[follower] === $b: 等待预测就绪 ==="
  stable=0; last=-1; waited=0; ready=0
  while (( waited < MAX_WAIT_HOURS * 3600 )); do
    dir="$(predictions_dir "$b")"   # 每轮重解析:目录要等预测开跑才出现
    n=$(count_predictions "$dir")
    if (( n > 0 && n == last )) && ! predict_running "$b"; then
      stable=$(( stable + 1 ))
      (( stable >= STABLE_POLLS )) && { ready=1; break; }
    else
      stable=0
    fi
    last="$n"
    sleep "$POLL_SECONDS"
    waited=$(( waited + POLL_SECONDS ))
  done
  if (( ready == 0 )); then
    echo "[follower] $b 等待超时($MAX_WAIT_HOURS 小时),跳过"
    continue
  fi
  echo "[follower] $b 预测已稳定在 $last 条,开始抽取+判分"
  PHASE=score NO_LOG=1 MODEL="$MODEL" ./scripts/run_eval.sh "$b"
  echo "[follower] $b 判分结束(exit=$?)"
done
echo "[follower] 全部处理完毕"
