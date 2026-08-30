# Cross-Asset & Multi-Frequency v2 RFC

状态：M0—M6已发布，M7软件门禁整改中，真实市场认证阻塞
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

## 11.M6调度、版本清单与治理接口

M6只编排本机研究、回测和paper trading任务，不引入分布式服务、实盘凭据或真实订单能力。`quant-workspace`是路径和版本事实的发现层，`quant-pipeline`只消费其冻结清单和已经发布的内部依赖；两者都不能反向修改研究运行的`standard/v1`或`standard/v2`。

### 11.1全栈版本清单

`quant-workspace`新增不可变`StackManifest`，schema版本冻结为`1.0.0`。每个仓库记录：

- 配置中的稳定项目名、相对workspace根目录的仓库路径和规范化origin URL；
- 完整40位小写commit SHA、当前branch、指向该commit的已发布tag和工作树是否dirty；
- `pyproject.toml`中的package name/version、Python版本范围；
- 直接内部依赖的package、仓库、精确tag或完整commit及其解析commit；
- 仓库声明的schema ID/version和外部依赖锁文件路径/SHA-256。

清单根节点记录`schema_version`、UTC`created_at`、workspace配置SHA-256、仓库记录、内部依赖DAG、允许的schema集合、`release_ready`和清单自身`manifest_hash`。除`created_at`外，相同workspace状态必须生成相同canonical JSON；调用者提供固定`created_at`时，完整文件hash必须确定。清单文件必须是`quant-workspace`生成的canonical JSON且以单个换行结束；缺字段、未知字段、非canonical编码、hash不一致或`release_ready=false`均不能进入v2调度。

发布模式必须fail closed：dirty仓库、浮动内部依赖、tag无法解析到清单commit、依赖目标不在清单、循环依赖、缺少声明的schema或外部lock均拒绝。审计模式允许记录dirty/untagged状态，但不得标记`release_ready=true`。旧tag不可移动；是否为注释tag也必须记录。

公开接口冻结为：

- `discover_stack(workspace,mode,created_at)->StackManifest`
- `validate_stack_manifest(manifest)->ValidationResult`
- `write_stack_manifest(path,manifest)`：临时文件、fsync、原子rename且拒绝覆盖
- CLI：`quant-workspace stack-manifest --mode audit|release --out <path>`和`quant-workspace verify-stack <path>`

### 11.2类型化DAG契约

`quant-pipeline`保留现有线性YAML读取，但v2配置必须声明`schema_version: "2.0.0"`。每个step必须包含稳定`id`、`kind`、显式`needs`、argv形式`command`、输入artifact、输出artifact、重试策略和timeout。`shell:true`仅保留给v1兼容配置；v2禁止shell字符串执行。v2运行只接受通过`quant-workspace.validate_stack_manifest`校验且`release_ready=true`的`StackManifest 1.0.0`；不再接受仅含`schema_version/created_at/repositories`的宽松映射。

artifact契约包含稳定`artifact_id`、规范化绝对或workspace相对path、producer step、可选schema ID/version、required、immutable和预期/实际SHA-256。同一artifact只能有一个producer；step读取另一步产物时必须同时声明`needs`和input artifact。未知依赖、重复ID、自依赖、环、路径逃逸和输出冲突在执行前失败。

公开类型冻结为：

- `PipelineSpec`、`StepSpec`、`ArtifactSpec`、`RetryPolicy`；
- `StepStatus={pending,running,succeeded,failed,blocked,cached,dry_run}`；
- `StepAttempt`记录attempt、开始/结束UTC时间、exit code、stdout/stderr日志hash；
- `PipelineCheckpoint`记录配置hash、stack manifest hash、run ID、seed、step状态、输入/输出hash和事件序列；
- `DagRunResult`记录确定性拓扑顺序、每步最终状态、失败隔离和产物索引。

公开入口冻结为：

- `load_pipeline_spec(path)->PipelineSpec`
- `validate_pipeline_spec(spec,stack_manifest)->ValidationResult`
- `DagRunner.run(spec,run_id,resume=False)->DagRunResult`
- `DagRunner.resume(checkpoint)->DagRunResult`

### 11.3幂等、重试与恢复

