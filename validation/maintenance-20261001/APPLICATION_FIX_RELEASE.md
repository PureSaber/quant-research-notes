# 应用修复发布验收

状态：`PASS / MARKET_DATA_GA_BLOCKED`

检查日期：2026-10-02

本记录覆盖本轮11个应用仓的正确性、安全与报告完整性修复。11个应用代码PR及择时结果PR均已合并；10月2日补齐独立review环境的安装，并完成两种账户模式、独立双腿fixture及QDK跨仓验收。[Workspace#20](https://github.com/PureSaber/quant-workspace/pull/20)的9项检查全部通过后已合并为[`7cc2bf7`](https://github.com/PureSaber/quant-workspace/commit/7cc2bf77b90a619f722b8ca440177d860e31cdf0)，合并后的实际环境再次通过核验。本次`PASS`只适用于软件修复及集成发布。

## 修复范围与边界

|应用仓|已确认根因与修复|适用边界|PR与当前状态|实际验证|
|---|---|---|---|---|
|`quant-timing`|收益、成本和订单使用不同仓位路径，期货现金结算及决策日对齐不一致。统一为考虑价格漂移的交易路径，费用扣现金、期货损益结算，并导出明确的收益权重和成本单位。|研究会计与标准产物修复；不构成策略收益或实盘适用性证明。|[#3](https://github.com/PureSaber/quant-timing/pull/3)，已合并[`36ec230`](https://github.com/PureSaber/quant-timing/commit/36ec2309f0beed5773a78a64f1fd1990b6fa3f08)|64项通过，覆盖率84%；Python3.10/3.11CI通过。|
|`quant-portfolio`|缩放暴露时错误缩减总NAV，且非有限配置、NAV和持仓可进入状态输出。改为用完整资本预算计算NAV，单列投资与现金权重，并拒绝NaN、Infinity及越界scale。|只保证组合输入和会计输出边界；不验证上游信号、行情或优化假设。|[#20](https://github.com/PureSaber/quant-portfolio/pull/20)，已合并[`3ade084`](https://github.com/PureSaber/quant-portfolio/commit/3ade084bebd341c2faee652ee45555a7d6fbe9b3)|224项通过，覆盖率82.24%；Python3.10–3.12及CodeQL通过。|
|`quant-crypto-basis`|双腿意图独立接纳时，一腿拒单、部分成交或未成交仍可生成认证产物，并把发送意图误作已开仓。现在逐信号核对两腿均全量成交；不完整组合在写产物前失败。|保留真实成交状态，不伪造回滚或补成交；当前只认证离线fixture，不代表真实交易所执行原子性。|[#8](https://github.com/PureSaber/quant-crypto-basis/pull/8)，已合并[`a84d2fb`](https://github.com/PureSaber/quant-crypto-basis/commit/a84d2fbc562fb3098b86e445b8ed02ac7fa7d858)|72项通过，分支覆盖率96.08%；Python3.10–3.12及CodeQL通过。|
|`quant-futures-spread`|价差信号第二腿拒单或信号未触发时仍可完成认证；旧绩效遗漏首期回撤，旧标准成本金额缺少明确收益率分母。现在逐组合失败关闭，回撤包含期初基线，并发布`cost_unit=currency`及`return_capital`。|不伪造组合回滚；认证链仍为合成PITfixture，legacy路径仍是research-only。|[#10](https://github.com/PureSaber/quant-futures-spread/pull/10)，已合并[`3f1195a`](https://github.com/PureSaber/quant-futures-spread/commit/3f1195acb5421f3c4e5b780a2c63bf567bf58ef4)|124项通过、1项跳过，分支覆盖率83.80%；Python3.10–3.12及CodeQL通过。|
|`quant-factors`|历史因子只按日期裁剪，忽略逐条`available_at`；稀疏数据还会压缩滚动窗口和信号延迟。改为按每日决策时点重建可见数据，并在完整会话网格上计算依赖。|没有`available_at`时仍是文档化的描述性日终假设；严格PIT需要真实可得时间和完整交易日历。|[#20](https://github.com/PureSaber/quant-factors/pull/20)，已合并[`a26c758`](https://github.com/PureSaber/quant-factors/commit/a26c758f2e6d9bc4e6169d97df8cbc97cdaa4f9d)|182项通过，覆盖率88.61%；下游Pipeline27项和A股工作台21项通过；跨平台CI及CodeQL通过。|
|`quant-regime`|样本不足时把不可计算统计量替换为0，单条价格也落入`risk_on`及满仓缩放。现在要求波动排名和收益窗口样本充足，并拒绝非法窗口和非有限诊断。|市场状态仍是研究元数据；修复避免输出伪正常建议，不表示有订单执行。|[#5](https://github.com/PureSaber/quant-regime/pull/5)，已合并[`5f1a73f`](https://github.com/PureSaber/quant-regime/commit/5f1a73f95e774c5ebd06beeeb532530b8e838544)|10项通过，覆盖率84%；Python3.10/3.11及CodeQL通过。|
|`quant-hk-equity`|公司行动仅按`effective_at`且按输入顺序处理，晚知支付可能早于可得时点或权益登记；含行动NAV又被标成纯价格收益。现在联合有效/可得边界排序，保持权益先于支付，并区分v1/v2收益口径。|需要重建历史持仓数量的晚知权益登记和拆股仍明确失败关闭；成本只声明为HKD金额。|[#3](https://github.com/PureSaber/quant-hk-equity/pull/3)，已合并[`390d532`](https://github.com/PureSaber/quant-hk-equity/commit/390d5329c7e6ac2a7edf7fc711470b9ab49d7006)|18项通过；通过真实study/simulate执行入口运行合成公司行动最小复现，核对行动账本、NAV差异和v2口径；Python3.11/3.12CI通过。|
|`quant-report-hub`|报告忽略同日`return_weight`，把成本金额直接当收益率，并遗漏首期回撤；本地HTTP又把共同父目录暴露为静态根。现在按manifest语义对齐权重，以`return_capital`或期初NAV换算成本，完整计算回撤，并只开放明确证据文件及回环Host。|归因校验不等于策略有效性；HTTP服务只面向本地回环使用，不是公网认证或多用户访问控制。|[#21](https://github.com/PureSaber/quant-report-hub/pull/21)，已合并[`c2afcd3`](https://github.com/PureSaber/quant-report-hub/commit/c2afcd3f831cd90e08abb680adaf801caa39d701)|144项通过、5项跳过，总覆盖率88.44%；归因分支226/242；Python3.10–3.12及CodeQL通过。|
|`quant-fund`|监控预测重复实现赎回日逻辑，并使用通用日历计算到账，可能早于真实下单的成交和银行用途日历。现在直接复用Ledger的成交日及银行偏移路径。|预测仍是指示性结果，不会创建订单；锁定期、通知期、开放日和终止日约束保持。|[#4](https://github.com/PureSaber/quant-fund/pull/4)，已合并[`1e83bd7`](https://github.com/PureSaber/quant-fund/commit/1e83bd735340b435ef2a5c4b03933c54de985431)|38项通过；集成复现中预测与真实订单同为2024-01-05成交、2024-01-09到账；Windows及Linux CI通过。|
|`quant-studio`|回环绑定没有验证浏览器请求，恶意页面可跨站提交`action=execute`。现在校验单一回环Host和实际端口、同源Origin及进程级CSRF令牌，并拒绝跨源嵌入。|保护本机Web操作入口；不是面向公网的身份认证、授权或远程部署方案。|[#7](https://github.com/PureSaber/quant-studio/pull/7)，已合并[`f3c4aa9`](https://github.com/PureSaber/quant-studio/commit/f3c4aa9834d9d4a3c466abfccb0ee05ae869e054)|83项通过；真实HTTP覆盖Host、Origin、token、重复头、非法长度和clickjacking；本地及上游集成CI通过。|

上表仅列10个公开应用仓；另1个私有应用仓的实现、提交和测试证据保留在本地维护记录。本轮回归数按仓库分别报告，包含各仓自身重复矩阵时不做简单求和。测试均为软件与fixture、合成或既有公开派生证据验证；没有运行真实交易，也没有把本机维护证据、原始行情、凭证或用户私有材料提交到Git。

## 固定历史输入兼容性回放

择时仓使用修复后的会计路径把既有12组market comparison配置重放到新输出目录，没有覆盖旧结果。12组均为`complete`，每组10个评分折，全部`leakage_passed=true`。其中11组平均超额收益为负；唯一为正的是`position_hs300/tsmom`，平均超额收益为`0.0059439453`，低于旧结果约`0.00618`。该组描述性全样本净收益为`0.1259607125`，基准为`0.1867847046`；成本和持仓漂移修正后不能继续引用旧的约13.56%策略收益。

该回放覆盖2019-03-08至2026-09-28的既有历史窗口，只验证修复后的兼容性和结果变化是否可解释，不是新样本外、真实前向或策略优胜证据。日期版结果及双哈希receipt见[`quant-timing`PR#4](https://github.com/PureSaber/quant-timing/pull/4)，已合并为[`65cc610`](https://github.com/PureSaber/quant-timing/commit/65cc61032df8f6b8f67c860f29134963c7029ecf)，Python3.10/3.11CI通过。

港股仓使用已合并源码重放原有真实价格v1快照：1535行、5个标的，沿用同一181日旧holdout窗口。89/89个声明产物的SHA-256全部通过，新旧summary的SHA-256均为`7ab7faffcf891d8354cba91f86d1557b3a5c70b5cf71a710cb23316c650d02ce`。收益`12.052751%`和成本`HKD8542.51`保持不变，口径仍是`price_only_excludes_corporate_actions`，不能解释为股东总回报。

这次港股运行通过`PYTHONPATH`加载干净的新源码依赖；`study.json`的`installed_stack`为空，内嵌的是旧stack lock，实际依赖提交只在本地外部核验证据中记录。因此它只证明新源码可兼容重放旧输入，不是新的冻结或认证HK发行。真实`quant-hk-study/v2`仍缺完整公司行动、结算日历、历史股票池和交易状态证据；目录中存在`standard/v2`适配导出也不等于完成真实财务证据v2研究。

本轮尚无新增基金真实数据接通证据，基金保留输入仍是合成数据或mock覆盖。非公开应用的数据接入过程和失败证据保存在本地，不在本次公开发行中声明新增真实数据接通结果。

## 本地集成验收

研究工作台profile只更新本次实际包含的5项依赖：`quant-factors`、`quant-report-hub`、`quant-portfolio`、`quant-crypto-basis`和`quant-futures-spread`。`quant-regime`、`quant-timing`、`quant-hk-equity`、`quant-fund`和`quant-studio`不在该profile中，不引入与其职责无关的新依赖。

10月1日创建的review环境只有初始pip，上次依赖安装中断；10月2日按原锁补齐，源码问题没有通过单独补装`packaging`掩盖。正式锁未修改；本机AKShare工件与清单SHA-256一致，其他依赖复用缓存及进程级代理完成传输，未修改系统代理设置。研究环境与fixture环境独立安装，旧冻结环境未升级。

|检查|实际结果|
|---|---|
|源码与依赖|13项精确提交及干净工作树核验通过；研究环境126个包，`pip check`及`run.py verify`通过|
|独立fixture环境|42个包，依赖兼容及三个认证依赖、两项应用源码身份核验通过；fixture锁不变|
|Workspace回归|新环境100项通过|
|QDK与Pipeline跨仓回归|19项全部执行并通过，无跳过|
|ETF独立折|4个候选成功、0失败；续跑结果及产物哈希不变|
|ETF连续账户|4个候选成功、0失败；续跑结果不变，改写缓存收益指标被拒绝，恢复原始证据后可继续校验|
|期货与Crypto样例|期货2个、Crypto3个候选全部成功；仍为fixture-only|
|r4账户保护|本次没有新增前向观察；旧账户、r4冻结环境及登记代码身份保持原样|

机器可读结果和两种smoke的候选产物哈希见[集成回执](evidence/application-integration.json)。本地smoke使用Workspace提交`e74434ce9dde7dbcbdc41b22fb5a75015fae625d`；逐文件比较确认其与最终合并提交仅有`VALIDATION_V4.md`文档差异，运行代码、profile、两份依赖锁及13项源码pin保持一致。最终发行身份为`7cc2bf77b90a619f722b8ca440177d860e31cdf0`，review环境已固定到该提交，合并后依赖和源码核验通过。

工作台smoke只覆盖上述合成ETF流程及恢复检查。Studio本地HTTP、PIT因子、港股公司行动、基金日历及各应用主入口分别以上表单仓回归和CI为证据，不把单个smoke解释为覆盖所有应用。

## 市场数据及前向门禁保持阻塞

软件修复不等于市场数据GA。本轮不改变权威状态`M8_SOFTWARE_RELEASE_COMPLETE / MARKET_DATA_GA_BLOCKED`。

- `quant-data-kit`已经具备Binance/OKX采集、标准化、质量和认证工具；当前阻断不是全栈缺少采集器，而是独立归档、容量、部署和实际连续窗口尚未满足。
- [Issue#11](https://github.com/PureSaber/quant-research-notes/issues/11)仍为`OPEN`：独立归档、SHA-256复核、故障注入和恢复演练未完成。
- [Issue#12](https://github.com/PureSaber/quant-research-notes/issues/12)仍为`OPEN`：真实网络采集尚未启动，Binance/OKX的BTC、ETH现货及USDT线性永续共8流尚未覆盖同一连续30个完整UTC日。fixture、重放和软件样例均不计真实天数。
- [Issue#13](https://github.com/PureSaber/quant-research-notes/issues/13)仍为`OPEN`：国内合法授权L2数据、许可范围及真实连续认证仍未具备。
- ETF前向账户`etf-risk-forward-20261008-r4`的登记观察期从2026-10-08开始；截至本记录日期尚未到起点，登记时为0次attempt、0次观察。历史开发回放、CI、smoke或补算都不能替代10月8日以后自然产生的前向观察。

Issues#11/#12/#13满足各自资源、授权和时间条件前必须保持开放。ETF账户只有在真实日期推进、逐日输入和冻结前缀校验通过后才能追加观察，不能因本轮软件发布提前完成。
