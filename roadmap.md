# Learning Roadmap

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

## Phase 5 — In progress

- [quant-futures-spread](https://github.com/PureSaber/quant-futures-spread) (private): futures spread research published
- [quant-regime](../quant-regime): rule-based regime detector with position_scale + `detect-multi`
- [quant-risk-monitor](../quant-risk-monitor): drawdown / concentration / tail / stress / liquidity alerts
- [quant-paper-sim](../quant-paper-sim): paper trading simulator (signals → holdings → NAV)
- [quant-workspace](../quant-workspace): central path resolver
- [quant-pipeline](../quant-pipeline): post-run orchestration
- [quant-factors](../quant-factors): shared factor library
- [quant-portfolio](../quant-portfolio): constrained allocator and capacity model
- [quant-agent](https://github.com/PureSaber/quant-agent): post-run QA review layer
- Live execution adapter (vnpy/ssquant) — later

## Phase 6 — Cross-Asset & Multi-Frequency v2

- [RFC](cross-asset-multifrequency-v2-rfc.md): instrument、symbol mapping、market clock、
  UTC双时间、固定点数和`standard/v2`契约
- M0—M6：默认分支收口、契约、数据、执行、三条纵向切片、组合风险归因和DAG治理均已完成并保留独立审计链
- M7软件/fixture：数据性能、执行性能和Crypto L2采集器软件门禁已通过独立验证
- M7合并就绪：`quant-workspace v0.3.0`、`quant-data-kit v0.7.4`和`quant-execution v0.5.0`已从默认分支通过独立验证、CI和组件tag发布
- M7真实市场：公共网络、连续30天、归档恢复及国内合法L2仍为外部/时间阻塞，不得宣称`market-data-certified`或`v2.0 GA`
- M8全频率研究层：冻结显式频率/年化、Curated Bar输入和逐因子PIT血缘契约；`quant-factors`实现与下游迁移进行中
- 当前状态与证据：[validation/m7/M7_STATUS.md](validation/m7/M7_STATUS.md)

## Skills checklist

- [ ] Can explain IC vs Rank IC
- [x] Can explain purged CV vs random K-fold
- [x] Can trace a backtest PnL line to positions, asset return and cost attribution
- [x] Can validate a run from config hash, code version and immutable dataset snapshots
