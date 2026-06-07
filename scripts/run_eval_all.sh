#!/usr/bin/env bash
# Run the per-benchmark eval pipeline for the C1 main-test benchmarks, one at a
# time, with logs on disk. Designed to survive terminal/SSH close — launch it as:
#
#   nohup ./scripts/run_eval_all.sh >> logs/run_eval_all.out 2>&1 &
#   echo "PID=$!"
#
# Resumable: predictions/extractions are cached per item_id, so re-running skips
# finished work. OlympiadBench scoring needs sympy+antlr 4.11 (which conflicts
# with hydra/omegaconf 4.9 globally), so this script isolates that step with
# `uv run --with` (ephemeral env, no venv dir) and reuses cached predictions.
#
# Config via env vars (all optional):
#   LIMIT=0            number of items per benchmark (0 = all; try 200 first)
#   CONCURRENCY=4      parallel API calls
#   MODEL=MiniMax-M3   model id (M3 is vision-capable; required for OlympiadBench MM)
#   BENCHMARKS="mmlu_pro agieval olympiadbench"   subset to run
#   SKIP_FETCH=0       set 1 to skip the data-fetch step

set -uo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

LIMIT="${LIMIT:-0}"
CONCURRENCY="${CONCURRENCY:-4}"
MODEL="${MODEL:-MiniMax-M3}"
BENCHMARKS="${BENCHMARKS:-mmlu_pro agieval olympiadbench}"
SKIP_FETCH="${SKIP_FETCH:-0}"

LOG_DIR="$ROOT_DIR/logs"
STAMP="$(date +%Y%m%d_%H%M%S)"
mkdir -p "$LOG_DIR"

log() { echo "[$(date +%H:%M:%S)] $*"; }

if [ -z "${MINIMAX_API_KEY:-}" ]; then
  echo "ERROR: MINIMAX_API_KEY is not set in the environment." >&2
  exit 1
fi

# --- 1) data acquisition (idempotent) ---------------------------------------
if [ "$SKIP_FETCH" != "1" ]; then
  log "fetching datasets (mmlu_pro + olympiadbench parquet -> jsonl) ..."
  python scripts/eval/data/fetch_eval_datasets.py --benchmark all \
    >> "$LOG_DIR/fetch_${STAMP}.log" 2>&1 || log "WARN: fetch step returned non-zero (may already exist)"
fi

run_text() {  # benchmarks scored on the main env (no antlr needed)
  local name="$1"
  local logf="$LOG_DIR/${name}_${STAMP}.log"
  log "=== $name : predict + extract + score (limit=$LIMIT) -> $logf"
  python scripts/eval_benchmark.py --benchmark "$name" \
    --model "$MODEL" --limit "$LIMIT" --concurrency "$CONCURRENCY" \
    >> "$logf" 2>&1 \
    && log "$name done" || log "WARN: $name exited non-zero (see $logf)"
}

run_olympiad() {
  local logp="$LOG_DIR/olympiadbench_predict_${STAMP}.log"
  local logs="$LOG_DIR/olympiadbench_score_${STAMP}.log"
  log "=== olympiadbench : predictions on main env (--skip-extract) -> $logp"
  python scripts/eval_benchmark.py --benchmark olympiadbench \
    --model "$MODEL" --limit "$LIMIT" --concurrency "$CONCURRENCY" --skip-extract \
    >> "$logp" 2>&1 \
    && log "olympiadbench predictions done" || log "WARN: olympiadbench predict exited non-zero (see $logp)"

  log "=== olympiadbench : extract + score in ephemeral uv env (sympy + antlr 4.11) -> $logs"
  if ! command -v uv >/dev/null 2>&1; then
    log "ERROR: uv not found — install it (https://docs.astral.sh/uv/) or score with antlr 4.11 manually. Skipping scoring."
    return
  fi
  # uv builds a throwaway env layering sympy+antlr on top of the interpreter;
  # --no-project keeps it from touching the repo. --score-only reuses the
  # predictions written above (extraction is regex-only, no API call here).
  uv run --no-project --with sympy --with "antlr4-python3-runtime==4.11" \
    python scripts/eval_benchmark.py \
    --benchmark olympiadbench --model "$MODEL" --limit "$LIMIT" --score-only \
    >> "$logs" 2>&1 \
    && log "olympiadbench scoring done" || log "WARN: olympiadbench score exited non-zero (see $logs)"
}

log "starting run: BENCHMARKS=[$BENCHMARKS] LIMIT=$LIMIT CONCURRENCY=$CONCURRENCY MODEL=$MODEL"
for b in $BENCHMARKS; do
  case "$b" in
    olympiadbench) run_olympiad ;;
    *)             run_text "$b" ;;
  esac
done
log "all requested benchmarks finished. Reports under reports/eval/<benchmark>/<date>/"