step幂等键为`SHA256(run_id,step_id,step定义hash,有序input artifact hash,stack manifest hash,seed)`。成功检查点只有在幂等键相同、全部immutable输出存在且hash一致时才可标记`cached`；输出缺失、hash变化或定义变化必须fail closed，不能把旧结果当成功。

每个step完成后通过临时文件、fsync和原子rename更新checkpoint；同时追加单调sequence的事件记录。checkpoint损坏、run ID/config/stack hash不匹配或出现`running`终态时，resume必须拒绝或把中断attempt明确标记为failed后重试，不能静默跳过。恢复任何已记录step（包括状态仍为`pending`的待重试step）前，必须重新计算全部input artifact hash和幂等键；任何变化都必须在追加resume事件或替换checkpoint前拒绝。

重试只针对配置的exit code或显式可重试异常，`max_attempts`包含首次执行。每次attempt使用同一幂等键、独立日志和确定性退避参数。`kind`精确等于`data_quality`、`schema_validation`、`sequence_validation`、`hash_validation`或`pit_validation`的step属于不可重试门禁；即使配置了匹配exit code或异常也必须忽略重试策略并在首次失败后阻断其后代。参数错误、契约/path/artifact hash错误同样不可重试。一个step最终失败后，其后代标记`blocked`，无依赖的其他分支可继续；`fail_fast=true`时才停止所有尚未开始的step。

### 11.4治理与资源门禁

1. Python3.10、3.11、3.12统一运行lint、unit、contract和integration测试。
2. `quant-pipeline`和`quant-workspace`全仓分支覆盖率不低于80%，DAG验证、checkpoint、hash及版本解析核心分支覆盖率不低于90%。
3. 跨仓CI只能安装全栈清单中的已发布tag或完整commit，禁止main/master/latest和未固定VCS引用。
4. 每个可运行仓库必须声明外部依赖lock文件及SHA-256；M6先治理解析结果，不强制所有仓库采用同一种lock工具。
5. L2配额检查在采集前执行：热数据默认150GB；当可用空间低于`max(卷容量20%,100GB)`时返回稳定`STORAGE_QUOTA_STOP`并停止新采集，不删除已有数据。
6. 数据质量失败分区必须作为隔离artifact进入DAG，任何curated或策略step依赖该分区时标记blocked；不能通过重试把schema、序列缺口、hash或PIT失败变成成功。
7. 同一fixture、配置、stack manifest、seed和run ID连续3次，拓扑顺序、step状态、事件序列、artifact hash和checkpoint hash必须一致（运行时间字段使用固定测试时钟）。

## 12.M7认证、证据语义与集成政策

M7把“组件软件可集成”和“平台真实市场认证”拆成两个不能互相替代的状态。组件PR可以在源码、fixture、性能、独立验证和精确HEAD三版本CI全部通过后合入默认分支；合并只表示软件能力进入主线，不表示公共网络、连续30天、合法市场数据或`v2.0 GA`通过。

### 12.1认证证据必须支持声明

只验证证据文件存在和SHA-256不足以通过认证。每类证据必须使用闭合JSON Schema，并将认证清单中的每个声明值与证据内容逐字段绑定：

- 数据性能证据必须绑定仓库、源码commit、dirty状态、三次独立运行、每次事件数、吞吐、峰值RSS、接受/隔离数、严格重载、确定性哈希和保留策略；
- 执行性能证据必须额外绑定订单、成交、费用、账本事件、成交密度、会计守恒和完整计时边界；
- Crypto市场证据必须绑定Binance/OKX、冻结8流、窗口起止、完整UTC天数、Raw/Normalized快照、序列与盘口质量、归档及恢复证据；
- 国内L2证据必须绑定授权来源、冻结范围、同等连续窗口和质量门禁；fixture证据只能产生`fixture-certified`，不得产生`market-data-certified`；
- CI证据必须绑定仓库、workflow运行ID、事件类型、精确40位`head_sha`、总体结论及Python3.10/3.11/3.12完整job集合。

证据文件哈希正确但Schema未知、字段缺失、未知字段、类型漂移、声明与内容不一致、运行commit不同、job矩阵不完整或使用自报成功字符串时必须fail closed。任意文本证据、伪造指标、伪造CI和同哈希不同语义都必须有负向测试。

### 12.2合并、组件tag与平台发布

