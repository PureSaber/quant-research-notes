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

## Phase 4 — In progress

- [quant-futures-spread](https://github.com/PureSaber/quant-futures-spread) (private): futures spread research published
- [quant-regime](../quant-regime): rule-based regime detector with position_scale + `detect-multi`
- [quant-risk-monitor](../quant-risk-monitor): drawdown / concentration alerts
- [quant-paper-sim](../quant-paper-sim): paper trading simulator (signals → holdings → NAV)
- [quant-workspace](../quant-workspace): central path resolver
- [quant-pipeline](../quant-pipeline): post-run orchestration
- [quant-factors](../quant-factors): shared factor library
- [quant-portfolio](../quant-portfolio): multi-strategy allocator
- [quant-agent](https://github.com/PureSaber/quant-agent): post-run QA review layer
- Live execution adapter (vnpy/ssquant) — later

## Skills checklist

- [ ] Can explain IC vs Rank IC
- [ ] Can explain purged CV vs random K-fold
- [ ] Can trace a backtest PnL line to trade ledger
- [ ] Can reproduce a run from YAML config alone
