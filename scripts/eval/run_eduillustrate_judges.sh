#!/usr/bin/env bash
# Multi-judge-model comparison for EduIllustrate, on one FIXED M3-generated substrate.
#
# Keeps the generated solutions constant (output/smoke_c3, judged earlier by MiniMax-M3
# into reports/eval/eduillustrate/minimax3/) and swaps only the LLM-as-judge across the
# gateway models that passed the vision pre-flight probe (vision_probe.json -> .kept).
#
# Each judge runs sequentially in its own evaluate.py process (workers=$WORKERS within a
# model). Routing is via EduIllustrate/.env (litellm reads CUSTOM_API_BASE/CUSTOM_API_KEY
# with load_dotenv(override=True)), so we rewrite those two keys per model; the original
# .env is backed up once and restored on exit.
#
# Resumable / rerunnable: evaluate.py reuses --output_folder (skips problems already true);
# a model whose summary.json already has judged==EXPECTED is skipped unless FORCE=1. One
# model failing never aborts the batch — a later rerun picks up only the missing ones.
#
# Env knobs (all optional):
#   MINIMAX_API_KEY   reused minimax3 result needs no key; set only if you re-judge M3.
#   API_GATEWAY       gateway key (default: sk-local-test-123).
#   EDUILLUSTRATE     upstream repo path (default: /home/likefallwind/code/EduIllustrate).
#   SUBSTRATE         generated-solutions folder (default: output/smoke_c3).
#   DATA_PATH         problem metadata json (default: data/benchmark/smoke5.json).
#   WORKERS           per-model judge concurrency (default: 3).
#   RETRY_LIMIT       evaluate.py per-call retries (default: 2).
#   EXPECTED          judged-problem count that marks a model complete (default: 4).
#   FORCE             1 = re-judge even completed models.
set -u

EDUBENCH="$(cd "$(dirname "$0")/../.." && pwd)"
EDUILLUSTRATE="${EDUILLUSTRATE:-/home/likefallwind/code/EduIllustrate}"
SUBSTRATE="${SUBSTRATE:-output/smoke_c3}"
DATA_PATH="${DATA_PATH:-data/benchmark/smoke5.json}"
WORKERS="${WORKERS:-3}"
RETRY_LIMIT="${RETRY_LIMIT:-2}"
EXPECTED="${EXPECTED:-4}"
FORCE="${FORCE:-0}"
API_GATEWAY="${API_GATEWAY:-sk-local-test-123}"
GATEWAY_BASE="${API_GATEWAY_BASE_URL:-http://127.0.0.1:8111/v1}"

PROBE_JSON="$EDUBENCH/reports/eval/eduillustrate/vision_probe.json"
REPORTS_DIR="$EDUBENCH/reports/eval/eduillustrate"
VENV_PY="$EDUILLUSTRATE/.venv/bin/python"
ENV_FILE="$EDUILLUSTRATE/.env"
ENV_BAK="$EDUILLUSTRATE/.env.judgebak"

log() { echo "[$(date +%H:%M:%S)] $*"; }

# ---- judge list from the vision probe ('kept') -----------------------------
if [[ ! -f "$PROBE_JSON" ]]; then
  echo "ERROR: $PROBE_JSON missing — run probe_vision.py first." >&2; exit 2