1. 组件PR只有在候选精确HEAD得到独立验证`P1=0、P2=0`且三版本CI通过后才可使用merge commit合入；不得squash导致源码commit和证据commit失去默认分支可追溯性。
2. 组件tag只能从默认分支CI通过的commit创建，必须是新的不可移动annotated tag。组件tag只发布该仓库的软件契约，不代表平台M7或真实市场认证。
3. 下游内部依赖必须更新到已发布组件tag或完整commit，并重新执行组合CI和受影响的正确性/性能门禁；不得沿用旧tag推断兼容。
4. `v2.0-rc`最多允许国内L2保持`fixture-certified-not-market-data-certified`，但Crypto真实市场范围、窗口和归档门禁必须由机器认证器实际校验。
5. 平台`v2.0`tag和GA必须等待所有适用真实数据、30天、归档恢复、默认分支CI、全栈清单和独立验证通过；组件合并不能解除这些门禁。

### 12.3当前里程碑状态

- M0—M6已完成默认分支整合、独立验证和组件发布；
- M7合并就绪审计发现的认证证据语义绑定P1和执行依赖组合认证P2已经关闭；`quant-workspace v0.3.0`、`quant-data-kit v0.7.4`和`quant-execution v0.5.0`均已通过精确HEAD独立验证、三版本CI、merge commit集成及默认分支CI；
- 上述tag只代表组件软件契约，不能替代平台真实市场认证；
- 公共Binance/OKX连续30天、独立归档恢复及国内合法L2仍未完成；
- 当前权威状态、历史FAIL和修复后PASS记录位于`validation/m7/`，任何新结论必须新增证据或更新当前状态，不得改写历史审计文件。

## 13.M8全频率因子与PIT特征契约

M8把“数据聚合频率”“事件采样频率”和“因子窗口语义”从隐含日频假设中拆开。
`quant-data-kit`继续独占交易日历、session边界、Bar聚合、事件顺序和Curated快照；
`quant-factors`只消费经严格加载器验证的Curated快照或显式标记的冻结fixture，不能自行按
自然日重采样、猜测夜盘交易日、信任调用方自报的snapshot ID或访问浮动数据源。

### 13.1规范Schema与`FrequencySpec`

M8机器契约位于`contracts/m8/`。`FrequencySpec`、`FactorSpec`、`AsOfSpec`、
`AuxiliarySource`和`FactorFrameManifest`分别使用对应文件中的闭合JSON Schema；所有对象
`additionalProperties=false`，未知字段拒绝。`FrequencySpec`的Schema ID固定为
`puresaber.factor-frequency@1.0.0`，字段和条件约束为：

| 字段 | JSON类型 | 约束 |
|---|---|---|
| `frequency_id` | string | 非空opaque ID；业务代码不得解析字符串推断参数 |
| `kind` | string enum | `fixed_time_bar`、`session_bar`、`event_bar`或`market_event` |
| `periods_per_year` | string | 正有限十进制定点字符串，禁止指数、前导`+`、尾随零和负零；只用于显式年化 |
| `calendar_id` | string | 必填；24x7市场也必须使用版本化日历ID |
| `session_policy_version` | string | 必填；必须与来源快照聚合或事件归属策略一致 |
| `interval_ns` | integer/null | 仅`fixed_time_bar`为1到int64最大值；其他kind必须为null |
| `session_rollup` | string/null | 仅`session_bar`为`session`或`trading_day`；其他kind必须为null |
| `event_bar_basis` | string/null | 仅`event_bar`为`trade_count`、`base_volume`或`quote_notional` |
| `event_bar_threshold` | FixedPoint/null | 仅`event_bar`必填；与QDK一致为`{units:int64,scale:integer[0,18]}`且值为正 |
| `market_event_types` | array/null | 仅`market_event`为非空、去重、排序后的事件Schema ID数组 |

`fixed_time_bar`只表示固定纳秒间隔；日线、半日、夜盘、午休、DST和提前收市必须使用
`session_bar`并由版本化`TradingSession`边界决定，不能伪装成24小时`timedelta`。
`event_bar`是`quant-data-kit`按稳定事件顺序生成的完整合成Bar，必须在来源元数据中绑定
起止`sequence/event_id`、实际事件数、basis和threshold。`market_event`表示原生Trade、
BBO或L2事件流，不要求Bar字段，但必须保留`event_id`、`sequence`和事件Schema ID；只接受
声明`input_profile=market_event`的因子。OHLC滚动因子对该kind必须fail closed。

