#!/bin/bash
# 下游排名实验（报告 §9.4 #4）：v1 vs v2 判官 rubric 重判缓存的 mrbench_tutor
# 生成，比较被测模型排名是否改变。约 2,400 次 glm-5.2 判官调用（走 gateway）。
#
# 用法:  nohup ./scripts/run_downstream_ranking.sh > /dev/null 2>&1 &
#        日志自动写到 reports/eval/_judge_rubric/downstream_ranking/run.log
# 断点续跑: responses.jsonl 按 (模型,题,维度,版本) 缓存，重发同命令即续。
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT/reports/eval/_judge_rubric/downstream_ranking"
mkdir -p "$LOG_DIR"
exec >>"$LOG_DIR/run.log" 2>&1

eval "$(grep -E '^export (API_GATEWAY|MINIMAX_API_KEY)=' ~/.bashrc)"
cd "$ROOT/scripts" || exit 1

for attempt in $(seq 1 72); do
  echo "=== downstream ranking attempt ${attempt} $(date) ==="
  python3 run_judge_downstream_ranking.py --concurrency 6 && exit 0
  echo "--- attempt ${attempt} failed; sleep 300s then resume ---"
  sleep 300
done
echo "!!! gave up after 72 attempts"
exit 1
