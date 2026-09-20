# PureSaber量化仓库P0-P2治理结项报告

日期：2026-09-05（Asia/Shanghai）

## 最终结论

独立只读验证基于GitHub实时API完成最终验收：`P0=PASS`、`P1=PASS`、`P2=PASS`，总评`PASS`。P0-P2治理、依赖安全、分支债务、GitHub元数据和deprecated shim生命周期已按授权收口。

权威产品状态保持`M8_SOFTWARE_RELEASE_COMPLETE / MARKET_DATA_GA_BLOCKED`。本次治理PASS不代表`market-data-certified`、平台GA或实盘批准。

| 阶段 | 结果 | 主要完成项 |
|---|---|---|
| P0 | `PASS` | 精确恢复14个M8 annotated tag；14仓全部public；28组branch/tag Ruleset有效且无bypass；14仓无凭据持续集成；Issue#15/#16审计关闭 |
| P1 | `PASS` | 17仓治理文件与Dependabot安全更新；16个public仓CodeQL与安全告警清零；workflow供应链加固；删除69条已验证陈旧分支 |
| P2 | `PASS` | 18仓metadata校准；7个治理/收口PR全绿合并；`spread-backtest-viz`建立两个恢复锚点并归档只读 |

平台控制的公开细节见[P0 GitHub治理控制](../../P0_GITHUB_GOVERNANCE_CONTROLS.md)，元数据与归档闭环见[P2 GitHub元数据与生命周期闭环](../../P2_GITHUB_METADATA_AND_LIFECYCLE.md)。

## `spread-backtest-viz`归档结果

- 状态：`public`、`archived=true`、`license=null`。
- 默认分支：`master@8b80ceebe84492de60133f2f9432cf7f002f8327`。
- 最终CI：[33502122906](https://github.com/PureSaber/spread-backtest-viz/actions/runs/33502122906)，Python3.10、3.11、3.12全部成功。
- 恢复tag：`spread-backtest-viz-v0.1.0-pre-merge`，tag object`bed66d8f776a1d4cff0b062b8f80ebadf92f363b`，指向`cf492d3e73ceee712889e74dab0766e11cc48bee`。
- 兼容tag：`v0.2.0`，tag object`a5bdd78e7dd789400f66b297acf5032c41d31973`，指向`8b80ceebe84492de60133f2f9432cf7f002f8327`。
- 未移动既有tag、未改写历史、未force push；归档后0个open PR、0个open Issue、0个Release。

归档前、tag和归档后原始快照位于[`evidence/2026-09-05/`](evidence/2026-09-05/)，SHA-256由[公开证据清单](PUBLIC_EVIDENCE_MANIFEST.json)固定。

## 仍保持的边界

- private`quant-infra-workspace`受当前套餐限制，CodeQL与Secret Scanning没有与16个public仓相同的覆盖。
- 活动Dependabot PR与`quant-portfolio`unique分支按证据保留，不属于陈旧可达分支债务。
- 单人维护仓暂不要求1名独立GitHub审批者，继续依赖强制PR、strict required checks、不可变tag与只读技术验收。
- M9 Issues[#11](https://github.com/PureSaber/quant-research-notes/issues/11)、[#12](https://github.com/PureSaber/quant-research-notes/issues/12)、[#13](https://github.com/PureSaber/quant-research-notes/issues/13)仍open，继续阻断真实市场数据GA。

详细结论见[P0-P2最终独立只读验收](P0_P2_FINAL_INDEPENDENT_VERIFICATION.md)。完整机器快照中涉及private仓库精确状态的部分按公开披露规则仅保留SHA-256承诺，不公开正文。