年化周期是研究配置，不能从间隔、日历或样本数量推导。`periods_per_year`先按规范十进制
字符串解析为Decimal；平方根使用precision=50、`ROUND_HALF_EVEN`的十进制上下文，再按
IEEE-754 roundTiesToEven转换为binary64。实现中禁止常量252、365或隐式24x7推断。

### 13.2QDK前置升级与统一认证输入

`quant-data-kit v0.7.4`的现有Curated manifest只绑定`recipe_version`、Normalized快照血缘和
Bar分区，未持久化日历、session策略、间隔、session rollup或event Bar聚合证据；现有
Curated loader也只接受Bar。因此`v0.7.4`明确不能产生M8认证输入。

M8实现必须先在`quant-data-kit`发布一个高于`v0.7.4`的新组件tag，并提供以下两个公共、
fail-closed工厂；`quant-factors`必须锁定该tag，不能复制私有loader逻辑：

```text
load_verified_curated_bars(root,dataset,snapshot_id)->VerifiedFactorInput
load_verified_normalized_events(
    root,snapshot_id,event_schema_ids,market_context_snapshot_id
)->VerifiedFactorInput
```

`VerifiedFactorInput`是`puresaber.verified-factor-input@1.0.0`联合类型，至少绑定`layer`、
完整源snapshot ID及逻辑hash、选择后逻辑hash、Schema ID/version集合、不可变Arrow表、
`calendar_id`、`session_policy_version`、市场上下文snapshot ID/hash和有序血缘。两个工厂均须先严格验证源快照manifest、
分区集合、行数、每分区物理SHA-256、分区/全数据集逻辑hash和上游血缘，再在同一显式快照
目录读取全部目标分区，复验Arrow Schema和内存表选择hash；任何读取期间变更都必须失败。

Normalized事件工厂只接受显式内容寻址snapshot、去重排序的事件Schema ID集合及不可变
InstrumentSpec/TradingSession市场上下文snapshot，验证每条
记录及同stream的`(event_time,sequence,event_id)`顺序；Trade、BBO和L2还须执行适用的
sequence/previous_sequence、快照锚点和缺口门禁。输出血缘同时保留完整Normalized快照hash
和选择后的事件集合hash，禁止把`read_normalized_events`返回的普通list直接升级为认证输入。

Curated manifest必须升级为带闭合`puresaber.curated-aggregation@1.0.0`元数据的内容寻址
版本。该元数据必须绑定`calendar_id`、`session_policy_version`、`kind`、`recipe_version`、
市场上下文snapshot ID/hash，以及和FrequencySpec相同的条件字段。`event_bar`还须按分区绑定源Schema、首末
`sequence/event_id`、实际事件数、basis和threshold；loader必须从Normalized血缘复算。
旧manifest永久可读，但只能产生`legacy-curated-not-m8-certified`。

因子层认证入口固定为：

```text
compute_factor_frame(
    input_ref,frequency,factors,*,as_of,auxiliary_sources=()
)->FactorFrame
```

`input_ref`是闭合的`FactorInputRef`：`layer=curated`时包含root、dataset和snapshot ID，内部只
调用Curated工厂；`layer=normalized`时包含root、snapshot ID、事件Schema ID集合和市场上下文snapshot ID，内部只调
用Normalized工厂。`fixed_time_bar/session_bar/event_bar`只接受Curated Bar，
`market_event`只接受Normalized事件；输入layer、Schema或权威聚合元数据与FrequencySpec
任何字段不一致均失败。调用方传入任意table/panel加一个字符串ID不能进入认证路径。

冻结fixture使用单独入口`compute_factor_frame_from_fixture(table,fixture_manifest,...)`。
fixture manifest适用相同Schema、逻辑hash和时间验证，但产物只能标记
`fixture-certified`，不能标记`curated-snapshot-certified`或`market-data-certified`。

Bar输入Schema ID固定为`puresaber.bar-event`、Schema版本固定为`2.0.0`，身份字段至少包括`instrument_id`、
`event_id`、`sequence`、`event_time`、`received_at`、`available_at`、`trading_day`、
`session_id`、`bar_start`、`bar_end`和`is_complete`；数值字段使用上游原名
`open_price/high_price/low_price/close_price/volume`。FixedPoint必须按
`Decimal(units).scaleb(-scale)`精确解码，禁止先经float；只有具体因子算法声明的数值边界
才允许一次显式转换为IEEE-754 binary64。

