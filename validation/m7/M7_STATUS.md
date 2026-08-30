# M7认证与发布状态

更新时间：2026-08-30（Asia/Shanghai）

## 负责人结论

当前状态：`IN_PROGRESS / RELEASE_BLOCKED`

M0—M6已经完成。M7数据性能、执行性能及Crypto L2采集器软件/fixture门禁已经形成通过证据，但最新合并就绪审计发现`quant-workspace#3`存在认证证据语义绑定P1，`quant-execution#6`存在数据版本组合认证P2，因此当前三个候选仍暂停合并。组件PR在P1/P2关闭、独立验证和精确HEAD三版本CI通过后可以集成；组件合并或组件tag不代表真实市场认证。平台`v2.0`tag和GA仍由公共网络、连续30天、归档恢复及合法数据门禁阻断。

## 门禁台账

| 门禁 | 当前结论 | 证据/说明 |
|---|---|---|
| M6全栈治理 | PASS | `validation-logs/m6/M6_ACCEPTANCE.md`及独立全栈审计 |
| M7机器认证契约 | PASS / UNMERGED | `quant-workspace`PR#3，最新提交`c894c80`；Python3.10/3.11/3.12 CI通过，59项测试通过，M7核心纯分支覆盖率98.28% |
| 数据标准化10M、三次、每次≥100k/s | PASS / INDEPENDENTLY_VALIDATED | `quant-data-kit`源提交`009a361`三次为155,932.27、155,071.20、153,097.30events/s；每次1000万接受、0隔离、严格重载和确定性哈希通过 |
| 数据标准化峰值RSS<16GiB | PASS / INDEPENDENTLY_VALIDATED | 三次最大2.967GiB；实际临时目录为F盘，约3.31GB正式产物保留，未自动清理 |
| 完整撮合＋账本10M、三次、每次≥50k/s | PASS / INDEPENDENTLY_VALIDATED | PR#6源提交`99eac28`三次为59,340.69、62,627.03、52,966.75events/s；5%成交密度，风险/撮合/费用/精确账本/Arrow均在计时范围内 |
| 完整撮合＋账本峰值RSS<16GiB | PASS / INDEPENDENTLY_VALIDATED | 三次最大2,236.26MiB；严格重载和逻辑/物理哈希一致性通过，约4.20GiB新正式产物全部保留 |
| Python3.10/3.11/3.12 CI | PASS / UNMERGED | 机器认证、执行和数据最终候选三版本CI均通过；PR仍保持开放 |
| M7候选PR合并就绪 | BLOCKED / P1=1 | 独立审计发现`quant-workspace#3`未将认证声明与证据内容语义绑定；`quant-execution#6`仍锁定`quant-data-kit@v0.6.1`。见`M7_PR_MERGE_READINESS_AUDIT.md` |
| Crypto L2采集器软件/fixture | PASS / INDEPENDENTLY_VALIDATED / UNMERGED | `quant-data-kit`源码`13e004a`、证据HEAD`5b15c2c`；431项通过、1项既有skip，17个核心模块纯分支≥90%，Dense/Sparse共6轮和3×1000万通过；17/17证据哈希复算一致；独立验证P1=0、P2=0。历史`63f49b0`FAIL记录永久保留 |
| Crypto公共网络适配与回放 | NOT RUN / CAPACITY BLOCKED | Binance/OKX、BTC/ETH现货及USDT永续的8流fixture通过；真实TLS消息、重连、重同步、序列质量和盘口哈希尚无数据，不能宣称market-data-certified |
| Crypto独立归档预检与恢复 | BLOCKED | 全部本机卷已复核；C/D/E/G均低于安全门限。F/H为不同物理NVMe，但按门限F仅可用171.94GiB、H仅可用32.96GiB；现有归档容量不足以承诺8流30天，因此长期采集必须保持PAUSED |
| Crypto连续30天认证数据集 | FAIL | 未发现采集数据、数据快照、质量报告、归档恢复演练或market-data-certified产物 |
| 国内L2合法数据认证 | EXTERNAL BLOCKED | 当前仅供应商中立脱敏fixture；没有合法授权数据时不得通过真实市场认证 |
| 组件集成 | BLOCKED / REMEDIATION | 当前由认证语义P1和依赖组合P2阻断；修复并复验后允许merge commit合入和创建默认分支CI通过的组件tag |
| 平台发布 | BLOCKED | Crypto真实L2、独立归档和连续30天门禁未通过；不得创建平台`v2.0`tag或发布GA |

## M7机器认证门禁

