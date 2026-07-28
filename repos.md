# Repository Map

| Repo | Role | Key CLI |
|------|------|---------|
| currency-converter | FX utility / warmup | `python -m currency_converter` |
| sklearn-stock-trend | ML trend prediction | `st-train`, `st-walkforward` |
| a-share-multifactor | Multi-factor equity research | `asm-fetch`, `asm-backtest` |
| quant-data-kit | Shared data layer | `qdk-validate` |
| quant-lab | Experiment index | `quant-lab scan/list/compare` |
| quant-report-hub | Charts (spread + equity) | `quant-report run` |
| quant-regime | Market regime detector | `quant-regime detect` |
| quant-risk-monitor | Portfolio risk alerts | `quant-risk check` |
| quant-paper-sim | Paper trading simulator | `quant-paper step` |
| quant-futures-spread | Futures spread engine (private) | `qfs-backtest`, `run_backtest.py` |
| spread-backtest-viz | Legacy spread viz (unchanged) | `spread-viz run` |

Local path for futures: `future_spread_analysis-team-framework`

## Dependency direction

```text
quant-data-kit ──► a-share-multifactor
                 └► sklearn-stock-trend

quant-lab ── reads ──► */outputs/

quant-report-hub ── reads ──► future_spread/output/
                           └► */outputs/ (equity adapter)

quant-regime ──► position_scale JSON ──► quant-paper-sim / strategies
quant-paper-sim ── writes ──► state/holdings.csv, state/nav.csv
quant-risk-monitor ── reads ──► capital_curves.csv, paper sim holdings, spread NAV
```

## GitHub

- https://github.com/PureSaber/a-share-multifactor
- https://github.com/PureSaber/sklearn-stock-trend
- https://github.com/PureSaber/currency-converter
- https://github.com/PureSaber/quant-data-kit
- https://github.com/PureSaber/quant-lab
- https://github.com/PureSaber/quant-report-hub
- https://github.com/PureSaber/quant-research-notes
- https://github.com/PureSaber/quant-regime
- https://github.com/PureSaber/quant-risk-monitor
- https://github.com/PureSaber/quant-paper-sim
- https://github.com/PureSaber/quant-futures-spread (private)
