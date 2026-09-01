# M8全栈软件发布状态

更新时间：2026-09-01（Asia/Shanghai）

## 当前权威状态

当前状态：`M8_SOFTWARE_RELEASE_COMPLETE / MARKET_DATA_GA_BLOCKED`

Cross-Asset & Multi-Frequency v2的内部软件范围已经完成：14个运行时仓库的默认分支均为clean、精确组件tag、无浮动内部依赖；数据/契约→执行→策略→组合风险→报告调度依赖方向通过机器验证；A股/ETF、国内期货、Crypto现货/永续三条fixture纵向切片均可形成`standard/v2`产物。研究、回测和paper trading范围内不发送真实订单。

本状态不是平台`v2.0`、`v2.0-rc`或`market-data-certified`。Crypto公共网络连续30天、独立归档恢复和国内合法L2仍未完成，因此不得宣称GA。

## GitHub治理P0与GA阻塞跟踪

- Milestone：[M9 Market Data GA](https://github.com/PureSaber/quant-research-notes/milestone/1)，不设置虚构截止日期；三项全部关闭并经独立只读验证前，权威状态保持不变。
- 平台控制：[P0 GitHub治理控制](../../P0_GITHUB_GOVERNANCE_CONTROLS.md)，记录14仓默认分支/tag Ruleset、单人审批边界、公开化审计和break-glass流程。

| GA阻塞 | GitHub Issue | 当前状态 |
|---|---|---|
| Binance/OKX、BTC/ETH现货与USDT永续8流、连续30个完整UTC日真实数据认证 | [#12](https://github.com/PureSaber/quant-research-notes/issues/12) | `BLOCKED_BY_ARCHIVE_CAPACITY / NETWORK_RUN_NOT_STARTED` |
| 满足容量门限的独立归档、SHA-256校验和恢复演练 | [#11](https://github.com/PureSaber/quant-research-notes/issues/11) | `BLOCKED / CAPACITY_AND_ARCHIVE_NOT_READY` |
| 国内合法授权L2数据及真实市场认证 | [#13](https://github.com/PureSaber/quant-research-notes/issues/13) | `EXTERNAL_BLOCKED / AUTHORIZED_REAL_DATA_NOT_AVAILABLE` |

Issue只公开脱敏指标、哈希和审计链接；Secrets、private仓内容、内部路径、授权原件和受限Raw数据不得进入公开Issue、PR或日志。

## 14仓不可变发布清单

| 仓库 | 默认分支HEAD | 组件tag | annotated tag对象 | HEAD默认分支CI |
|---|---|---|---|---|
| `a-share-multifactor` | `05567b057ec00286fc045888b907e734d327a914` | `v0.4.2` | `d5d7cb0bd0ed594ffc7aedb854d8b7ef74ed0344` | `33374854384`，SUCCESS |
| `quant-agent` | `80fb5deb9ab804d9224b0c064524c3b45981dd6e` | `v0.3.2` | `ff9b3dc17b0e88bd8bb2eace92ce22bca21cce43` | `33369046755`，SUCCESS |
| `quant-crypto-basis` | `34c816d981cb320e6aa1306225dde52459ffbf3e` | `v0.1.2` | `7924fe32e6c22cf5236728b2c254da06497fa06c` | `33374854096`，SUCCESS |
| `quant-data-kit` | `8f258f11be8e4d8edddcd41b79b817bd6c925970` | `v0.8.1` | `87fc686dfb2d5ac2f86eca0132b3cdf05ff87c63` | `33362531418`，SUCCESS |
| `quant-execution` | `15e4e5c9dbaf2fe9b438732b2e94db295d5ea58c` | `v0.5.1` | `8fe725f70c05be388f8591f0a21d7a87e56c4b8a` | `33367468083`，SUCCESS |
| `quant-factors` | `fb60fcbe30cf7012ca1def0eecab4e77a43c94a7` | `v0.3.0` | `5b71f7dbf6f4be8497b21db3c7f5c3507187fe85` | `33365385875`，SUCCESS |
| `quant-futures-spread` | `1787b6dc16dfebdf1d0bde96b07281e3ae61f070` | `v0.3.2` | `9f25549622d165f5a9b6263537cb0523dd81155e` | `33374854167`，SUCCESS |
| `quant-lab` | `27489d270e132adbec1bced93eb2ae84ad5e1a9b` | `v0.3.1` | `e88e41b298b3384c5ba88d8dc41d07b69bedb8ee` | `33224026198`，SUCCESS |
| `quant-paper-sim` | `03502329495498c6d4544c024d1488c9ccd2955d` | `v0.2.2` | `67074d5fda52683e96e93afc086b4fea8848f99d` | `33374856474`，SUCCESS |
| `quant-pipeline` | `e0b94b4a7ba84c8d583bdbfe8874a95c40602e2c` | `v0.3.3` | `ba4aae145c3c321041689a6c192a9bb6227f08d5` | `33374855685`，SUCCESS |
| `quant-portfolio` | `81e6dff1071a1114cfc5157d1d242225c7ab872d` | `v0.4.2` | `78f7c6e93e969d70a30dec5c23bf1f201dd6f031` | `33370867156`，SUCCESS |
| `quant-report-hub` | `4c7917231271a175c120ce4d63ef5c40abe470cb` | `v0.4.1` | `0ea0b8efcab81acc9166cc49b4dabd1515d6afef` | `33225284866`，SUCCESS |
| `quant-risk-monitor` | `229655a605122edf16e60ecfe148fdfe13f4aa43` | `v0.3.2` | `8941aab1264a468d1d349bddd914377d9b76cc64` | `33370866773`，SUCCESS |
| `quant-workspace` | `537388a4d9548b612fa1e4b306c482c04b45c433` | `v0.3.1` | `415adc712a7c7791a36ad981914e7dd5b640041a` | `33366648678`，SUCCESS |

所有tag均由默认分支CI通过后创建，tag类型复核为`tag`且peeled commit与表中HEAD一致。旧tag未移动、未重建；没有创建平台`v2.0`系列tag。

上表是M8软件发布时点的不可变快照，不是默认分支的永久HEAD清单。默认分支可在发布后经受保护PR、required checks和审计证据继续前进；这不会改变既有annotated tag对象、peeled commit或M8权威状态。任何tag修复仍须遵守break-glass授权，禁止历史改写、force push或移动既有tag。

## 本轮最终5个PR

| 仓库/PR | 最终验证HEAD | merge commit | 默认分支CI | 结论 |
|---|---|---|---|---|
| `a-share-multifactor#6` | `f43176d6a89b8757dec27defc934f88be90e7632` | `05567b057ec00286fc045888b907e734d327a914` | `33374854384` | MERGED/PASS |
| `quant-crypto-basis#3` | `cac24e0eaf3b63efce56d5d74a16c23e37bf5d0f` | `34c816d981cb320e6aa1306225dde52459ffbf3e` | `33374854096` | MERGED/PASS |
| `quant-futures-spread#4` | `ffc4e3b6eed0714d738e08589e3367dda186260e` | `1787b6dc16dfebdf1d0bde96b07281e3ae61f070` | `33374854167` | MERGED/PASS |
| `quant-paper-sim#3` | `dac3dac30eb8541af59e97f6526a1b59cccb980d` | `03502329495498c6d4544c024d1488c9ccd2955d` | `33374856474` | MERGED/PASS |
| `quant-pipeline#5` | `0a98a2587fca2fa2e0c190a50505f56d2a578876` | `e0b94b4a7ba84c8d583bdbfe8874a95c40602e2c` | `33374855685` | MERGED/PASS |

## 独立验证证据

- A股/ETF：Python3.10完整`99 passed`，总覆盖率86.64%，`run_contract.py`纯分支97.41%；Windows/Ubuntu×Python3.10/3.11/3.12 CI全部通过。验证发现并关闭了描述字段硬编码旧QExec版本的P2，新HEAD增量复验为P0/P1/P2均0。
- Crypto：`69 passed`，总覆盖率96.70%，认证核心纯分支100%，Python3.10/3.11/3.12 CI通过；生产认证路径只读Binance/OKX脱敏fixture，不执行网络采集或真实下单。
- 国内期货：`117 passed,1 skipped`，总覆盖率83.51%，认证核心纯分支97.83%，三版本CI通过；1项legacy skip已有负责人和解除条件，不在v2认证关键路径。
- Paper：Windows Python3.10为`115 passed,4 skipped`、总覆盖率92.00%，`state.py`/`execution.py`/`engine.py`纯分支分别93.75%/92.42%/90.18%；Ubuntu三版本CI均为119项通过。`0.2.0/0.2.0`、`0.2.1/0.4.1`和`0.2.2/0.5.1`版本元组、逐字节前代归档、递归归档链、篡改检出及未知元组fail-closed均通过。
- Pipeline：`78 passed`，总覆盖率93.28%；核心53项通过，`dag_runner.py`、`dag_schema.py`、`checkpoint.py`、`integrity.py`纯分支均≥90%；三版本CI无Node20警告或annotations。
- Portfolio：`46 passed,1 skipped`，总覆盖率92.07%，核心100%；Risk：`57 passed`，总覆盖率91.38%，核心93.90%。可选`quant_regime`集成skip不属于v2关键路径。
- 所有验证代理均为只读，返回范围、修改文件（无）、实际测试/CI、P0/P1/P2和剩余风险。一次策略验证因模型容量错误没有正文，未被采信；相同范围重新执行后才签发PASS。

## 不可变全栈manifest

- 生成配置：`quant-workspace/configs/v2.release.workspace.yaml`
- 固定创建时间：`2026-08-31T16:56:12+08:00`，清单规范化为`2026-08-31T08:56:12Z`
- 清单A：[stack-manifest-v2-release-a.json](stack-manifest-v2-release-a.json)
- 清单B：[stack-manifest-v2-release-b.json](stack-manifest-v2-release-b.json)
- `puresaber.stack-manifest@1.0.0`规范hash：`51b8278226a8c550ff14e2908d1ecaf81435cd0579970acba17f8a483978420a`
- 两个文件SHA-256：`F90889A154D1419BFB595A524FAA13D809D1BB39078AE1ABF729C2E7CAFD34AF`
- 两次生成逐字节一致；两次`verify-stack`均返回`valid=true`、`release_ready=true`、`issues=[]`。
- `validation/m8/*.json`固定为`eol=lf`，确保Windows的`core.autocrlf=true`检出后仍保持规范JSON并可通过`verify-stack`。
- 清单覆盖14仓、23个允许schema、14份外部锁文件、全部内部tag解析提交和完整依赖DAG；没有dirty仓库、浮动默认分支依赖、缺失tag、轻量tag或循环依赖。

## 仍未完成的真实市场门禁

1. Binance/OKX、BTC/ETH现货和USDT永续冻结8流公共网络真实数据，连续30个完整UTC日并通过序列、PIT和盘口hash质量认证；
2. 满足容量门限的独立归档、hash校验和恢复演练；
3. 国内L2合法授权数据和真实市场认证。

在这三项关闭前，当前成果只能称为“内部软件release complete、Crypto/国内L2 fixture-certified”，不能称为`market-data-certified`、`v2.0 GA`或实盘OMS/EMS。L2研究回放也不代表纳秒级HFT真实性。
