#!/bin/bash
# 纯 M3 自进化实验：judge=MiniMax-M3 且 reflector=MiniMax-M3（不依赖任何外部
# 强模型），与 glm 主实验（judge=glm-5.2 + reflector=glm-5.2 的自进化）对称。
# 状态目录 stage1_minimax3_self/；pilot 的 stage1/ 与 stage1_minimax3_full/ 不动。
#
# 用法:  nohup ./scripts/run_judge_stage1_m3_self.sh [round] > /dev/null 2>&1 &
#        round 默认 1；日志自动写到
#        reports/eval/_judge_rubric/stage1_minimax3_self/round<N>_run.log
#
# 断点续跑: 判分响应有条目级缓存，失败后 sleep 300s 重发同命令即续。
set -u
ROUND="${1:-1}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT/reports/eval/_judge_rubric/stage1_minimax3_self"
mkdir -p "$LOG_DIR"
exec >>"$LOG_DIR/round${ROUND}_run.log" 2>&1

eval "$(grep -E '^export (API_GATEWAY|MINIMAX_API_KEY)=' ~/.bashrc)"
export STAGE1_JUDGE_MODEL=MiniMax-M3
export STAGE1_REFLECT_MODEL=MiniMax-M3
export STAGE1_OUT_SLUG=minimax3_self
cd "$ROOT/scripts" || exit 1

run_line () {
  local bench="$1" dim="$2"
  for attempt in $(seq 1 72); do
    echo "=== ${bench}/${dim} round ${ROUND} attempt ${attempt} $(date) ==="
    python3 run_judge_rubric_stage1.py --benchmark "$bench" --dimension "$dim" \
      --round "$ROUND" --big-screen --rediagnose --concurrency 6 && return 0
    echo "--- attempt ${attempt} failed; sleep 300s then resume ---"
    sleep 300
  done
  echo "!!! ${bench}/${dim} round ${ROUND} gave up after 72 attempts"
  return 1
}

run_line mrbench Providing_Guidance
run_line mrbench Coherence
run_line bea2025 Providing_Guidance
echo "=== round ${ROUND} all lines done $(date) ==="
