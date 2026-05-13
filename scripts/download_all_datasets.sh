#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_PATH="$ROOT_DIR/data/exhaustive_2026-05-13/dataset_acquisition_report.md"
SUMMARY_FILE="$ROOT_DIR/data/exhaustive_2026-05-13/download_summary.csv"
TRACE_FILE="$ROOT_DIR/data/exhaustive_2026-05-13/dataset_download.log"
DATASET_BASE="$ROOT_DIR/sources/datasets"
COMMAND_TIMEOUT="${COMMAND_TIMEOUT:-1200}"
export KAGGLE_CONFIG_DIR="$ROOT_DIR/.cache/kaggle"

normalize_cmd() {
  local cmd="$1"
  cmd="${cmd//\`/}"
  cmd="$(printf '%s' "$cmd" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')"
  cmd="${cmd/hf download/huggingface-cli download}"
  printf '%s' "$cmd"
}

mkdir -p "$DATASET_BASE" "$ROOT_DIR/data/exhaustive_2026-05-13/download_logs"
mkdir -p "$KAGGLE_CONFIG_DIR"

# Keep historical attempts in summary for FAILED_ONLY support, only initialize once.
if [ ! -f "$SUMMARY_FILE" ]; then
  echo "timestamp,status,command,return_code" > "$SUMMARY_FILE"
fi
: > "$TRACE_FILE"

tmp_commands="$(mktemp)"
tmp_summary="$(mktemp)"
trap 'rm -f "$tmp_commands" "$tmp_summary"' EXIT

awk -F'|' '
  /^\| / {
    cmd=$4
    if (cmd ~ /`/) {
      gsub(/^[[:space:]]+|[[:space:]]+$/, "", cmd)
      gsub(/`/, "", cmd)
      gsub(/[[:space:]]*<br>[[:space:]]*/, "\n", cmd)
      n = split(cmd, arr, /\n/)
      for (i = 1; i <= n; i++) {
        c = arr[i]
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", c)
        gsub(/`/, "", c)
        if (c ~ /^(git clone|huggingface-cli download|kaggle competitions download)/) {
          print c
        }
      }
    }
  }
' "$REPORT_PATH" > "$tmp_commands"

  if [ "${FAILED_ONLY:-0}" = "1" ]; then
  if [ ! -s "$SUMMARY_FILE" ]; then
    echo "FAILED_ONLY requested but summary is empty or missing. Run full mode first." >> "$TRACE_FILE"
    exit 0
  fi
  awk -F',' 'NR>1 {
    gsub(/"/, "", $3)
    gsub(/`/, "", $3)
    sub(/^hf download/, "huggingface-cli download", $3)
    latest[$3] = $2
  }
  END {
    for (c in latest) {
      if (latest[c] != "ok" && latest[c] != "skip") print c
    }
  }' "$SUMMARY_FILE" > "$tmp_summary"
  awk 'NR==FNR {wanted[$0]=1; next} wanted[$0]' "$tmp_summary" "$tmp_commands" > "${tmp_commands}.filtered"
  mv "${tmp_commands}.filtered" "$tmp_commands"
  echo "Filter failed-only: $(wc -l < "$tmp_summary") candidates" >> "$TRACE_FILE"
  if [ ! -s "$tmp_commands" ]; then
    echo "Filter failed-only: no failed/unknown commands found." >> "$TRACE_FILE"
    exit 0
  fi
fi

total_cmds="$(wc -l < "$tmp_commands")"
echo "Prepared commands: $total_cmds" >> "$TRACE_FILE"

while IFS= read -r cmd; do
  [ -z "$cmd" ] && continue
  original_cmd="$cmd"
  if [[ "$cmd" == "huggingface-cli download"* ]]; then
    if command -v hf >/dev/null 2>&1; then
      cmd="${cmd/huggingface-cli download/hf download}"
    fi
  fi
  if [[ "$cmd" == git*https://gitee.com/* ]]; then
    cmd="${cmd/https://gitee.com\//git@gitee.com:}"
  fi
  dataset_path="$(printf '%s' "$cmd" | awk '{print $NF}')"
  log_cmd="$(normalize_cmd "$original_cmd")"
  ts=$(date -Iseconds)
  echo "[$ts] START $dataset_path: $log_cmd" >> "$TRACE_FILE"

  if [ -d "$dataset_path" ]; then
    case "$cmd" in
      git*)
        if [ -f "$dataset_path/.git/HEAD" ] && git -C "$dataset_path" rev-parse --verify HEAD >/dev/null 2>&1; then
          echo "$ts,skip,\"$log_cmd\",0" >> "$SUMMARY_FILE"
          echo "[$ts] SKIP existing $dataset_path" >> "$TRACE_FILE"
          continue
        fi
        rm -rf "$dataset_path"
        ;;
      *)
        if [ -n "$(ls -A "$dataset_path" 2>/dev/null)" ]; then
          echo "$ts,skip,\"$log_cmd\",0" >> "$SUMMARY_FILE"
          echo "[$ts] SKIP existing $dataset_path" >> "$TRACE_FILE"
          continue
        fi
        rmdir "$dataset_path" 2>/dev/null || true
        ;;
    esac
  fi
  if [ -f "$dataset_path/.git/shallow.lock" ]; then
    rm -f "$dataset_path/.git/shallow.lock"
  fi

  set +e
  timeout "$COMMAND_TIMEOUT" bash -lc "$cmd"
  rc=$?
  set -e
  ts=$(date -Iseconds)

  if [ $rc -eq 0 ]; then
    echo "$ts,ok,\"$log_cmd\",$rc" >> "$SUMMARY_FILE"
    echo "[$ts] OK $dataset_path" >> "$TRACE_FILE"
  else
    echo "$ts,fail,\"$log_cmd\",$rc" >> "$SUMMARY_FILE"
    echo "[$ts] FAIL $dataset_path (code=$rc)" >> "$TRACE_FILE"
  fi
done < "$tmp_commands"