fi
mapfile -t MODELS < <("$VENV_PY" -c "import json,sys; print('\n'.join(json.load(open('$PROBE_JSON'))['kept']))")
if [[ ${#MODELS[@]} -eq 0 ]]; then
  echo "ERROR: vision probe kept 0 models." >&2; exit 2
fi
log "judge models (vision-passed): ${MODELS[*]}"

# ---- gateway up? -----------------------------------------------------------
if ! curl -s --max-time 8 "$GATEWAY_BASE/models" -H "Authorization: Bearer $API_GATEWAY" >/dev/null; then
  echo "ERROR: gateway $GATEWAY_BASE unreachable." >&2; exit 2
fi

# ---- back up .env once; restore on any exit --------------------------------
if [[ -f "$ENV_FILE" && ! -f "$ENV_BAK" ]]; then cp "$ENV_FILE" "$ENV_BAK"; fi
restore_env() {
  if [[ -f "$ENV_BAK" ]]; then cp "$ENV_BAK" "$ENV_FILE"; log "restored original .env"; fi
}
trap restore_env EXIT

# rewrite CUSTOM_API_BASE / CUSTOM_API_KEY in .env to point at the gateway
route_to_gateway() {
  "$VENV_PY" - "$ENV_BAK" "$ENV_FILE" "$GATEWAY_BASE" "$API_GATEWAY" <<'PY'
import sys
src, dst, base, key = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
lines = open(src, encoding="utf-8").read().splitlines() if __import__("os").path.exists(src) else []
out, seen_base, seen_key = [], False, False
for ln in lines:
    if ln.startswith("CUSTOM_API_BASE="):
        out.append(f"CUSTOM_API_BASE={base}"); seen_base = True
    elif ln.startswith("CUSTOM_API_KEY="):
        out.append(f"CUSTOM_API_KEY={key}"); seen_key = True
    else:
        out.append(ln)
if not seen_base: out.append(f"CUSTOM_API_BASE={base}")
if not seen_key: out.append(f"CUSTOM_API_KEY={key}")
open(dst, "w", encoding="utf-8").write("\n".join(out) + "\n")
PY
}

slug_of() { echo "$1" | sed 's#[^A-Za-z0-9._-]\+#-#g'; }

OVERALL_RC=0
for MODEL in "${MODELS[@]}"; do
  SLUG="$(slug_of "$MODEL")"
  OUT_FOLDER="output/eduillustrate_judge/$SLUG"      # relative to EDUILLUSTRATE
  SLUG_DIR="$REPORTS_DIR/$SLUG"
  SUMMARY="$SLUG_DIR/summary.json"
  mkdir -p "$SLUG_DIR"
  RUNLOG="$SLUG_DIR/run.log"

  if [[ "$FORCE" != "1" && -f "$SUMMARY" ]]; then
    JUDGED="$("$VENV_PY" -c "import json;print(json.load(open('$SUMMARY')).get('judged',0))" 2>/dev/null || echo 0)"
    if [[ "$JUDGED" -ge "$EXPECTED" ]]; then
      log "SKIP $MODEL (already judged=$JUDGED >= $EXPECTED). Set FORCE=1 to redo."
      continue
    fi
  fi

  log "=== JUDGE: $MODEL -> $SLUG (workers=$WORKERS) ===" | tee -a "$RUNLOG"
  route_to_gateway

  (
    cd "$EDUILLUSTRATE" || exit 3
    export API_TIMING_LOG="output/_judge_${SLUG}_timing.log"
    export STREAM_HEARTBEAT=60
    "$VENV_PY" -u evaluate.py \
      --eval_type doc \
      --file_path "$SUBSTRATE" \
      --output_folder "$OUT_FOLDER" \
      --model_doc "$MODEL" \
      --problem_data_path "$DATA_PATH" \
      --bulk_evaluate --combine \
      --max_workers "$WORKERS" \
      --retry_limit "$RETRY_LIMIT"
  ) >>"$RUNLOG" 2>&1
  RC=$?

  if [[ $RC -ne 0 ]]; then
    log "WARN $MODEL evaluate.py exited rc=$RC — see $RUNLOG. Continuing batch (rerun later)." | tee -a "$RUNLOG"
    OVERALL_RC=1
  fi

  # build the per-model report even on partial success (whatever evals exist)
  if compgen -G "$EDUILLUSTRATE/$OUT_FOLDER/evaluation_problem*.json" >/dev/null; then
    "$VENV_PY" "$EDUBENCH/scripts/eval/build_eduillustrate_report.py" \
      --source-repo "$EDUILLUSTRATE" \
      --eval-dir "$OUT_FOLDER" \
      --gen-dir "$SUBSTRATE" \
      --data-path "$EDUILLUSTRATE/$DATA_PATH" \
      --model "MiniMax-M3" \
      --judge-model "$MODEL" \
      --out "$SLUG_DIR" >>"$RUNLOG" 2>&1
    cp "$EDUILLUSTRATE/$OUT_FOLDER"/evaluation_problem*.json "$SLUG_DIR/" 2>/dev/null
    JUDGED="$("$VENV_PY" -c "import json;print(json.load(open('$SUMMARY')).get('judged',0))" 2>/dev/null || echo 0)"
    OVER="$("$VENV_PY" -c "import json;print(json.load(open('$SUMMARY')).get('overall_mean_judged_only','?'))" 2>/dev/null || echo '?')"
    log "DONE $MODEL: judged=$JUDGED/$EXPECTED overall_judged=$OVER -> $SLUG_DIR"
  else
    log "WARN $MODEL produced no evaluation_problem*.json — nothing to report." | tee -a "$RUNLOG"
    OVERALL_RC=1
  fi
done

log "all judges processed (rc=$OVERALL_RC)."
exit $OVERALL_RC
