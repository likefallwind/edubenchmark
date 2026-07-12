#!/bin/bash
# deepseek-v4-pro 自进化复验（§9.4 #2）：judge=reflector=deepseek-v4-pro，
# 与 glm-5.2 / 纯 M3 的自进化完全对称，裁判 n=2 → 3。走 gateway。
# 状态目录 stage1_deepseek-v4-pro/（judge slug 默认解析，无需 OUT_SLUG）。
#
# 用法:  nohup ./scripts/run_judge_stage1_dsv4_self.sh [round] [lines] > /dev/null 2>&1 &
#        round 默认 1；lines 默认 all，可选 mrbench_pg / mrbench_coh / bea_pg
#        （round 2 后 Coherence 与 bea 已按协议收官，round 3 只跑 mrbench_pg）。
#        日志自动写到 reports/eval/_judge_rubric/stage1_deepseek-v4-pro/round<N>_run.log
#
# 断点续跑: 判分响应有条目级缓存，失败后 sleep 300s 重发同命令即续。
set -u
ROUND="${1:-1}"
LINES="${2:-all}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT/reports/eval/_judge_rubric/stage1_deepseek-v4-pro"
mkdir -p "$LOG_DIR"
exec >>"$LOG_DIR/round${ROUND}_run.log" 2>&1

eval "$(grep -E '^export (API_GATEWAY|MINIMAX_API_KEY)=' ~/.bashrc)"
export STAGE1_JUDGE_MODEL=deepseek-v4-pro
export STAGE1_REFLECT_MODEL=deepseek-v4-pro
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

[[ "$LINES" == "all" || "$LINES" == "mrbench_pg"  ]] && run_line mrbench Providing_Guidance
[[ "$LINES" == "all" || "$LINES" == "mrbench_coh" ]] && run_line mrbench Coherence
[[ "$LINES" == "all" || "$LINES" == "bea_pg"      ]] && run_line bea2025 Providing_Guidance
echo "=== round ${ROUND} lines=${LINES} done $(date) ==="
