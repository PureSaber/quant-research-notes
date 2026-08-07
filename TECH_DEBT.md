# Technical Debt Register — quant-agent & quant-pipeline

**Review date:** 2026-08-07  
**Last audit:** 2026-08-07 (local stack audit)  
**Scope:** `quant-agent`, `quant-pipeline`, cross-stack CI  
**Focus:** Security and maintainability

---

## Summary

| Package | Critical | High | Medium | Low |
|---------|----------|------|--------|-----|
| quant-pipeline | 0 | 1 | 3 | 2 |
| quant-agent | 0 | 2 | 4 | 3 |
| Cross-cutting (viz) | — | 1 | 1 | 1 |

---

## Closed (2026-08-07 audit)

| ID | Fix |
|----|-----|
| **C-01** | `quant-pipeline`: default `shell=False`; per-step `shell: true` in YAML; optional `error_log_dir` writes full failure logs |
| **C-02** | `quant-agent`: spread projects skip IC rules; `check_spread_performance()` reads `performance/summary.csv` |
| **H-01** | `quant-pipeline[workspace]` optional extra in `pyproject.toml`; clear ImportError when missing |
| **M-03** | Spread vs equity rule routing in `run_all_rules()` |
| **M-06** | Failure logs written when `error_log_dir` set in pipeline YAML |
| **M-07** | `_resolve_notes_root()` uses `QUANT_WORKSPACE_ROOT` and walks for `quant-research-notes` |
| **M-05** | CLI: offline by default; `--llm` enables online mode |
| **CI** | `spread-backtest-viz`, `currency-converter` added `ci.yml`; `health-check.ps1` uses `QUANT_WORKSPACE_ROOT` |

---

## Critical

_(none open)_

---

## High

### H-02 — LLM nodes send full context externally

No redaction / opt-in policy when `--llm` is enabled.

**Fix:** `llm.send_paths: false`, require `QUANT_AGENT_LLM_OK=1`, document data policy.

### H-03 — Dead / ignored config keys

`temperature`, `rules.flag_nan_factors`, `enable_llm` partially wired.

### H-04 — ~87% duplication spread-backtest-viz ↔ quant-report-hub

See `quant-report-hub/docs/MERGE_PLAN.md`.

---

## Medium (selected)

- **M-01** No config schema validation (both packages)
- **M-02** `_expand()` format-string fragility in pipeline runner (KeyError on missing keys — documented; tests added)
- **M-04** Unbounded file reads in adapters

---

## Local workspace (Desktop)

Clone siblings under `C:\Users\ASUS\Desktop\quant_projects` and set:

```powershell
$env:QUANT_WORKSPACE_ROOT = "C:\Users\ASUS\Desktop\quant_projects"
```

Use `quant-workspace/configs/desktop.workspace.yaml` or env override. Run stack health:

```powershell
cd quant-infra-workspace
powershell -File scripts/health-check.ps1
```

---

## Priority order

1. H-04 — Viz merge (see MERGE_PLAN)
2. H-02 — LLM data policy
3. H-03 — Wire or remove dead config keys
4. M-01 — Pipeline/agent config schema validation
