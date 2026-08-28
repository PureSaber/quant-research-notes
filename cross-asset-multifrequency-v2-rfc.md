# Cross-Asset & Multi-Frequency v2 RFC

状态：M4已发布，M5接口冻结候选版
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
| `product_type` | string | 现货、线性永续、期货等显式产品类型 |
| `venue` | string | 非空venue ID |
| `native_symbol` | string | venue原生代码，仅用于适配，不作为全局主键 |
| `base_currency/quote_currency` | string/null | 资产和报价币种 |
| `settlement_currency` | string | 非空结算币种代码 |
| `price_tick` | FixedPoint | 严格大于0 |
| `quantity_step` | FixedPoint | 严格大于0 |
| `contract_multiplier` | FixedPoint | 严格大于0 |
| `calendar_id` | string | 显式日历版本 |
| `margin_mode` | enum | `none/cash/cross/isolated/portfolio` |
| `inverse` | bool | 是否为反向计价合约 |
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

所有event共享：`event_id`、`instrument_id`、`event_time`、`received_at`、`available_at`、`source`、`trading_day`、`session_id`和`sequence`。从`quant-data-kit v0.6.0`起，全部事件的`sequence`都是非空非负整数。联合类型由`event_type`判别：

- `QuoteEvent`：bid/ask price和quantity。
- `TradeEvent`：成交price、quantity和aggressor side。
- `BarEvent`：`bar_start/bar_end`、OHLC、volume、`is_complete`；`event_time=bar_end`。
- `BookSnapshotEvent`：严格排序、无重复价位且不交叉的bid/ask多档快照。
- `BookDeltaEvent`：bid/ask、upsert/delete、price、quantity及`previous_sequence`。
- `FundingRateEvent`：有限资金费率及计费区间。
- `MarkPriceEvent`：永续和保证金估值使用的标记价格。
- `CorporateActionEvent`：公司行动类型、生效日、比例或现金金额及币种。
- `StatusEvent`：交易状态和reason。

事件顺序域严格定义为`(source,instrument_id,session_id,domain)`。`BookSnapshotEvent`和`BookDeltaEvent`共享`book`域，其余事件类型各自形成独立域；每个域内`sequence`必须严格递增。`BookDeltaEvent.previous_sequence`必须等于同一`book`域中紧邻的前一个sequence，因此首个Delta可直接衔接Snapshot。强制满足`event_time<=received_at<=available_at`。不完整Bar可以保存，但不得作为已完成Bar进入因果研究。

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
- `puresaber.book-snapshot-event`
- `puresaber.book-delta-event`
- `puresaber.funding-rate-event`
- `puresaber.mark-price-event`
- `puresaber.corporate-action-event`
- `puresaber.status-event`

Arrow用于Parquet物理类型，JSON Schema用于API和manifest记录。两者字段名称、nullability、枚举、双时间有效期和固定点数含义必须与公开dataclass领域约束一致。schema registry遇到未知ID或不支持的major版本必须失败。

### 5.1执行、订单、成交和账本契约

执行领域契约由`quant-execution`提供，契约预览版本为`1.0.0`，并且只依赖`quant-data-kit`的精确commit或已发布tag。评审期间允许锁到待发布契约的完整commit；合并`quant-execution`前必须改为默认分支CI通过后发布的tag。M1只冻结类型和接口，不实现撮合或发送真实订单。

`OrderIntent`必须包含`idempotency_key`、account/strategy/instrument ID、side、FixedPoint quantity、order type、可空limit/stop price、time in force、`reduce_only`和UTC`created_at`。market/limit/stop/stop-limit的价格字段组合不合法时直接拒绝。

订单状态固定为：

```text
created -> accepted -> partially_filled -> filled
   |           |              |
   v           +--------------+-> cancelled/expired
 rejected
```

