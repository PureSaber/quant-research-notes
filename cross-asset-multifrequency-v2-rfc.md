# Cross-Asset & Multi-Frequency v2 RFC

状态：M1冻结候选版  
schema版本：`2.0.0`  
所有者：`quant-data-kit`负责市场数据领域类型，`quant-lab`负责运行产物封装与验证。

## 1.目标与非目标

v2建立跨资产、跨频率可复用的语义底座，使日线、分钟、tick以及不同交易场所的数据和研究运行可以使用同一组可审计接口。M1只冻结并实现数据与运行契约，不实现撮合、账户账本、跨资产风险或新的研究策略。

以下原则是强制约束：

1. 资产和市场差异通过显式字段和adapter表达，不使用symbol前缀或路径名称推断。
2. 所有因果数据同时记录事件发生时间和研究者可获得时间。
3. 所有跨仓库文件都由版本化schema描述；缺失必填字段必须失败，不能自动补空列。
4. 价格、数量和金额使用固定点数；浮点数只用于收益率、统计量和无量纲暴露。
5. v1目录和读取行为保持不变；v2损坏时禁止静默回退v1。

## 2.标识与固定点数

### 2.1稳定标识

`instrument_id`是跨数据源、跨运行稳定的非空opaque ID。业务代码不得解析其字符结构获取venue、asset class或到期日；这些信息只能来自`InstrumentSpec`。`calendar_id`、`session_id`、`source`和`provider_symbol`同样按opaque ID处理。

### 2.2 FixedPoint

固定点数定义为：

```text
decimal_value = units × 10 ^ (-scale)
```

- `units`：有符号64位整数。
- `scale`：0至18的整数。
- `FixedPoint`禁止NaN和Infinity；缺失值使用null，而不是特殊数值。
- 加减前必须统一scale；乘除必须显式指定结果scale和舍入模式。
- 转换为`units`时若原值不能在指定scale下精确表示，默认失败；调用者只有显式指定舍入模式时才能舍入。
- 价格、数量、金额、tick、lot和contract multiplier都使用该语义。
- return、volatility、ratio、dimensionless exposure使用有限`float64`，NaN和Infinity均非法。

## 3.公开数据领域类型

### 3.1 InstrumentSpec

`InstrumentSpec`是某一有效期内的不可变合约规格：

| 字段 | 类型 | 约束 |
|---|---|---|
| `instrument_id` | string | 非空稳定ID |
| `asset_class` | enum | `cash/equity/etf/fund/future/option/bond/fx/crypto/index/other` |
| `venue` | string | 非空venue ID |
| `currency` | string | 非空结算币种代码 |
| `tick_size` | FixedPoint | 严格大于0 |
| `lot_size` | FixedPoint | 严格大于0 |
| `contract_multiplier` | FixedPoint | 严格大于0 |
| `effective_from` | UTC timestamp | 必填 |
| `effective_to` | UTC timestamp/null | 若存在则大于`effective_from` |
| `available_at` | UTC timestamp | 研究者首次可获得该规格版本的时间 |
| `superseded_at` | UTC timestamp/null | 若存在则大于`available_at` |
| `underlying_id` | string/null | 衍生品可用 |
| `expiry_date` | date/null | 到期型产品可用 |
| `metadata` | object | 仅放schema尚未标准化的说明性字段 |

规格变化必须创建新的有效期记录，不能覆盖历史记录。

### 3.2 SymbolMapping

`SymbolMapping`把数据源代码映射到稳定`instrument_id`：

- 键为`source + provider_symbol + effective_from`。
- 业务有效时间为`effective_from/effective_to`。
- 知识时间为`available_at/superseded_at`。
- `available_at`可以早于`effective_from`，因为映射可能提前公告；`superseded_at`若存在必须晚于`available_at`。
- 对同一source和provider symbol，同一业务有效区间、同一知识切面上最多映射到一个instrument。

### 3.3 TradingSession与MarketClock

`TradingSession`是已经展开到具体交易日的UTC半开区间`[opens_at, closes_at)`：

| 字段 | 说明 |
|---|---|
| `session_id` | 稳定session实例ID |
| `calendar_id` | 使用的日历版本 |
| `venue` | 交易场所 |
| `trading_day` | venue定义的交易日，不等于UTC或自然日 |
| `phase` | `preopen/auction/continuous/break/close/after_hours` |
| `opens_at/closes_at` | 时区感知UTC时间，且close严格晚于open |
| `available_at/superseded_at` | 日历session版本的知识有效区间 |

同一calendar的session区间不得重叠。夜盘属于其venue指定的`trading_day`，不得使用自然日猜测。

`MarketClock`只消费已版本化session，不访问网络，也不内置任何交易所假日。公开操作为：

- `session_at(timestamp)`：返回包含该UTC时间的session或null。
- `trading_day_at(timestamp)`：无session时返回null，不猜测。
- `is_open(timestamp, phases=...)`：仅指定phase视为开放。
- `next_open(timestamp, phases=...)`：没有后续session时返回null。

### 3.4 MarketEvent联合类型

所有event共享：`instrument_id`、`event_time`、`available_at`、`source`和可选`sequence`。联合类型由`event_type`判别：

- `QuoteEvent`：bid/ask price和quantity。
- `TradeEvent`：成交price、quantity和aggressor side。
- `BarEvent`：`bar_start/bar_end`、OHLC、volume、`is_complete`；`event_time=bar_end`。
- `StatusEvent`：交易状态和reason。

