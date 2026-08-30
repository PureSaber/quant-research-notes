# M7 Crypto L2采集与认证验收规范

更新时间：2026-08-30（Asia/Shanghai）

状态：`FROZEN / SOFTWARE_FIXTURE_PASS / MARKET_DATA_CAPACITY_BLOCKED`

## 范围

首期真实市场认证固定覆盖以下8条L2数据流，不允许用K线、逐笔或fixture替代：

| 供应商 | 市场 | 原生标的 |
|---|---|---|
| Binance | 现货 | `BTCUSDT`、`ETHUSDT` |
| Binance | USDT线性永续 | `BTCUSDT`、`ETHUSDT` |
| OKX | 现货 | `BTC-USDT`、`ETH-USDT` |
| OKX | USDT线性永续 | `BTC-USDT-SWAP`、`ETH-USDT-SWAP` |

所有原生代码必须经有效期`SymbolMapping`映射到稳定`instrument_id`；供应商代码不得直接成为全局主键。本任务仅使用公开行情连接，不读取交易密钥、不发送订单。

## 当前实现验收状态

- `quant-data-kit`源码提交`13e004a80296bb3a49c4bd54e64cb64670e56b01`、证据HEAD`5b15c2c26a5a2f2b125e912d7f9412caf477b31c`已通过软件、fixture和本机性能门禁。
- 独立只读验证见`M7_CAPTURE_REMEDIATION_V5_INDEPENDENT_VALIDATION.md`：P1=0、P2=0、无新增P3代码缺陷，结论PASS。
- 431项测试通过、1项既有平台skip；17个核心模块纯分支覆盖率全部≥90%；Python3.10、3.11、3.12精确HEAD CI全部SUCCESS。
- 默认8流Dense/Sparse共6轮通过吞吐、延迟、Raw/Normalized/archive/restore门禁；3×1000万均≥100,000events/s且峰值<16GiB。
- 当前归档容量不足，实际CLI的`preflight`和显式`run --confirm-long-running`均在联网前安全返回`PAUSED_PREFLIGHT_FAILED`；公共网络消息数、连续天数和真实市场认证均为0。
- 历史候选`63f49b0`的FAIL验证保留在`M7_CAPTURE_INDEPENDENT_VALIDATION.md`，不得改写或用当前PASS追溯升级。

## 采集状态机

1. 每条流必须显式经历`CONNECTING→BUFFERING→SNAPSHOT_SYNC→LIVE→RESYNC/PAUSED`状态；状态跃迁、原因和时间写入不可变Raw审计记录。
2. Binance先缓存WebSocket增量，再取得REST深度快照；丢弃`u<=lastUpdateId`的旧事件，首个有效事件必须满足`U<=lastUpdateId<=u`。USDⓈ-M后续事件要求`pu`等于前一事件`u`；Spot按官方更新ID连续性规则处理。数量是绝对值，0数量删除价位；删除本地不存在价位记录为可审计正常事件，不伪造盘口。
3. OKX当前真实流使用`seqId/prevSeqId`连续性，不再把JSON`checksum`作为有效完整性门禁。空`asks/bids`且`seqId==prevSeqId`按心跳处理；检测到不符合维护重置语义的回退或断链时必须进入`RESYNC`，重新获取快照后才能恢复`LIVE`。
4. 连接重试使用有界指数退避和抖动；达到失败阈值后转`PAUSED`并告警，禁止在未知缺口后继续把事件标为连续。
5. 本地接收时钟必须为UTC且有时区；`received_at`由单调采集顺序约束，`available_at`首期保守取实际本地可用时点，不得早于可审计接收时点。

## Raw、Normalized与质量证据

