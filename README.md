# Quant Research Notes

Knowledge base and roadmap for the PureSaber quant research monorepo (local workspace).

## Contents

| Doc | Description |
|-----|-------------|
| [roadmap.md](roadmap.md) | Learning path and project phases |
| [repos.md](repos.md) | Repository map and dependencies |
| [pitfalls.md](pitfalls.md) | Common backtest / ML mistakes |
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

## Conventions

- Config: YAML under `configs/`
- Outputs: gitignored under `outputs/` or `output/`
- CLI: `pip install -e .` then project-specific commands
- Tests: `pytest -q` before push
