#!/usr/bin/env bash
# 裁判选择评测：逐个候选裁判跑 mathtutorbench_judge_calibration（论文 482 对专家偏好，
# 位置交换 = 964 题），比 agreement 选 win-rate 任务的生产裁判。
#
# 用法:
#   ./scripts/run_judge_calibration.sh            # 全量 (LIMIT=0)
#   LIMIT=40 ./scripts/run_judge_calibration.sh   # 小样本探针
#   后台: nohup ./scripts/run_judge_calibration.sh >/dev/null 2>&1 &   (脚本自行 tee 到 eval/)
#
# 候选裁判与 provider（除 MiniMax 系列外一律走 gateway）:
#   MiniMax-M3, MiniMax-M2.7            -> minimax (MINIMAX_API_KEY，prefix 自动解析)
#   glm-5.2                            -> gateway (API_GATEWAY)
#   deepseek-v3.2/-v4-pro/-v4-flash    -> gateway (API_GATEWAY，强制 --provider gateway，
#                                         不走 DeepSeek 官方 API)
set -uo pipefail
cd "$(dirname "$0")/.."
export PYTHONUNBUFFERED=1

# 默认用带依赖的 miniconda python（默认 PATH 的 python 指向 apigateway venv，缺 requests/依赖）
PY="${PY:-/home/likefallwind/miniconda3/bin/python}"
LIMIT="${LIMIT:-0}"                 # 0/不设 = 全量 964 题
CONCURRENCY="${CONCURRENCY:-3}"
BENCH=mathtutorbench_judge_calibration

LOG_DIR="${LOG_DIR:-eval}"
mkdir -p "$LOG_DIR"
LOG_FILE="${LOG_FILE:-$LOG_DIR/judge_calib_$(date +%Y%m%d_%H%M%S).log}"
exec > >(tee -a "$LOG_FILE") 2>&1
echo "[judge-calib] 日志 $LOG_FILE | PY=$PY | LIMIT=$LIMIT | CONCURRENCY=$CONCURRENCY"

# "模型:provider"  —— provider 为空表示按 prefix 自动解析(minimax)；非空则强制
MODELS=(
  "MiniMax-M3:"
  "MiniMax-M2.7:"
  "glm-5.2:gateway"
  "deepseek-v3.2:gateway"
  "deepseek-v4-pro:gateway"
  "deepseek-v4-flash:gateway"
)

for entry in "${MODELS[@]}"; do
  model="${entry%%:*}"
  provider="${entry#*:}"
  echo ""
  echo "==================== $model (provider=${provider:-auto}) ===================="
  args=(--benchmark "$BENCH" --model "$model"
        --concurrency "$CONCURRENCY" --extract-concurrency "$CONCURRENCY" --limit "$LIMIT")
  [[ -n "$provider" ]] && args+=(--provider "$provider")
  "$PY" scripts/eval_benchmark.py "${args[@]}" || echo "!! $model 运行出错(已跳过，继续下一个)"
done

echo ""
echo "==================== 汇总 (agreement 越高越好) ===================="
"$PY" - <<'PYEOF'
import json, glob, os
base = "reports/eval/mathtutorbench_judge_calibration"
rows = []
for sd in sorted(glob.glob(f"{base}/*/summary.json")):
    s = json.load(open(sd))
    e = s.get("extra_metrics", {}) or {}
    rows.append((os.path.basename(os.path.dirname(sd)), s.get("scored"), s.get("total_items"),
                 e.get("agreement"), e.get("position_consistency")))
rows.sort(key=lambda r: (r[3] is not None, r[3] or 0), reverse=True)
print(f"{'model-slug':24}{'scored':>12}{'agreement':>12}{'pos_consist':>14}")
for slug, scored, total, agr, pc in rows:
    print(f"{slug:24}{str(scored)+'/'+str(total):>12}{str(agr):>12}{str(pc):>14}")
print("\n推荐生产裁判 = agreement 最高者；用 MATHTUTORBENCH_JUDGE_MODEL / JUDGE_MODEL 设定。")
PYEOF
echo "[judge-calib] done"
