# Technical Debt Register — quant-agent & quant-pipeline

**Review date:** 2026-08-07  
**Scope:** `quant-agent`, `quant-pipeline`  
**Focus:** Security and maintainability

---

## Summary

| Package | Critical | High | Medium | Low |
|---------|----------|------|--------|-----|
| quant-pipeline | 1 | 2 | 4 | 2 |
| quant-agent | 1 | 3 | 5 | 3 |
| Cross-cutting (viz) | — | 1 | 2 | 1 |

---

## Critical

### C-01 — Shell command injection via YAML pipeline configs

**Package:** quant-pipeline  
**Files:** `src/quant_pipeline/runner.py`

`run_step()` uses `subprocess.run(..., shell=True)` with commands from YAML after env expansion. Treat pipeline YAML as trusted; prefer `shell=False` with argv lists.

**Fix:** Replace `shell=True` with explicit argv; optional `allow_shell: true` per step; JSON Schema validation.

### C-02 — Futures-spread reviews always fail deterministic rules

**Package:** quant-agent  
**Files:** `rules/engine.py`, `adapters/futures_spread.py`

`check_ic_quality()` errors when `ic_summary` is empty; spread adapter always returns empty IC → exit code 2.

**Fix:** Gate rules by adapter capability; add spread-specific rules from `performance/summary.csv`.

---

## High

### H-01 — `quant-workspace` undeclared runtime dependency

`quant-pipeline` imports `quant_workspace` when `workspace:` is set but does not declare the dependency in `pyproject.toml`.

**Fix:** Add optional extra `quant-pipeline[workspace]` or hard dependency.

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
- **M-02** `_expand()` format-string fragility in pipeline runner
- **M-03** Project-agnostic rule engine (multifactor rules on spread)
- **M-04** Unbounded file reads in adapters
- **M-05** Confusing `--offline` CLI semantics
- **M-06** Pipeline observability (stdout discarded)
- **M-07** Hardcoded monorepo path in `_resolve_notes_root`

---

## Priority order

1. C-02 — Unblock futures-spread reviews
2. C-01 — Harden pipeline execution
3. H-01 — Declare quant-workspace dependency
4. H-04 — Viz merge (see MERGE_PLAN)
5. H-02 — LLM data policy

Full review notes in agent transcript; update as items are closed.
