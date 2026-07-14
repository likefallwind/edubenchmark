#!/bin/bash
# P5 消融（去诊断）：与 glm-5.2 主实验同规格、同预算、同统计门，唯一区别是
# 提案阶段看不到混淆矩阵和错例（--no-diagnosis）。对照的是 glm 主实验 round 1
# 的 3/3 验收——若本臂 0/3，则"收益来自诊断"从间接证据变成直接证据。
# 状态目录 stage1_glm-5.2_nodiag/（STAGE1_OUT_SLUG 隔离，v1 标签仍走 glm 缓存）。
#
# 用法:  nohup ./scripts/run_judge_stage1_nodiag.sh [round] > /dev/null 2>&1 &
#        日志自动写到 reports/eval/_judge_rubric/stage1_glm-5.2_nodiag/round<N>_run.log
# 断点续跑: 判分响应有条目级缓存，失败后 sleep 300s 重发同命令即续。
set -u
ROUND="${1:-1}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT/reports/eval/_judge_rubric/stage1_glm-5.2_nodiag"
mkdir -p "$LOG_DIR"
exec >>"$LOG_DIR/round${ROUND}_run.log" 2>&1

eval "$(grep -E '^export (API_GATEWAY|MINIMAX_API_KEY)=' ~/.bashrc)"
export STAGE1_JUDGE_MODEL=glm-5.2
export STAGE1_REFLECT_MODEL=glm-5.2
export STAGE1_OUT_SLUG=glm-5.2_nodiag
cd "$ROOT/scripts" || exit 1

run_line () {
  local bench="$1" dim="$2"
  for attempt in $(seq 1 72); do
    echo "=== ${bench}/${dim} round ${ROUND} attempt ${attempt} $(date) ==="
    python3 run_judge_rubric_stage1.py --benchmark "$bench" --dimension "$dim" \
      --round "$ROUND" --big-screen --no-diagnosis --concurrency 6 && return 0
    echo "--- attempt ${attempt} failed; sleep 300s then resume ---"
    sleep 300
  done
  echo "!!! ${bench}/${dim} round ${ROUND} gave up after 72 attempts"
  return 1
}

run_line mrbench Providing_Guidance
run_line mrbench Coherence
run_line bea2025 Providing_Guidance
echo "=== nodiag round ${ROUND} done $(date) ==="
