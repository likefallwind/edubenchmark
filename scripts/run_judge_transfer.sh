#!/bin/bash
# 跨裁判 rubric 迁移矩阵（报告 §9.4 #1）：3 条已验收的 mrbench/PG rubric
# × 3 个裁判，在诊断池子样本（与选择切片零重叠）上判分，对比各自 v1。
# 对角线复用各臂自己的 pool_<version> 缓存，实际约 2.9k 次调用（glm/dsv4 走
# gateway，M3 走 MiniMax）。
#
# 用法:  nohup ./scripts/run_judge_transfer.sh > /dev/null 2>&1 &
#        日志自动写到 reports/eval/_judge_rubric/transfer_matrix/run.log
# 断点续跑: 每格 responses.jsonl 条目级缓存，失败 sleep 300s 重发同命令即续。
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$ROOT/reports/eval/_judge_rubric/transfer_matrix"
mkdir -p "$LOG_DIR"
exec >>"$LOG_DIR/run.log" 2>&1

eval "$(grep -E '^export (API_GATEWAY|MINIMAX_API_KEY)=' ~/.bashrc)"
cd "$ROOT/scripts" || exit 1

for attempt in $(seq 1 72); do
  echo "=== transfer matrix attempt ${attempt} $(date) ==="
  python3 run_judge_rubric_transfer.py --concurrency 6 && exit 0
  echo "--- attempt ${attempt} failed; sleep 300s then resume ---"
  sleep 300
done
echo "!!! gave up after 72 attempts"
exit 1
