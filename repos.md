# Repository Map

| Repo | Role | Key CLI |
|------|------|---------|
| currency-converter | FX utility / warmup | `python -m currency_converter` |
| sklearn-stock-trend | ML trend prediction | `st-train`, `st-walkforward` |
| a-share-multifactor | Multi-factor equity research | `asm-fetch`, `asm-backtest` |
| quant-data-kit | Shared data layer | `qdk-validate` |
| quant-lab | Experiment index | `quant-lab scan/list/compare` |
| quant-report-hub | Charts (spread + equity) | `quant-report run` |
| spread-backtest-viz | Legacy spread viz (unchanged) | `spread-viz run` |
| future_spread_analysis-team-framework | Futures spread engine | project-specific |

## Dependency direction

```text
quant-data-kit ──► a-share-multifactor
                 └► sklearn-stock-trend

quant-lab ── reads ──► */outputs/

quant-report-hub ── reads ──► future_spread/output/
                           └► */outputs/ (equity adapter)
```

## GitHub

- https://github.com/PureSaber/a-share-multifactor
- https://github.com/PureSaber/sklearn-stock-trend
- https://github.com/PureSaber/currency-converter
- https://github.com/PureSaber/quant-data-kit (pending push)
- https://github.com/PureSaber/quant-lab (pending push)
- https://github.com/PureSaber/quant-report-hub (pending push)
- https://github.com/PureSaber/quant-research-notes (pending push)