全部时间必须是UTC有时区值。Bar逐行满足`bar_start<bar_end`、
`event_time==bar_end`以及`event_time<=received_at<=available_at`；原生市场事件满足
`event_time<=received_at<=available_at`。同一标的按`(event_time,sequence,event_id)`严格
有序且身份键唯一。固定时间Bar还必须满足权威聚合元数据中的精确`interval_ns`；session Bar边界必须等于快照
绑定的session或trading-day rollup；event Bar必须通过上游顺序范围和threshold复算。不完整
Bar、序列缺口、重复、乱序、naive时间、策略版本不匹配或逻辑hash不一致一律拒绝。

`compute_factors(date/symbol/close,...)`作为`legacy-daily`兼容入口永久保留，但不能产生
任何v2认证声明。迁移期不把旧列名静默解释为v2列，也不根据数据间隔自动猜频率。

### 13.3因子依赖和窗口

`FactorSpec`必须声明稳定ID/version、`input_profile=bar|market_event`、有序源列、对应可用
时间列、窗口period数、数值dtype和是否年化。新Bar因子ID使用period语义，例如
`momentum_20p`、`volatility_20p`和`downside_vol_20p`；`20p`表示同一标的20个已完成
period，不表示自然日。旧`*_20d`仅属于legacy入口。

所有滚动计算按`instrument_id`隔离并使用已验证稳定顺序。年化波动率精确使用13.1规定的
十进制平方根和binary64舍入结果。频率、年化周期、窗口、dtype或
FactorSpec版本变化必须改变配置hash和产物血缘。

### 13.4逐行`as_of`与外部PIT选择

`as_of`是闭合`AsOfSpec`，必须显式传入，支持两种模式：

- `source_available_at`：每行`row_as_of`严格等于该源Bar或事件的`available_at`；这是
  backtest/paper的认证模式；
- `fixed`：每行使用一个显式UTC纳秒时间，只能生成`research-restated`范围，不能声明
  backtest-PIT-certified；源`available_at>fixed`的行不得产生非空因子。

`observation_time`始终是当前源行`event_time`，不能用`row_as_of`替代。若窗口内任何实际
依赖的源值在`row_as_of`后才可用，则当前因子值为null，同时保留实际最大
`<factor_id>__available_at`；只有所有依赖均已可用时才允许非空值。

每个外部基本面、FX或参考数据源必须作为`AuxiliarySource`独立绑定：

- `role`、Schema ID/version、snapshot ID、物理hash及规范逻辑hash；
- 业务键列、`observation_time`、`effective_from/effective_to`、`available_at`、可选
  `superseded_at`及int64`revision`；revision在
  `(role,business_key,effective_from)`内严格递增；
- 每个依赖值列到其可用时间列的强制映射，例如`pe_ratio -> pe_available_at`；
- join recipe及每个FactorSpec的`missing_policy=null|error`。

对每个源行和业务键，候选外部版本必须同时满足：

1. `effective_from<=observation_time<effective_to`，null`effective_to`表示正无穷；
2. `available_at<=row_as_of`；
3. `superseded_at`为null或`row_as_of<superseded_at`。

先选择最大`effective_from`，再选择最大`revision`，不得使用文件顺序、墙钟或“最后一行”。
同一`(role,business_key,effective_from,revision)`出现完全相同的两行返回
`AUX_DUPLICATE_VERSION`，相同身份但内容不同返回`AUX_REVISION_CONFLICT`；有效区间或superseded时间非法返回
`AUX_INVALID_INTERVAL`；没有候选时按FactorSpec返回null或`AUX_NOT_FOUND`。这些错误码和
选择顺序跨实现固定。

一个因子可以拥有多个来源快照；血缘按`(role,snapshot_id)`排序并完整记录，不得把外部列
并入Bar快照后只保留一个ID。对每个输出值，`<factor_id>__available_at`等于实际窗口内所有
Bar、事件及辅助值可用时间的最大值。值非空时该时间必须非空、UTC且不早于任何依赖；
`row_as_of`早于它时因子值必须为null，消费者也必须拒绝非空违规值。修订数据只能产生新
快照和新因子产物，不能原地覆盖。

