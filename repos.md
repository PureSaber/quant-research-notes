# Repository Map

更新时间：2026-09-30。当前维护范围为23个核心仓库；下面同时保留学习工具、历史工作区和已归档兼容层。
核心范围与M8的14仓不可变发布清单不同：新增研究项目及默认分支更新不会自动获得M8发布认证。

| Repo | Role | Key CLI |
|------|------|---------|
| quant-workspace | Central path resolver | `quant-workspace show/path/lab-config` |
| [quant-studio](https://github.com/PureSaber/quant-studio) | 本机模板操作台；先预览配置，再显式执行A股、港股或模拟盘工具 | `python -m quant_studio serve` |
| quant-pipeline | Post-run orchestration | `quant-pipe run` |
| quant-factors | Shared factor library | `quant-factors compute/list` |
| quant-portfolio | Multi-strategy allocator | `quant-portfolio status` |
| quant-agent | Post-run QA review | `quant-review run` |
| quant-execution | Deterministic execution, risk gate, matching and exact ledger | library API |
| quant-crypto-basis | Fixture-certified crypto basis research | project CLI |
| currency-converter | FX utility / warmup | `python -m currency_converter` |
| sklearn-stock-trend | ML trend prediction | `st-train`, `st-walkforward` |
| a-share-multifactor | Multi-factor equity research | `asm-fetch`, `asm-backtest` |
| [quant-hk-equity](https://github.com/PureSaber/quant-hk-equity) | 港股日频现金账户探索；真实行情、滞后信号、整手税费、训练/留出期；价格收益，未获可投资认证 | `quant-hk fetch/preflight/run` |
| [quant-us-equity](https://github.com/PureSaber/quant-us-equity) | 美股研究扩展（private）；不属于既有M8认证范围 | 入口与证据见授权仓库 |
| [quant-fund](https://github.com/PureSaber/quant-fund) | 基金研究、场外申赎模拟和FOF组合监控；当前验收使用合成基金 | `python -m quant_fund.cli`、`streamlit run app.py` |
| [quant-stat-arb](https://github.com/PureSaber/quant-stat-arb) | 统计套利研究扩展（private）；不属于既有M8认证范围 | 入口与证据见授权仓库 |
| [quant-timing](https://github.com/PureSaber/quant-timing) | 指数仓位和风格择时研究；按因果时点回放并保留样本外门禁 | `python -m quant_timing run/compare` |
| quant-data-kit | Shared data layer + catalog | `qdk-validate`, `qdk-catalog list` |
| quant-lab | Experiment index + HTML dashboard | `quant-lab scan/export html` |
| quant-report-hub | Charts (spread + equity) | `quant-report run` |
| quant-regime | Market regime detector | `quant-regime detect`, `detect-multi` |
| quant-risk-monitor | Portfolio risk alerts | `quant-risk check` |
| quant-paper-sim | Paper trading simulator | `quant-paper step` |
| quant-futures-spread | Public fixture-certified futures spread engine | `qfs-certified-backtest`, `run_backtest.py` |
| quant-infra-workspace | Private cross-repository health and governance workspace | `scripts/health-check.ps1` |
| quant-research-notes | 仓库地图、研究边界、治理及验收证据索引 | Markdown与`contracts/m8` |
| research-workspace | Cross-product arb research (TaskSolver) | `scripts/run_backtest.py` |
| spread-backtest-viz | Deprecated compatibility shim；2026-09-05已归档为只读 | `spread-viz run` |

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

日常源码目录、固定提交的集成环境、冻结研究账户分别管理，见[工作区维护说明](WORKSPACE_GUIDE.md)。
M8真实市场门禁以[M8状态](validation/m8/M8_STATUS.md)和[M9里程碑](https://github.com/PureSaber/quant-research-notes/milestone/1)为准。

## Dependency direction

```text
quant-workspace ── resolves paths ──► quant-lab / quant-pipeline / quant-portfolio

quant-studio ── declared templates / CLI ──► a-share-multifactor / quant-hk-equity / quant-paper-sim

quant-fund ── independent fund research / OTC ledger ──► read-only integration snapshot
quant-timing ── validated position_scale ──► quant-paper-sim / quant-portfolio configuration

quant-data-kit ──► a-share-multifactor / quant-futures-spread / quant-crypto-basis
                 └► quant-hk-equity（同时复用quant-factors与quant-execution）
                 └► sklearn-stock-trend
                 └► qdk-catalog

quant-execution ── deterministic fills/ledger ──► certified research engines

quant-factors ── validation/factors ──► research engines

research engines ── writes standard/v2 ──► quant-lab
                                            └► quant-report-hub attribution

quant-hk-equity ── exploratory standard/v1 ──► quant-lab

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
- https://github.com/PureSaber/quant-hk-equity
- https://github.com/PureSaber/quant-us-equity (private)
- https://github.com/PureSaber/quant-fund
- https://github.com/PureSaber/quant-stat-arb (private)
- https://github.com/PureSaber/quant-timing
- https://github.com/PureSaber/quant-studio
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
- https://github.com/PureSaber/spread-backtest-viz (deprecated shim; archived read-only)
