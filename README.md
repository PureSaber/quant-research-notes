# Quant Research Notes

新增：[11–20 研究可信度使用指南](research-integrity-11-20.md) 与 [事前投资目标示例](examples/investment-objective.json)。

Knowledge base and roadmap for the PureSaber quant research multi-repository workspace.

## Contents

| Doc | Description |
|-----|-------------|
| [roadmap.md](roadmap.md) | Learning path and project phases |
| [repos.md](repos.md) | Repository map and dependencies |
| [WORKSPACE_GUIDE.md](WORKSPACE_GUIDE.md) | 日常源码同步、固定提交集成与冻结研究环境的维护边界 |
| [2026-10-01维护与r4登记](validation/maintenance-20261001/README.md) | 行动观察契约修复、新环境验收、旧账户保留与新前向起点 |
| [2026-10-03轻量市场数据验收](validation/maintenance-20261001/RESOURCES.md#当前阶段轻量真实行情验收) | 四ETF真实日线采集、重复一致性和下游输入检查通过；全量数据建设延期 |
| [轻量真实数据全栈验收规范](validation/light-market-data-20261003/STACK_POLICY.md) | 各市场小样本预算、异常注入、续跑与存储验收，以及尚未覆盖的业务范围 |
| [当前P0—P2进展](validation/p0-p2-20261003/README.md) | 23仓能力、研究结论、统一入口及逐项验收；Studio十模板工作台，择时反事实与现金证券独立报价成交价差软件已验收，真实成本校准继续 |
| [TECH_DEBT.md](TECH_DEBT.md) | Security / maintainability debt register |
| [pitfalls.md](pitfalls.md) | Common backtest / ML mistakes |
| [research-integrity-v1.md](research-integrity-v1.md) | PIT data, validation, run contract, risk and attribution standard |
| [cross-asset-multifrequency-v2-rfc.md](cross-asset-multifrequency-v2-rfc.md) | Cross-asset data, time and standard/v2 contract RFC |
| [validation/m7/](validation/m7/) | M7状态、验收规范、历史FAIL、修复PASS和PR合并就绪审计 |
| [validation/m8/](validation/m8/) | M8全栈软件发布、14仓不可变清单、tag、CI和独立验证证据 |
| [validation/risk-pit-20260926/](validation/risk-pit-20260926/) | 联合约束、真实PIT证据、风险模型与前向观察 |
| [validation/governance/](validation/governance/) | P0-P2治理结项、独立只读验收与公开证据清单 |
| [P0_GITHUB_GOVERNANCE_CONTROLS.md](P0_GITHUB_GOVERNANCE_CONTROLS.md) | 14仓分支/tag平台保护与break-glass审计控制 |
| [P2_GITHUB_METADATA_AND_LIFECYCLE.md](P2_GITHUB_METADATA_AND_LIFECYCLE.md) | 18仓GitHub元数据与deprecated shim归档证据 |
| [experiment-log/](experiment-log/) | Short summaries of important runs |

## Repo stack（2026-09）

```text
currency-converter        → Python CLI warmup
sklearn-stock-trend       → supervised learning + walk-forward
a-share-multifactor       → factor IC + quantile + retail backtest
quant-hk-equity           → 港股日频探索性价格收益研究；真实数据与现金账本，未获可投资认证
quant-us-equity           → 美股研究扩展（private），不属于既有M8认证范围
quant-fund                → 基金研究、场外申赎与FOF监控；合成基金验收
quant-stat-arb            → 统计套利研究扩展（private），不属于既有M8认证范围
quant-timing              → 指数仓位与风格择时；因果回放及样本外门禁
quant-studio              → 本机研究模板页面；预览配置并显式执行上游CLI
quant-data-kit            → shared AKShare + Parquet + validation
quant-execution           → deterministic execution and exact ledger
quant-lab                 → cross-project experiment index
quant-report-hub          → unified charts (spread + equity adapters)
quant-crypto-basis        → fixture-certified crypto basis research
quant-futures-spread      → fixture-certified futures spread backtest
quant-infra-workspace     → private cross-repository health and governance tooling
spread-backtest-viz       → deprecated compatibility shim; archived read-only
```

港股首版说明与复现证据见[quant-hk-equity研究记录](https://github.com/PureSaber/quant-hk-equity/blob/main/docs/RESEARCH.md)。当前仅覆盖固定观察名单，不包含完整公司行动与历史PIT证券主表；该仓采用standard/v1研究产物，不属于已有standard/v2认证范围。

## Local workspace

Clone sibling repositories under a workspace root and set:

```powershell
$env:QUANT_WORKSPACE_ROOT = "<workspace-root>"
```

Use `quant-workspace/configs/desktop.workspace.yaml` for path resolution. Stack health:

```powershell
cd quant-infra-workspace
powershell -File scripts/health-check.ps1
```

## Conventions

- Config: YAML under `configs/`
- Outputs: gitignored under `outputs/` or `output/`
- CLI: `pip install -e .` then project-specific commands
- Tests: `pytest -q` before push

