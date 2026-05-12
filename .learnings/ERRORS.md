# Errors

## [ERR-20260512-001] parallel_dependent_commands

**Logged**: 2026-05-12T11:29:40+08:00  
**Priority**: low  
**Status**: pending  
**Area**: workflow

### Summary
Ran a dependent read command in parallel with the command that generated the file.

### Error
```text
sed: can't read pilot_runs/run_manifest.csv: No such file or directory
```

### Context
- Attempted to generate `pilot_runs/run_manifest.csv` and read it in the same parallel tool call.
- The read raced ahead before the writer finished.

### Suggested Fix
Do not use parallel tool calls for dependent file generation and inspection. Run generation first, then inspect in a separate command.

### Metadata
- Reproducible: yes
- Related Files: scripts/make_run_manifest.py, pilot_runs/run_manifest.csv

---

## [ERR-20260512-003] validator_check_missing_errors_argument

**Logged**: 2026-05-12T14:12:49+08:00  
**Priority**: low  
**Status**: fixed  
**Area**: scripting

### Summary
Added `check(...)` calls to `scripts/validate_pilot_artifacts.py` without passing the shared `errors` list.

### Error
```text
TypeError: check() missing 1 required positional argument: 'errors'
```

### Context
- While adding expert review archive validation, two new `check(...)` calls were written with only condition and message.
- The local helper signature is `check(condition, message, errors)`.

### Suggested Fix
When extending validators that use accumulator helpers, run the validator immediately after patching and ensure every helper call passes the accumulator argument.

### Metadata
- Reproducible: yes
- Related Files: scripts/validate_pilot_artifacts.py

---

## [ERR-20260512-002] csv_dictreader_fieldnames_access

**Logged**: 2026-05-12T12:44:00+08:00  
**Priority**: low  
**Status**: fixed  
**Area**: scripting

### Summary
Accessed `fieldnames` on the file handle instead of the `csv.DictReader` while filling a synthetic blind score sheet in the smoke test.

### Error
```text
Pilot pipeline smoke test failed: '_io.TextIOWrapper' object has no attribute 'fieldnames'
```

### Context
- `scripts/smoke_test_pilot_pipeline.py` added a `fill_blind_score_sheet` helper.
- The code created `rows = list(csv.DictReader(handle))` and then read `handle.fieldnames`, but `fieldnames` belongs to the reader object.

### Suggested Fix
Keep a `reader = csv.DictReader(handle)` variable and read `reader.fieldnames` before writing the updated CSV.

### Metadata
- Reproducible: yes
- Related Files: scripts/smoke_test_pilot_pipeline.py

---
## [ERR-20260512-004] shell_backtick_in_rg_pattern

**Logged**: 2026-05-12T17:21:56+08:00  
**Priority**: low  
**Status**: pending  
**Area**: workflow

### Summary
Ran an `rg` command with a double-quoted pattern containing backticks, causing shell command substitution before ripgrep executed.

### Error
```text
/bin/bash: line 1: --require-complete: command not found
```

### Context
- Attempted to search docs for text containing `` `--require-complete` ``.
- Because the shell command was double-quoted, the backticked text was interpreted as command substitution.

### Suggested Fix
When searching for text that contains backticks, wrap the search pattern in single quotes or escape the backticks.

### Metadata
- Reproducible: yes
- Related Files: README.md, final_report_2026-05-12.md

---