- 分支：`codex/cross-asset-v2-m7-certification`
- 候选提交：`c894c80`
- PR：[PureSaber/quant-workspace#3](https://github.com/PureSaber/quant-workspace/pull/3)
- 契约：`puresaber.m7-certification@1.0.0`，内容寻址、规范JSON、证据文件SHA-256校验、不可覆盖发布。
- 发布语义：数据标准化和完整撮合＋账本分别必须有3次1000万事件实测；Crypto必须是Binance/OKX双源、BTC/ETH现货和USDT永续、连续30天；国内真实L2也必须连续30天才允许`ga-ready`，fixture最多`rc-ready`。
- 本地证据：Python3.12隔离锁文件环境依赖闭包通过，59项测试通过，总覆盖率94%，`stack_manifest.py`纯分支覆盖率92.19%，`m7_certification.py`纯分支覆盖率97.12%。本机没有Python3.10/3.11解释器，因此不记作本地通过。
- 最新远端证据：[GitHub Actions运行#33249314954](https://github.com/PureSaber/quant-workspace/actions/runs/33249314954)的Python3.10、3.11、3.12三个任务全部通过，均包含锁文件安装、Ruff、测试、总覆盖率和核心纯分支覆盖率门禁。
- 结论：PR保持开放；该门禁本身通过也不会替代真实性能和市场数据证据。

## 执行性能专项交接

- 分支：`codex/cross-asset-v2-m7-performance`
- 被测源提交：`99eac282b1d31e33828a2d18e0efa42f983ef049`
- 证据提交：`b99245d9145d44f481a41b2311b7a9c8d764f7b3`
- PR：[PureSaber/quant-execution#6](https://github.com/PureSaber/quant-execution/pull/6)
- 正确性：200项测试通过；总覆盖率95.44%；全部核心纯分支覆盖率≥90%；Python3.10/3.11/3.12最新两组CI通过。
- 性能：三次独立1000万事件完整路径分别59,340.69、62,627.03、52,966.75events/s；每次50万成交、100万零1笔账本交易；最大峰值2,236.26MiB。
- 确定性：三次逻辑哈希、每个Arrow文件物理哈希和清单哈希完全一致；严格重载全部通过；工作树均为干净源提交。
- 产物：`F:\puresaber-m7-artifacts\execution-final2-10m-99eac28`下三个目录各1,501,955,792字节，未自动删除；证据JSON SHA-256为`a26c9f0eefeb9b0150c9c1ed93b8163a57ec603c8349082847b3927755bec634`。
- 已知限制：正式负载显式为5%成交密度；单独50%成交密度压力负载仍低于50k/s；最慢正式轮仅高门限约5.9%；认证范围不是O(1)内存。
- 独立验证：初审`CONDITIONAL`发现失败恢复和流式结束账本状态问题；`99eac28`修复并补回归后复验PASS。
- 结论：正确性与M7执行性能PASS且已独立验证。PR保持开放，不允许提前合并或打tag。

## 数据性能专项当前证据

- 分支：`codex/cross-asset-v2-m7-data-performance`
- 被测源提交：`009a36162a2ec1a48fc4f96b93b2e675196e9263`；证据提交：`bb796ad49f5c69e9b31d1813d9ca12641755f876`。
- PR：[PureSaber/quant-data-kit#6](https://github.com/PureSaber/quant-data-kit/pull/6)，保持OPEN。
- 正确性：263项通过、1项Windows/POSIX符号链接skip；总分支83.98%；`normalized_v3`90.45%、`data_lake`90.32%、`l2_replay`95.83%，全部配置核心≥90%。
- 性能：干净提交三次1000万分别155,932.27、155,071.20、153,097.30events/s；最大RSS2.967GiB；接受100%、隔离0、严格重载和快照/manifest/claim/L2哈希一致。
- 存储：`TEMP`、`TMP`和实际`tempfile.gettempdir()`均为F盘；H盘三份新正式产物共3,310,487,778字节，未自动清理；证据JSON SHA-256为`69416eeba389ff520043c9382ed7e1ff7380f4d5937030a02cb84cb1ab80c08f`。
- 市场语义：OKX`checksum=0`不作为当前完整性门禁，非零CRC32只保留legacy fixture；空等序列心跳不生成Normalized delta，维护重置要求新快照。
- 独立验证：只读复核PR大diff、约2700行`normalized_v3.py`、公开接口兼容性、PIT/sequence/L2、lake-wide claim、失败回滚、不可变发布、OKX 2026语义和三份正式产物；263项测试、覆盖率、报告哈希、1000万event claim、36个文件大小与mtime及三版本CI全部复算通过。
- 已知限制：正式基准是单盘口、单snapshot加连续upsert的合成Binance-style L2，不代表真实网络、重连和全部盘口形态；内存会随活跃stream、checkpoint和partition增长，不构成O(1)证明；claim索引缺失时公共严格loader具有自修复写入行为，只读审计采用全分区哈希复算与纯内存claim重建。
- 结论：数据正确性、性能和三版本CI为PASS且已独立验证；不代表真实市场数据认证。

## Crypto L2采集器软件/fixture专项交接

- 分支：`codex/cross-asset-v2-m7-data-performance`
- 源码提交：`13e004a80296bb3a49c4bd54e64cb64670e56b01`；证据提交：`5b15c2c26a5a2f2b125e912d7f9412caf477b31c`；包版本`0.7.4`。
- PR：[PureSaber/quant-data-kit#6](https://github.com/PureSaber/quant-data-kit/pull/6)，保持OPEN/MERGEABLE，未合并、未打tag。
- 正确性：journal→snapshot按分区集合、行数、规范行摘要、`available_at`上界和最终L2 checkpoint进行语义重算；四类持久状态使用闭合Schema、严格类型和精确内容寻址文件名。
- 质量：431项通过、1项既有平台skip、0失败；全源码纯分支87.08%；全部17个核心模块≥90%；Ruff、格式和依赖闭包通过。
- 8流fixture：Dense三轮299.17—310.60messages/s、p99≤37.73ms；Sparse三轮573.59—578.13messages/s、p99≤15.97ms；Raw、Normalized、archive和restore-hash全部一致。
- 3×1000万：182,097.14—188,473.94events/s，最大峰值3.136GiB；每轮1000万接收、0隔离、严格重载和确定性哈希通过，3,310,487,778字节产物保留且未清理。
- 容量守卫：实际安装CLI的`preflight`和显式`run --confirm-long-running`均在联网前以退出码2返回`PAUSED_PREFLIGHT_FAILED`；8流0消息且`network_started=false`。
- CI：[GitHub Actions运行33315502321](https://github.com/PureSaber/quant-data-kit/actions/runs/33315502321)精确绑定证据HEAD，Python3.10、3.11、3.12均SUCCESS。
- 独立验证：`M7_CAPTURE_REMEDIATION_V5_INDEPENDENT_VALIDATION.md`，17/17证据哈希、历史两项P2负向复现、真实硬退出、junction锁、stream anchor、测试、性能、容量和CI全部复核，结论PASS，P1=0、P2=0。
- 结论边界：软件、fixture和本机性能门禁PASS；公共网络、30天留存、归档恢复和market-data认证未执行，发布仍BLOCKED。

## 发布规则

1. 两个性能专项都必须返回范围、修改文件、实际测试/基准/CI证据和剩余风险。
2. 性能报告必须记录机器、Python与依赖、commit/dirty状态、计时范围、三次独立结果、峰值RSS和确定性哈希。
3. 性能未达标时保持PR开放，不得以缩小计时范围、跳过校验或推算值替代10M实测。
4. Crypto真实L2必须完成采集、Raw/Normalized不可变快照、序列/校验和/PIT/盘口哈希质量门禁、30天数据集和归档恢复演练。
5. 国内L2在合法授权数据缺失时只能保持fixture认证。
6. 组件tag仅要求该仓库全部适用软件门禁、独立只读验证和默认分支CI通过，并且不得被描述为平台M7或真实市场认证。
7. 平台`v2.0`tag和GA只有在全部适用真实市场门禁、全栈清单、独立验证和默认分支CI通过后才可批准。

## 2026-08-30合并就绪复核

- 15个正式仓库默认工作树均clean、0ahead/0behind；3个M7候选工作树均与远端PR HEAD一致，没有未推送源码commit。
- `quant-data-kit#6`和`quant-execution#6`单仓软件门禁通过，但执行候选尚未与数据候选`0.7.4`组合认证。
- `quant-workspace#3`存在P1：内容哈希只能证明“文件未变化”，不能证明“文件内容支持认证声明”；当前实现允许任意文本证据配合伪造指标通过门禁。
- 合并动作暂停，先归档治理证据、修复认证P1、更新内部依赖并完成新精确HEAD独立复验。
- 组件代码合并和组件tag不等于真实市场认证；平台`v2.0`tag及GA继续由30天和合法市场数据门禁阻断。

## 2026-08-29官方市场规则复核

- OKX已经自2026-06-23起弃用JSON订单簿`checksum`完整性校验；`books`、`books-l2-tbt`和`books50-l2-tbt`仍返回该字段，但值固定为0。真实流必须使用TLS连接并严格校验`seqId/prevSeqId`。现有CRC32测试只能作为历史fixture黄金测试，不能作为当前market-data认证依据。
- OKX增量频道允许空`asks/bids`心跳且`seqId==prevSeqId`，维护期间还可能发生序列重置。真实采集器必须显式处理心跳、重置和重新快照，不能静默当作普通连续增量。
- Binance USDⓈ-M本地订单簿要求先缓存WebSocket事件，再用REST快照对齐`U/u/lastUpdateId`，后续要求`pu`等于前一事件`u`；数量是绝对值，0表示删除。交易所明确说明删除本地不存在价位可能正常发生，真实适配层需保留可审计处理策略。
- 官方依据：
  - https://www.okx.com/en-us/help/okx-order-book-channels-checksum-field-deprecation
  - https://www.okx.com/docs-v5
  - https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/How-to-manage-a-local-order-book-correctly