同一source、instrument和event stream中，非空sequence必须严格递增。`available_at>=event_time`。不完整Bar可以保存，但不得作为已完成Bar进入因果研究。

## 4.UTC双时间与PIT

v2时间戳必须是时区感知UTC值；naive时间或非UTC时间直接失败，不做隐式本地化或转换。

两组时间含义不可互换：

- 业务时间：`event_time`或`effective_from/effective_to`，表示市场事件发生或事实生效。
- 知识时间：`available_at/superseded_at`，表示研究者何时能够看到该版本。

PIT查询必须同时满足：

```text
effective_from <= observation_time < effective_to（若effective_to存在）
available_at <= as_of < superseded_at（若superseded_at存在）
```

`observation_time`和`as_of`必须由调用者分别提供。禁止把event time自动当作as-of，也禁止在找不到可用版本时采用最新记录。

## 5.Arrow与JSON schema

`quant-data-kit`发布以下schema ID，版本均为`2.0.0`：

- `puresaber.instrument-spec`
- `puresaber.symbol-mapping`
- `puresaber.trading-session`
- `puresaber.quote-event`
- `puresaber.trade-event`
- `puresaber.bar-event`
- `puresaber.status-event`

Arrow用于Parquet物理类型，JSON Schema用于API和manifest记录。两者字段名称、nullability和固定点数含义必须一致。schema registry遇到未知ID或不支持的major版本必须失败。

## 6.standard/v2运行契约

v1保持原目录和内容：

```text
<run>/standard/run_manifest.json
<run>/standard/*.csv
```

v2使用独立不可变子目录：

```text
<run>/standard/v2/
├── run_manifest.json
├── run_manifest.sha256
├── config.json
├── metrics.json
└── artifacts/*.parquet
```

写入必须先在`standard`下的唯一临时目录完成全部schema验证、文件哈希和manifest哈希，再原子重命名为`v2`。若`standard/v2`已经存在则失败，不能覆盖。

### 6.1 RunManifestV2

必填字段：

- `schema_version="2.0.0"`
- `project`、`run_id`、非空`strategy_ids`
- `profile`
- UTC格式`created_at`
- `status="complete"`
- `code_version`、`config_sha256`
- `base_currency`
- `dataset_snapshots`
- `capabilities`
- `artifacts`
- `tags`

每条artifact记录必须包含`name`、相对`path`、`schema_id`、`schema_version`、SHA-256、rows、columns、required以及可用的最小/最大event time和available time。path必须留在`standard/v2`内。

`run_manifest.sha256`保存`run_manifest.json`的SHA-256。除manifest及其hash文件外，目录内每个普通文件必须且只能在artifact清单出现一次；额外文件、缺失文件或hash不一致均视为损坏。

### 6.2 profile与artifact

| artifact | research | backtest-ledger | 说明 |
|---|---:|---:|---|
| `config`、`metrics` | 必需 | 必需 | JSON也进入完整hash清单 |
| `returns` | 必需 | 必需 | 时间区间、策略、gross/net/nav/base currency |
| `positions` | 必需 | 必需 | 账户/策略/instrument、数量、价格、市值和币种 |
| `valuations` | 必需 | 必需 | 估值、FX和P&L快照 |
| `exposures` | 必需 | 必需 | factor/currency/asset-class等暴露 |
| `orders` | 可选 | 必需 | 不可由Fill反推 |
| `order_events` | 可选 | 必需 | 完整状态历史 |
| `fills` | 可选 | 必需 | 独立成交事实 |
| `costs` | 可选 | 必需 | commission/slippage/impact/tax/financing |
| `cash`、`margin` | 可选 | 必需 | 多币种现金和保证金 |

M1实现`research`profile；`backtest-ledger`schema在M1冻结，由后续execution里程碑实现生产适配。writer不得为未提供的必填artifact创建空文件。

## 7.读取与兼容

统一reader规则：

1. 若`standard/v2`存在，必须严格验证并返回v2。
2. 若v2目录存在但缺文件、schema错误或hash错误，直接失败，不得回退v1。
3. 仅当v2目录完全不存在时，才调用历史v1reader。
4. 原`load_and_validate_run()`继续保持v1语义；新入口为版本无关reader。

v2reader只支持相同major且明确注册的minor版本。未知major失败；新增optional artifact或nullable字段只能通过minor版本发布。

## 8.v1到v2迁移

v1缺少稳定instrument ID、时区、账户、真实quantity/market value和独立Fill，因此禁止通用迁移器猜测这些值。

迁移必须由资产adapter提供：

- symbol到instrument的PIT映射；
- naive日期/时间的原始venue时区与时间标签规则；
- base currency和账户/策略ID；
- 可追溯的quantity、price、market value及成本来源。

迁移成功后写新的`standard/v2`，不修改v1。无法恢复的字段写null并记录结构化`migration_issues`时，只能使用后续定义的`legacy-migrated`profile，不能标记为完整`research`或`backtest-ledger`运行。M1不提供自动猜测型迁移器。

## 9.验收门禁

M1完成必须满足：

1. Python类型、Arrow schema和JSON Schema的字段/nullability一致。
2. naive或非UTC时间、未来可得时间、重叠session、无效固定点数全部被拒绝。
3. v2writer生成Parquet、完整artifact hash清单和manifest hash，并保证不可覆盖。
4. 缺列、额外列、nullability、类型、hash、额外文件和路径逃逸均验证失败。
5. 同时存在v1/v2时优先返回v2；v2损坏时不回退；仅无v2时读取v1。
6. v1原有测试不改预期且继续通过。
