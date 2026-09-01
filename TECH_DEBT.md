# Technical Debt Register — quant-agent & quant-pipeline

**Review date:** 2026-09-01
**Last audit:** 2026-09-01 (GitHub governance and lifecycle audit)
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
| **H-04** | Visualization implementation consolidated in `quant-report-hub`; `spread-backtest-viz` reduced to a tested compatibility shim and passed Python3.10/3.11/3.12 CI. Archive and recovery-tag creation remain explicit owner decisions, not open duplication work. |

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

---

## Medium (selected)

- **M-01** No config schema validation (both packages)
- **M-02** `_expand()` format-string fragility in pipeline runner (KeyError on missing keys — documented; tests added)
- **M-04** Unbounded file reads in adapters

---

## Local workspace

Clone siblings under a workspace root and set:

```powershell
$env:QUANT_WORKSPACE_ROOT = "<workspace-root>"
```

Use `quant-workspace/configs/desktop.workspace.yaml` or env override. Run stack health:

```powershell
cd quant-infra-workspace
powershell -File scripts/health-check.ps1
```

---

## Priority order

1. H-02 — LLM data policy
2. H-03 — Wire or remove dead config keys
3. M-01 — Pipeline/agent config schema validation
