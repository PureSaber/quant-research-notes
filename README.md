# Quant Research Notes

Knowledge base and roadmap for the PureSaber quant research monorepo (local workspace).

## Contents

| Doc | Description |
|-----|-------------|
| [roadmap.md](roadmap.md) | Learning path and project phases |
| [repos.md](repos.md) | Repository map and dependencies |
| [TECH_DEBT.md](TECH_DEBT.md) | Security / maintainability debt register |
| [pitfalls.md](pitfalls.md) | Common backtest / ML mistakes |
| [research-integrity-v1.md](research-integrity-v1.md) | PIT data, validation, run contract, risk and attribution standard |
| [experiment-log/](experiment-log/) | Short summaries of important runs |

## Repo stack (2026-07)

```text
currency-converter        → Python CLI warmup
sklearn-stock-trend       → supervised learning + walk-forward
a-share-multifactor       → factor IC + quantile + retail backtest
quant-data-kit            → shared AKShare + Parquet + validation
quant-lab                 → cross-project experiment index
quant-report-hub          → unified charts (spread + equity adapters)
spread-backtest-viz       → legacy futures viz (frozen reference)
future_spread_analysis    → futures spread backtest engine
```

## Local workspace (Desktop)

Clone sibling repos under `C:\Users\ASUS\Desktop\quant_projects` and set:

```powershell
$env:QUANT_WORKSPACE_ROOT = "C:\Users\ASUS\Desktop\quant_projects"
```

Use `quant-workspace/configs/desktop.workspace.yaml` for path resolution. Stack health:

```powershell
cd quant-infra-workspace
powershell -File scripts/health-check.ps1
```

## Conventions

- Config: YAML under `configs/`
- Outputs: gitignored under `outputs/` or `output/`
- CLI: `pip install -e .` then project-specific commands
- Tests: `pytest -q` before push

