# Repository Map

| Repo | Role | Key CLI |
|------|------|---------|
| quant-workspace | Central path resolver | `quant-workspace show/path/lab-config` |
| quant-pipeline | Post-run orchestration | `quant-pipe run` |
| quant-factors | Shared factor library | `quant-factors compute/list` |
| quant-portfolio | Multi-strategy allocator | `quant-portfolio status` |
| quant-agent | Post-run QA review | `quant-review run` |
| quant-execution | Deterministic execution, risk gate, matching and exact ledger | library API |
| quant-crypto-basis | Fixture-certified crypto basis research | project CLI |
| currency-converter | FX utility / warmup | `python -m currency_converter` |
| sklearn-stock-trend | ML trend prediction | `st-train`, `st-walkforward` |
| a-share-multifactor | Multi-factor equity research | `asm-fetch`, `asm-backtest` |
| quant-data-kit | Shared data layer + catalog | `qdk-validate`, `qdk-catalog list` |
| quant-lab | Experiment index + HTML dashboard | `quant-lab scan/export html` |
| quant-report-hub | Charts (spread + equity) | `quant-report run` |
| quant-regime | Market regime detector | `quant-regime detect`, `detect-multi` |
| quant-risk-monitor | Portfolio risk alerts | `quant-risk check` |
| quant-paper-sim | Paper trading simulator | `quant-paper step` |
| quant-futures-spread | Public fixture-certified futures spread engine | `qfs-certified-backtest`, `run_backtest.py` |
| quant-infra-workspace | Private cross-repository health and governance workspace | `scripts/health-check.ps1` |
| research-workspace | Cross-product arb research (TaskSolver) | `scripts/run_backtest.py` |
| spread-backtest-viz | Deprecated compatibility shim；technical archive readiness complete，approval pending | `spread-viz run` |

Local path for futures: `quant-futures-spread` (sibling under workspace root)

## Architecture docs

| Doc | Location |
|-----|----------|
| Stack dependency graph | This file (below) |
| research-workspace data flow | [research-workspace/docs/ARCHITECTURE.md](https://github.com/PureSaber/research-workspace/blob/main/docs/ARCHITECTURE.md) |
| Tech debt register | [TECH_DEBT.md](TECH_DEBT.md) |
| Viz merge plan | [quant-report-hub/docs/MERGE_PLAN.md](https://github.com/PureSaber/quant-report-hub/blob/main/docs/MERGE_PLAN.md) |
| Workspace maintenance log | [quant-infra-workspace/docs/OPTIMIZATION_LOG.md](https://github.com/PureSaber/quant-infra-workspace/blob/main/docs/OPTIMIZATION_LOG.md) |

See also [run-contract.md](run-contract.md).

## Dependency direction

```text
quant-workspace ── resolves paths ──► quant-lab / quant-pipeline / quant-portfolio

quant-data-kit ──► a-share-multifactor / quant-futures-spread / quant-crypto-basis
                 └► sklearn-stock-trend
                 └► qdk-catalog

quant-execution ── deterministic fills/ledger ──► certified research engines

quant-factors ── validation/factors ──► research engines

research engines ── writes standard/v2 ──► quant-lab
                                            └► quant-report-hub attribution

quant-agent ── reads ──► run outputs ── writes ──► review_manifest.json

quant-pipeline ── orchestrates ──► regime → paper → risk → lab → html

quant-regime detect-multi ──► position_scale JSON ──► quant-paper-sim / quant-portfolio

quant-paper-sim ── writes ──► state/holdings.csv, state/nav.csv
quant-risk-monitor ── reads ──► capital_curves.csv, paper sim holdings, spread NAV
quant-portfolio ── reads ──► strategy nav/holdings
                 └─ optimization/capacity ──► target weights

quant-risk-monitor ── VaR/CVaR/stress/liquidity/factor risk ──► alerts + metrics
```

## GitHub

- https://github.com/PureSaber/quant-workspace
- https://github.com/PureSaber/quant-pipeline
- https://github.com/PureSaber/quant-factors
- https://github.com/PureSaber/quant-portfolio
- https://github.com/PureSaber/quant-agent
- https://github.com/PureSaber/quant-execution
- https://github.com/PureSaber/quant-crypto-basis
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
- https://github.com/PureSaber/quant-futures-spread
- https://github.com/PureSaber/quant-infra-workspace (private)
- https://github.com/PureSaber/spread-backtest-viz (deprecated shim; archive approval pending)