- Raw在不可变分段内逐消息保留TLS来源、连接/订阅标识、请求或频道、原始字节、接收时间、原生序列字段、内容SHA-256和采集器commit；分段按批量、字节或时间轮转，不采用每条消息一个文件，修订只能产生新segment或新快照。
- Normalized事件必须满足`MarketEvent`强制字段、整数价格/数量刻度、稳定标的映射、PIT和分区约束。
- 每个分区生成事件数、首末序列、重复、乱序、缺口、重同步次数、隔离数、Raw/Normalized哈希、盘口检查点哈希和时间覆盖率报告。
- 序列缺口、乱序、重复主键、类型错误、无时区时间或盘口重建失败的分区进入隔离区，不得进入Curated或认证统计。
- 双交易所只做适配完整性和交叉质量异常检测，不要求价格逐笔完全一致。

## 连续30天定义

- 认证窗口按UTC计算，`window_end-window_start>=30×86400秒`，且报告中的`continuous_days`必须与完整UTC日数一致。
- 8条目标流均必须覆盖整个窗口；每次断线、维护序列重置和重同步都必须有Raw证据及已解释区间。存在无法解释的采集缺口时，该窗口失败并重新累计，不允许用插值补齐。
- 只有Binance和OKX均通过真实数据门禁，Crypto状态才可写为`market-data-certified`。

## 机器认证交接

- 最终`puresaber.m7-certification@1.0.0`中的`providers`必须去重并按字典序写为`["binance","okx"]`。
- `capabilities`必须去重、排序，至少包含`btc-spot-l2`、`eth-spot-l2`、`btc-usdt-perpetual-l2`和`eth-usdt-perpetual-l2`。
- `window_start`和`window_end`必须是可解析的带时区UTC时间，`continuous_days`必须严格等于时间差的完整86400秒日数且不少于30。
- `evidence`必须指向认证清单目录内的不可变证据文件并记录SHA-256；认证清单创建时间不得早于市场窗口结束时间。

## 存储、归档与恢复

- 热数据配额150GiB；可用空间低于卷容量20%或100GiB中的较大值时，采集器必须先转`PAUSED`并告警，禁止自动删除。
- 2026-08-29全部正式性能证据保留后复核：C/D/E/G盘均已低于安全门限，不得用于新增采集或归档；F盘位于物理磁盘0（WD_BLACK SN770），剩余282.69GiB，扣除20%卷容量门限后可用171.94GiB，是当前热数据候选；H盘位于独立物理磁盘1（WD_BLACK SN850X），剩余218.95GiB，但扣除20%门限后只能使用32.96GiB，不能据此承诺8路L2连续30天。部署必须使用显式配置，不能把盘符硬编码进库。
- 启动长期采集前必须配置独立归档目标，通过可审计的物理卷身份确认其与热数据卷独立，并完成上传/复制、SHA-256复核和抽样恢复演练。没有可靠归档、容量不足或恢复验证失败时保持`PAUSED`。
- 归档成功后也只允许按明确保留策略清理已核验分区；30天认证窗口及其Raw、清单、质量报告和恢复证据永久不可变。

## 退出条件

1. 采集器、状态机、两供应商现货/永续适配、不可变写入、空间守卫、归档和恢复均有单测与故障注入测试。
2. Python3.10、3.11、3.12的lint、unit、contract和integration CI全部通过，关键路径无skip。
3. 8条流完成连续30天真实采集，盘口重建检查点哈希100%匹配，所有异常均可追溯且失败分区被隔离。
4. 认证报告及其证据文件由`puresaber.m7-certification@1.0.0`校验通过；国内L2仍可保持fixture警告，因此该结果最多允许`rc-ready`。

## 官方规则依据

- OKX checksum弃用公告：https://www.okx.com/en-us/help/okx-order-book-channels-checksum-field-deprecation
- OKX API文档：https://www.okx.com/docs-v5
- Binance USDⓈ-M本地订单簿规则：https://developers.binance.com/docs/derivatives/usds-margined-futures/websocket-market-streams/How-to-manage-a-local-order-book-correctly
- Binance Spot WebSocket文档：https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams
