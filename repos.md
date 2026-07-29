# Repository Map

| Repo | Role | Key CLI |
|------|------|---------|
| quant-workspace | Central path resolver | `quant-workspace show/path/lab-config` |
| quant-pipeline | Post-run orchestration | `quant-pipe run` |
| quant-factors | Shared factor library | `quant-factors compute/list` |
| quant-portfolio | Multi-strategy allocator | `quant-portfolio status` |
| quant-agent | Post-run QA review | `quant-review run` |
| currency-converter | FX utility / warmup | `python -m currency_converter` |
| sklearn-stock-trend | ML trend prediction | `st-train`, `st-walkforward` |
| a-share-multifactor | Multi-factor equity research | `asm-fetch`, `asm-backtest` |
| quant-data-kit | Shared data layer + catalog | `qdk-validate`, `qdk-catalog list` |
| quant-lab | Experiment index + HTML dashboard | `quant-lab scan/export html` |
| quant-report-hub | Charts (spread + equity) | `quant-report run` |
| quant-regime | Market regime detector | `quant-regime detect`, `detect-multi` |
| quant-risk-monitor | Portfolio risk alerts | `quant-risk check` |
| quant-paper-sim | Paper trading simulator | `quant-paper step` |
| quant-futures-spread | Futures spread engine (private) | `qfs-backtest`, `run_backtest.py` |
| spread-backtest-viz | Legacy spread viz (unchanged) | `spread-viz run` |

Local path for futures: `future_spread_analysis-team-framework`

See also [run-contract.md](run-contract.md).

## Dependency direction

```text
quant-workspace ── resolves paths ──► quant-lab / quant-pipeline / quant-portfolio

quant-data-kit ──► a-share-multifactor
                 └► sklearn-stock-trend
                 └► qdk-catalog

quant-factors ── optional input ──► research engines

quant-lab ── reads ──► */outputs/ + review_manifest.json

quant-agent ── reads ──► run outputs ── writes ──► review_manifest.json

quant-pipeline ── orchestrates ──► regime → paper → risk → lab → html

quant-regime detect-multi ──► position_scale JSON ──► quant-paper-sim / quant-portfolio

quant-paper-sim ── writes ──► state/holdings.csv, state/nav.csv
quant-risk-monitor ── reads ──► capital_curves.csv, paper sim holdings, spread NAV
quant-portfolio ── reads ──► strategy nav/holdings
```

## GitHub

- https://github.com/PureSaber/quant-workspace
- https://github.com/PureSaber/quant-pipeline
- https://github.com/PureSaber/quant-factors
- https://github.com/PureSaber/quant-portfolio
- https://github.com/PureSaber/quant-agent
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
