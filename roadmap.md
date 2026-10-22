# Learning Roadmap

## 当前推进范围：采纳业务评审（2026-10-22）

按 [业务决定与验收顺序](BUSINESS_DIRECTION_20261022.md) 推进四 ETF 数据与研究、原账户
工程验收和已验证的软件缺陷修复。Portfolio #32 与 Risk Monitor #34 已合并；#37 暂缓。
原账户仍未获继续权限、自然验收 0/6，原研究与冻结环境保留。工作台已完成本机升级；
新增决策摘要另见 Studio #53，不能把代码提交等同于部署或自然运行。
长历史采集已发现真实停牌和 510500 拆分，补齐类型化历史规则及公司行动证据后才准入。

## 历史推进范围：ETF 每日运行与故障恢复（2026-10-16）

先完善已有冻结 ETF 模拟账户的每日运行，再同步能力清单、路线图和交付状态。顺序为：保存基线并核查原账户续跑条件 → 独立运维层与恢复预览 → Windows 调度和中文状态页 → 固定环境安装、测试与备份恢复 → 六个连续真实交易日验收。

账户 `etf-base-20261014` 的资金、参数、原观察窗口和冻结执行代码保持不变。10 月 15 日缺口保留，不补造历史成交。若原生规则不允许继续，保持自动写入停用；软件交付和自然运行验收分别报告。具体进度见 [ETF 运维交付](ETF_OPERATIONS_DELIVERY.md)。

不增加新策略、新资产、完整 Barra 或实盘接口。下面的暂停说明属于较早账户和当时状态，不能用于推断本次 Windows 任务或当前账户状态。

当前进度：独立运维层、恢复预览、中文页面、Windows 任务定义、上一候选本机安装、测试及服务升级回退已通过。10 月 17 日审查补上“关联已有账本不计新的自然成功”的修正，回归通过，修正待安装。业务任务保持停用，原账户续跑仍受当前合格资料缺失阻塞。下一步验证修正安装、恢复资料可用性并完成原生续跑核查，再启用业务和开始六交易日验收。管理员开启任务事件历史、下一次自然登录确认分别跟踪。四仓 GitHub 交付已授权，本次按用户要求不运行 CI；现有主分支 CI 保护与合并状态独立记录。

## 历史推进范围：低频平台维护（2026-10-07）

近期先完成界面与操作体验、低频时间及账本一致性、跨仓兼容和代码运维。本批依赖维护、报告独立入口与文档同步已交付，四只真实公募13386条净值完成分红再投资修复和独立复核；A股完整历史PIT输入、基金真实业务资料及新的视觉验收仍缺。逐项证据见[低频后续验收](validation/p0-p2-20261003/LOW_FREQUENCY_FOLLOW_THROUGH.md)。

原ETF自动化仍为`PAUSED`，本批没有恢复或新增自然前向。完整纳秒贯通是可选兼容工作；大归档、Crypto连续30日、国内授权L2、完整Barra和实盘按原暂缓或外部条件状态保留。旧P0—P2总目标仍在进行中，市场数据GA未通过。

## 历史阶段：轻量真实行情验证（2026-10-03）

