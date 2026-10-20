# Technical Debt Register — quant-agent & quant-pipeline

**Review date:** 2026-09-01
**Last audit:** 2026-09-01 (GitHub governance and lifecycle audit)
**Targeted source refresh:** 2026-10-19 (`quant-agent` `a3b5ff39d7b78dd4f423214b8077de31d83c07b7`)
**Scope:** `quant-agent`, `quant-pipeline`, cross-stack CI  
**Focus:** Security and maintainability

---

## Summary

The counts below are the historical 2026-09-01 inventory, not current open-item
counts. The 2026-10-19 refresh checks H-02 and the named H-03 configuration paths
only; it is not a new complete security audit.

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
| **H-04** | Visualization implementation consolidated in `quant-report-hub`; `spread-backtest-viz` reduced to a tested compatibility shim, passed Python3.10/3.11/3.12 CI, received exact recovery/compatibility tags under explicit authorization, and was archived read-only on 2026-09-05. |

---

## Critical

_(none open)_

---

## High

### H-02 — Explicit opt-in and default path redaction implemented

The original missing-control finding is closed for the reviewed source:
`llm_enabled()` requires both `enable_llm` and `QUANT_AGENT_LLM_OK=1`;
`_llm_user_payload()` defaults `llm.send_paths` to false. The shared LLM draft
node checks the gate before invocation. Evidence:
[`nodes/pipeline.py`](https://github.com/PureSaber/quant-agent/blob/a3b5ff39d7b78dd4f423214b8077de31d83c07b7/src/quant_agent/nodes/pipeline.py),
[`DATA_POLICY.md`](https://github.com/PureSaber/quant-agent/blob/a3b5ff39d7b78dd4f423214b8077de31d83c07b7/docs/DATA_POLICY.md), and
[`test_llm_policy.py`](https://github.com/PureSaber/quant-agent/blob/a3b5ff39d7b78dd4f423214b8077de31d83c07b7/tests/test_llm_policy.py).

This redacts the explicit run-directory field, not arbitrary secrets embedded
in findings or source text. Authorized online review still sends its documented
context. No claim of comprehensive content sanitization or online-model quality
is made.

### H-03 — Dead / ignored config keys

`temperature` is passed to `ChatOpenAI` by the shared draft node, and
`enable_llm` participates in the explicit opt-in gate. They are no longer
unwired findings at the reviewed commit. `rules.flag_nan_factors` remains an
open configuration-wiring item; no implementation read of this key was found
outside the default configuration. Full rule/configuration consistency remains
to be reviewed.

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

1. H-03 — Wire or remove the remaining `rules.flag_nan_factors` key
2. M-01 — Review remaining pipeline/agent config schema coverage
3. Retain H-02 opt-in/path-redaction regression coverage and review any newly
   added outbound context separately