### 13.5`FactorFrame`和规范内容hash

`FactorFrame`保留输入身份列，并携带完整`FrequencySpec`、有序`FactorSpec`、有序来源
血缘、代码commit/tag、输入/输出行数、输出Schema和`logical_content_sha256`。禁止把墙钟
写入逻辑hash字段；生成时间只能作为非确定性物理元数据存在。

逻辑hash算法固定为SHA-256，输入是`puresaber.factor-frame-canonical@1.0.0`规范envelope的
RFC8785 JCS UTF-8字节，而不是Parquet文件字节。envelope只有固定键`schema`、`metadata`、
`output_schema`和`records`；元数据先按闭合Schema转为typed cell，输出列按
`output_schema`顺序，行按`(instrument_id,event_time,sequence,event_id)`排序。JCS负责对象
键排序、字符串转义和无空白序列化，不再定义私有长度前缀。

除envelope键和固定`schema`版本字面量外，每个领域值必须转为以下唯一typed cell对象，
原始JSON number不得直接进入envelope：

- null：`{"t":"null"}`；布尔：`{"t":"bool","v":true|false}`；
- int8/16/32/64及uint：`{"t":"<arrow-type>","v":"无前导零十进制"}`；
- binary64：`{"t":"f64","v":"大端IEEE-754位模式16位小写hex"}`，`-0.0`先规范为
  `0.0`，NaN和正负Infinity拒绝；
- FixedPoint：`{"t":"fixed","u":"int64十进制","s":"0..18十进制"}`；
- UTC timestamp[ns]：`{"t":"ts_ns","v":"相对Unix epoch的有符号纳秒十进制"}`；
- date32：`{"t":"date","v":"YYYY-MM-DD"}`；utf8：`{"t":"utf8","v":"原值"}`，
  禁止Unicode规范化；binary：`{"t":"binary","v":"无填充base64url"}`；
- list：`{"t":"list","v":[cell,...]}`；struct：
  `{"t":"struct","v":[["按Arrow Schema顺序的字段名",cell],...]}`。

机器Schema和`contracts/m8/golden/factor-frame-hash-v1.json`共同冻结完整envelope及黄金hash；
Python和一个独立实现必须从同一`canonical_input`复算文件中的JCS字节和SHA-256。QDK合法的
纳秒时间不得降为微秒或RFC3339文本。

hash输入必须包括完整FrequencySpec、FactorSpec、源和辅助快照逻辑hash、join recipe、代码
版本、输出Schema及全部输出记录。任何来源、频率、因子集合、可用时间、数值或顺序变化都
必须改变hash。物理Parquet SHA-256另行记录，不能替代逻辑hash。

### 13.6M8退出门禁

1. session日线、1分钟、tick派生event Bar和原生事件输入分别有黄金样例；Bar类相同period序列的非年化因子一致，年化结果只按显式`periods_per_year`变化。
2. Curated和Normalized两个正式工厂均有内容/选择hash与TOCTOU负向测试；任意table伪配snapshot ID、快照内容篡改、Schema/recipe/日历不匹配、FixedPoint错误适配、源行乱序/重复、naive时间、不完整Bar、错误间隔和事件序列缺口全部fail closed。
3. 每个认证因子有逐行`row_as_of`和精确窗口可用时间黄金测试；多辅助快照、重叠版本、重复revision、修订/superseded数据及故意注入未来可得值后，PIT选择或稳定错误码完全符合13.4。
4. 同一输入、配置、代码和seed连续3次，FactorFrame逻辑hash完全一致；Python和一个独立实现复算规范hash黄金向量，JCS字节和SHA-256均匹配。
5. 旧`legacy-daily`结果保持回归兼容，但认证测试不得调用legacy入口；下游不得把legacy产物升级标记为v2认证。
6. Python3.10、3.11和3.12的lint、unit、contract、integration、`pip check`全部通过；QDK认证输入及因子频率、PIT和hash核心模块纯分支覆盖率不低于90%，各仓不低于80%。
7. 先发布具备13.2能力的新`quant-data-kit`annotated组件tag；`quant-factors`锁定该tag并在默认分支CI通过后发布新tag。下游升级后重新执行契约和纵向策略回归，不能从浮动分支安装。