终态不可继续跃迁；每次跃迁生成独立、单调sequence的`OrderEvent`。部分成交与最终成交必须在`fill_quantity`中显式给出本次成交量，其他跃迁的该字段必须为空。累计成交不能超过委托量，且所有数量使用同一scale。

`Fill`是独立成交事实，包含fill/order/account/strategy/instrument ID、side、FixedPoint quantity/price、UTC event time、maker/taker角色和可空venue trade ID。`Fee`、`Funding`和`Settlement`均为独立事实，金额允许正负以表示费用、返佣、收付和结算方向。

`LedgerTransaction`由至少两个`Posting`构成，每个posting包含ledger account、currency、FixedPoint amount，以及可选instrument和quantity delta。同一transaction必须在每个币种内精确借贷平衡，不允许以浮点容差通过。幂等键、reference ID和事件类型是必填字段。

公开接口冻结为：

- `Strategy.on_event(context,event) -> Sequence[OrderIntent]`
- `BrokerSimulator.submit/cancel`
- `RiskGate.check(order_intent,account_snapshot) -> RiskDecision`
- `MatchingModel.match(market_event,open_orders) -> Sequence[Fill]`
- `AccountLedger.apply(fill|fee|funding|settlement|corporate_action)`
- `RunEngine.replay(event_stream,seed) -> RunResult`