按用户确认，近期只要求证明小规模真实市场数据链路正常，暂缓完整市场数据建设。固定四ETF日线的两次真实采集、覆盖与数值检查、文件哈希及下游输入验收已通过，两个快照及数据目录索引共572294字节，未新增运行环境。范围、限制和复核步骤见[当前验收说明](validation/maintenance-20261001/RESOURCES.md#当前阶段轻量真实行情验收)，机器证据见[acceptance.json](validation/light-market-data-20261003/acceptance.json)。

当时计划在原r4登记窗口继续四ETF日频观察，复用已验收环境；当前执行状态以本页顶部2026-10-07维护范围及暂停状态为准。独立大容量归档、Crypto八流连续30日、授权国内L2和完整Barra数据列为后续阶段，不阻塞当时轻量交付；既有全市场认证仍未取得，历史认证标准和失败证据保持不变。

同日追加的全栈检查采用[轻量真实数据全栈验收规范](validation/light-market-data-20261003/STACK_POLICY.md)。已扩展到港股、基金、择时、市场状态和工作台，并分别记录期货/Crypto数据层探测与尚未覆盖的策略链路；美股限流及OKX超时保留为未通过。该追加检查为基金建立了独立锁定环境，因此上段“未新增运行环境”只描述最初四ETF数据验收，不代表全栈检查的总空间。

## Phase 0 — Engineering basics ✅

- [currency-converter](../currency-converter): CLI, config separation, pluggable providers, pytest

## Phase 1 — Supervised ML ✅

- [sklearn-stock-trend](../sklearn-stock-trend): features, labels, RF/XGB, walk-forward, purged CV, retail backtest

## Phase 2 — Factor research ✅

- [a-share-multifactor](../a-share-multifactor): IC, quantile backtest, synthesis (OLS/Ridge), param grid

## Phase 3 — Shared infrastructure ✅

- [quant-data-kit](../quant-data-kit): unified data fetch/cache/validate
- [quant-research-notes](README.md): this knowledge base
- [quant-lab](../quant-lab): experiment index across repos
- [quant-report-hub](../quant-report-hub): adapter-based visualization

## Phase 4 — Research Integrity v1 ✅

- Point-in-time data joins, historical universe, immutable snapshots and quality gates
- Walk-forward, purged CV, embargo, leakage audits and FDR correction
- Immutable standard backtest run contract for equity and futures spread engines
- Constrained optimization, covariance, capacity, liquidity, stress and tail risk
- Holdings/cost/factor/Brinson performance attribution

See [research-integrity-v1.md](research-integrity-v1.md).

## Phase 5 — Core software complete；ongoing governance

- [quant-futures-spread](https://github.com/PureSaber/quant-futures-spread): public fixture-certified futures spread research；backtest-only
- [quant-regime](../quant-regime): rule-based regime detector with position_scale + `detect-multi`
- [quant-risk-monitor](../quant-risk-monitor): drawdown / concentration / tail / stress / liquidity alerts
- [quant-paper-sim](../quant-paper-sim): paper trading simulator (signals → holdings → NAV)
- [quant-workspace](../quant-workspace): central path resolver
- [quant-pipeline](../quant-pipeline): post-run orchestration
- [quant-factors](../quant-factors): shared factor library
- [quant-portfolio](../quant-portfolio): constrained allocator and capacity model
- [quant-agent](https://github.com/PureSaber/quant-agent): post-run QA review layer
- Live execution adapter (vnpy/ssquant) — later

以上软件组件已经纳入M8内部发布与GitHub治理。这里的“complete”不表示真实市场数据GA或实盘批准；当前权威状态仍是`M8_SOFTWARE_RELEASE_COMPLETE / MARKET_DATA_GA_BLOCKED`，后续门禁由[M9 Market Data GA](https://github.com/PureSaber/quant-research-notes/milestone/1)跟踪。

## Phase 6 — Cross-Asset & Multi-Frequency v2

- [RFC](cross-asset-multifrequency-v2-rfc.md): instrument、symbol mapping、market clock、
  UTC双时间、固定点数和`standard/v2`契约
- M0—M6：默认分支收口、契约、数据、执行、三条纵向切片、组合风险归因和DAG治理均已完成并保留独立审计链
- M7软件/fixture：数据性能、执行性能和Crypto L2采集器软件门禁已通过独立验证
- M7合并就绪：`quant-workspace v0.3.0`、`quant-data-kit v0.7.4`和`quant-execution v0.5.0`已从默认分支通过独立验证、CI和组件tag发布
- M7真实市场：公共网络、连续30天、归档恢复及国内合法L2仍为外部/时间阻塞，不得宣称`market-data-certified`或`v2.0 GA`
- M8全频率研究层与全栈软件发布：显式频率/年化、Curated Bar与Normalized事件认证输入、逐行`as_of`、PIT血缘、规范hash、三条纵向切片、统一执行、组合风险及14仓不可变release manifest均已完成并通过独立复核
- 当前状态与证据：[validation/m8/M8_STATUS.md](validation/m8/M8_STATUS.md)；真实市场数据阻塞沿革保留于[validation/m7/M7_STATUS.md](validation/m7/M7_STATUS.md)

## Skills checklist

- [ ] Can explain IC vs Rank IC
- [x] Can explain purged CV vs random K-fold
- [x] Can trace a backtest PnL line to positions, asset return and cost attribution
- [x] Can validate a run from config hash, code version and immutable dataset snapshots
