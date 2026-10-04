# Repository Map

更新时间：2026-10-04。当前维护范围为23个核心仓库；下面同时保留学习工具、历史工作区和已归档兼容层。
核心范围与M8的14仓不可变发布清单不同：新增研究项目及默认分支更新不会自动获得M8发布认证。

[机器可读能力清单](https://github.com/PureSaber/quant-workspace/blob/main/src/quant_workspace/capabilities.json)列出23仓的资产、功能、接口、数据状态、缺口和关系。[开发配置](https://github.com/PureSaber/quant-workspace/blob/main/configs/platform.workspace.yaml)与14仓发行配置分开；`quant-workspace capabilities --inventory`只能核验源码、提交和证据文件存在性，不能替代环境、跨仓业务或市场数据认证。

| Repo | Role | Key CLI |
|------|------|---------|
| quant-workspace | 路径解析、23仓能力清单、源码盘点及不可变发布门禁 | `quant-workspace show/path/capabilities/lab-config` |
| [quant-studio](https://github.com/PureSaber/quant-studio) | 本机统一总览、十一模板与十个业务预检入口、显式运行、只读前向账户、原生事件账本及择时分折/发布展示 | `python -m quant_studio serve/check` |
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
| [quant-fund](https://github.com/PureSaber/quant-fund) | 基金研究、场外申赎模拟和FOF监控；已有真实净值小样本，完整条款、分红和分用途日历仍未闭合 | `python -m quant_fund.cli`、`streamlit run app.py` |
| [quant-stat-arb](https://github.com/PureSaber/quant-stat-arb) | 统计套利研究（private）、原生只读预检和Studio配置文件入口；不属于既有M8认证范围 | `python -m quant_stat_arb preflight/run` |
| [quant-timing](https://github.com/PureSaber/quant-timing) | 指数仓位和风格择时研究；原生只读预检、因果回放、发布门禁、分折及账本归因；Studio已接入。固定仓位/风格反事实已接入Studio，核验完整候选族与原生文件集合，候选禁发仓位 | `python -m quant_timing preflight/run/compare` |
| quant-data-kit | Shared data layer + catalog | `qdk-validate`, `qdk-catalog list` |
| quant-lab | Experiment index + HTML dashboard | `quant-lab scan/export html` |
| quant-report-hub | 图表、账本及反事实归因；独立报价的有符号成交价差和原生重算 | `quant-report run/cash-price-bridge/verify-cash-price-bridge` |
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

当前功能、研究进度、视觉与操作体验、资产成熟度及后续工作见[2026-10-03平台进展](validation/p0-p2-20261003/README.md)。五个新增应用已完成七份实际产物的跨仓消费与损坏拒绝验收；这种验收不提升市场数据或策略有效性状态。

## Dependency direction

```text
quant-workspace ── resolves paths ──► quant-lab / quant-pipeline / quant-portfolio

quant-studio ── declared templates / CLI ──► a-share-multifactor / quant-hk-equity / quant-paper-sim
             ├─ native preflight / CLI ──► quant-fund / quant-us-equity
             ├─ offline fixture / native ledger views ──► quant-futures-spread / quant-crypto-basis
             ├─ research config file / native preflight ──► quant-stat-arb
             ├─ research config / verified folds and publication ──► quant-timing
             └─ read-only account inspection ──► quant-pipeline

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

quant-hk-equity ── standard/v1 + exploratory standard/v2 ──► quant-lab
quant-us-equity / quant-fund ── exploratory standard/v2 ──► quant-lab
quant-timing / quant-stat-arb ── standard/v1研究列约定 ──► 需逐链路消费验收

quant-agent ── reads ──► run outputs ── writes ──► review_manifest.json

quant-pipeline ── orchestrates ──► regime → paper → risk → lab → html

quant-regime detect-multi ──► position_scale JSON ──► quant-paper-sim / quant-portfolio

quant-paper-sim ── writes ──► state/holdings.csv, state/nav.csv
quant-risk-monitor ── reads ──► capital_curves.csv, paper sim holdings, spread NAV
quant-portfolio ── reads ──► strategy nav/holdings
                 └─ optimization/capacity ──► target weights

quant-risk-monitor ── VaR/CVaR/stress/liquidity/factor risk ──► alerts + metrics
```

探索性v2导出表示产物接口已适配，不等于执行认证或真实公司行动证据完整。港股现有真实研究仍为价格收益；美股价格链、基金完整业务资料以及独立前向结果仍有缺口。当前推进清单见[P0—P2验收计划](validation/p0-p2-20261003/PLAN.md)。

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