订单、订单事件、成交、费用、Funding、Settlement和LedgerTransaction均同时注册JSON Schema与Arrow schema，并提供提交到仓库的黄金样例。未知版本、字段、类型或nullability必须失败。

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
├── returns.parquet
├── portfolio_snapshots.parquet
├── positions.parquet
├── order_events.parquet
├── fills.parquet
├── cash_ledger.parquet
├── costs.parquet
├── exposures.parquet
├── attribution.parquet
└── 其余profile声明的Parquet产物
```

写入必须先在`standard`下的唯一临时目录完成全部schema验证、文件哈希和manifest哈希，再原子重命名为`v2`。若`standard/v2`已经存在则失败，不能覆盖。

### 6.1 RunManifestV2

必填字段：

- `schema_version="2.0.0"`
- `project`、`run_id`、非空`strategy_ids`
- `profile`
- UTC格式`created_at`
- `status="complete"`
- `code_version`、`internal_dependencies`、`config_sha256`、`random_seed`
- `base_currency`
- `dataset_snapshots`
- `instrument_master_version`、`execution_model_version`
- `capabilities`
- `time_range`、覆盖全部artifact且无环的`lineage`DAG
- `artifacts`
- `tags`

`code_version`必须是完整40位小写Git commit SHA；`internal_dependencies`的每个值必须是明确发布版本或完整commit，`main`、`master`、`latest`和其他浮动分支均不合法。

每条artifact记录必须包含`name`、相对`path`、`schema_id`、`schema_version`、SHA-256、rows、columns、required以及可用的最小/最大event time和available time。artifact必须是`standard/v2`直属的单个文件，path必须严格等于`<name>.json`或`<name>.parquet`，不允许子目录。

`run_manifest.sha256`保存`run_manifest.json`的SHA-256。除manifest及其hash文件外，目录内每个普通文件必须且只能在artifact清单出现一次；额外文件、缺失文件或hash不一致均视为损坏。

### 6.2 profile与artifact

| artifact | research | backtest-ledger | 说明 |
|---|---:|---:|---|
| `config`、`metrics` | 必需 | 必需 | JSON也进入完整hash清单 |
| `returns` | 必需 | 必需 | 时间区间、策略、gross/net、FixedPoint NAV和base currency |
| `positions` | 必需 | 必需 | 账户/策略/instrument、数量、价格、市值和币种 |
| `portfolio_snapshots` | 必需 | 必需 | NAV、现金、市值、保证金和P&L快照 |
| `exposures` | 必需 | 必需 | factor/currency/asset-class等暴露 |
| `orders` | 可选 | 必需 | 不可由Fill反推 |
| `order_events` | 可选 | 必需 | 完整状态历史 |
| `fills` | 可选 | 必需 | 独立成交事实 |
| `costs` | 可选 | 必需 | commission/slippage/impact/tax/financing |
| `cash_ledger`、`margin` | 可选 | 必需 | 多币种双式账本posting和保证金 |
| `attribution` | 可选 | 可选 | price/carry/funding/roll/FX/cost/slippage归因 |

`positions`必须包含估值币种、对应时点可得的FX rate及`fx_snapshot_id`，并同时记录本币市值和基础币种市值。`cash_ledger`逐posting保存transaction/idempotency/reference ID，不得只保存余额快照；每个事务至少两个posting，index从0连续，事务元数据一致，且按币种精确平衡。orders必须记录累计成交量和version，order_events必须记录本次成交量，fills必须记录account/strategy ID；三者字段必须与`quant-execution`契约同义。writer和reader都必须跨artifact核对order ID、账户、策略、标的、方向、scale、状态、version，以及订单累计成交量、事件成交量总和和Fill数量总和，任何超额或矛盾均失败。可空limit/stop price、order-event fill quantity和venue trade ID的Arrow nullability必须显式冻结。

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
7. 订单非法状态跃迁、超额成交、非UTC事件和不平衡账本transaction全部失败。
8. `quant-execution`只能依赖数据/契约仓库，数据仓库和`quant-lab`不得反向依赖执行实现。

## 10.M5组合、风险与归因接口

M5不改变`standard/v2`的`2.0.0`物理schema。现有`positions`、`portfolio_snapshots`、`exposures`、`costs`、`margin`和可选`attribution`承载全部新增结果；新增语义通过受控值、生产者版本和黄金样例冻结，不能给Parquet增加私有列。

### 10.1单一真值与依赖方向

1. `quant-execution.AccountSnapshot`和双式账本是现金、持仓、保证金、费用、Funding、Settlement及NAV的唯一事实来源。
2. `quant-portfolio`只能把目标组合转换为`OrderIntent`建议，不能直接修改现金、持仓、保证金或NAV。
3. `quant-risk-monitor`实现QExec公开的风险策略协议并由`RuleBookRiskGate`组合调用；QExec不得反向依赖风险仓库。
4. `quant-report-hub`只读取经过`quant-lab.load_and_validate_standard_run()`严格验证的运行产物，不从策略私有文件反推账本事实。
5. 分析层可以使用有限`float64`执行优化和统计，但所有跨仓输入输出、金额、数量、价格、保证金和归因值必须在边界转换为`FixedPoint`，并显式记录基础币种。

### 10.2QExec只读风险快照

`quant-execution`新增以下不可变公开类型：

- `PositionRiskSnapshot`：`instrument_id`、`asset_class`、`venue`、`settlement_currency`、quantity、mark price、基础币种signed notional、initial margin和maintenance margin。
- `PortfolioRiskSnapshot`：account/event time/base currency、NAV、基础币种现金价值、gross exposure、net exposure、initial margin、maintenance margin以及按`instrument_id`排序的position快照。
- `RiskCheckContext`：当前`AccountSnapshot`、`PortfolioRiskSnapshot`、待检查标的的`InstrumentSpec`、因果可得reference price，以及QExec使用同一时点FX换算的signed `projected_notional_base`；运行中检查时后三项为空。
- `PortfolioRiskPolicy`协议：`check_order(order_intent,context)->RiskDecision`与`runtime_check(context)->RiskDecision`。

`ExactAccountLedger.portfolio_risk_snapshot(event_time)`负责从同一时点的mark和FX快照生成风险快照。非衍生品notional为`mark×quantity×multiplier`，衍生品notional使用相同定义但NAV仍只计入未实现损益；gross exposure为绝对notional之和，net exposure为signed notional之和。缺少mark、FX或保证金参数时必须失败，不能用0或最新未来值代替。

`RuleBookRiskGate`按配置顺序组合零个或多个纯函数式`PortfolioRiskPolicy`：

1. 先执行现有资产规则、现金/持仓/保证金和订单预留检查；
2. 再对每个policy执行`check_order`，首个拒绝立即终止并保留稳定code；
3. open-order重检、成交后检查、Funding/Settlement后运行中检查必须使用同一组policy；
4. policy不能发送订单、修改账本或读取网络，重放capture/restore后必须产生相同决策；
5. 构造`RiskCheckContext`失败时fail closed并记录`RISK_CONTEXT_INVALID`。

### 10.3跨资产组合约束

`quant-portfolio`在现有成本和流动性约束上增加：

- long/short及cash-aware预算，不再强制long-only权重和为1；
- gross/net leverage、单标的、asset class、currency、venue和strategy上限；
- initial/maintenance margin与可用资金约束；
- turnover、ADV参与率、days-to-liquidate、线性费用和平方根impact成本；
- 使用显式FX快照把目标notional转换到基础币种；缺失或晚于决策时点的FX/流动性数据必须失败；
- 目标权重转`OrderIntent`时按`price_tick`、`quantity_step`、contract multiplier和`reduce_only`规则确定性舍入，零数量订单不生成。

优化结果必须同时报告可行性、绑定约束、预计换手、成本、gross/net leverage、margin utilization和未分配现金。不可行问题返回结构化失败，不得静默放宽约束。

### 10.4模拟前置与运行中风险

`quant-risk-monitor`提供`CrossAssetRiskPolicy`，至少覆盖：

- gross/net leverage；
- 单标的、asset class、currency、venue和strategy集中度；
- initial margin、maintenance margin和margin utilization；
- ADV参与率和days-to-liquidate；
- 配置化压力场景、历史/参数VaR-CVaR及因子暴露漂移。

前置检查必须按拟议订单后的projected exposure决策；reduce-only订单不能被错误计为新增风险。运行中检查在Funding、每日结算、FX/mark变化和成交后重新评估。若某条启用规则所需的PIT价格、FX、ADV或分类缺失，返回稳定拒绝码而不是跳过规则。

### 10.5PnL与成本归因

`attribution.component`受控值为：

```text
price,carry,funding,roll,fx,commission,tax,maker_fee,taker_fee,
slippage,market_impact,financing,residual
```

`costs.cost_type`复用对应成本类受控值；一个账本总费用可以拆成多条成本/归因明细，但所有明细之和必须与账本费用精确一致。slippage以决策时因果可得reference price与成交价之差计算，market impact使用冻结模型参数，二者不得重复计费。

每个归因区间必须满足：

```text
delta NAV = price + carry + funding + roll + FX
            - commission - tax - maker/taker fee
            - slippage - market impact - financing + residual
```

按account、strategy、instrument、currency和base currency分别对账。`residual`绝对值不得超过`max(abs(delta NAV)×1e-8,0.01基础币种单位)`；超过即发布失败。价格、Carry、Funding、Roll、FX和成本来源必须可追溯到v2 artifact或manifest声明的数据快照。

### 10.6M5退出门禁

1. 相同输入、配置和seed连续3次的风险决策、目标订单、归因和产物hash一致。
2. 至少各有一个A股、期货和Crypto用例证明组合建议只通过`OrderIntent`进入QExec，违规订单由前置风险实际拒绝。
3. 每个风险拒绝码覆盖接受、边界和超过边界三类测试；reduce-only、缺失PIT输入和多币种FX必须有负向测试。
4. 归因按区间、标的、策略和总组合四层通过NAV对账；费用、Funding、Settlement、Roll、FX和slippage均有黄金样例。
5. `quant-report-hub`优先读取v2，v2损坏时不得回退v1；仅v2不存在时保留v1读取。
6. 核心新增模块分支覆盖率不低于90%，全仓不低于80%，Python3.10/3.11/3.12矩阵全部通过。
