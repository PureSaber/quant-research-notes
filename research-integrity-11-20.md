# 11–20：从漂亮回测到可审查研究

本轮是研究工具的开发与软件验收，不是策略实盘认证。代码不发真实订单，不自动选赢家，
也不把 DSR、PBO 或统计显著性解释为未来赚钱概率。原研究输出不覆盖；改变验证方式应注册新研究 ID。

## 功能与入口

|编号|实现仓库与入口|回答什么问题|需要警惕什么|
|---|---|---|---|
|11|quant-lab `TrialRegistry.register_family`、`deflated_sharpe`；factors 适配；report 卡|跨研究、所有尝试计算筛选校正 Sharpe|有效独立试验数只是敏感性假设；矩估计与样本依赖不稳定|
|12|lab `cscv_pbo`；factors `purged_combinatorial_splits`|样本内赢家在其他划分是否退化|原始 CSCV 与带 purge 的切分不是同一估计对象，也不是时间前推|
|13|lab `spa_mcs`；pipeline `quant-family-evidence`|整个预登记候选族是否改善，哪些模型不可区分|失败/缺失候选保留；不能仅用赢家的矩阵|
|14|lab `bootstrap_means`、`hac_mean`；pipeline/factors 适配|结论是否依赖区块长度与序列相关|所有块长一起展示，不能挑最显著的那个|
|15|execution `replay_segments`；A 股 `continuous`；pipeline `account_policy: continuous`|一笔资金持续滚动投资的路径|保留现金、持仓、订单、结算、风险锁存；批量重放不等于持久化断点恢复|
|16|lab `intervention_plan`；A 股 `run_paired`；report 卡|跑输与信号、配置、风控、频率、费用、延迟的关系|单因素反事实不是因果识别；残差包含交互和遗漏因素|
|17|QDK `forward_labels`；US `factor_label_samples`；factors 报告|诊断样本是否漏掉困难证券|有证据的退市归零必须保留；未知终值不可默认填零或最后价格|
|18|lab `nested_selection`、`register_transfer`；pipeline/factors 适配|选择方法本身能否迁移|所有学习在内层；跨市场还要冻结币种、费用、交易规则；回调不是安全沙箱|
|19|lab `invariants`；QDK/execution/factors 测试|现金、拆股、FX、前缀、成本等经济恒等式是否成立|固定订单成本单调性不能套在不同动态交易路径；本轮用独立手算，不声称对接 LEAN|
|20|本仓目标模板；lab 不可变注册；agent `quant-objective-review`|研究究竟要赚超额、控回撤，还是提高资金效率|只能事前定义，不能看到结果后改目标；缺证据不等于通过|

## 推荐使用顺序

1. 写下经济机制与一个主要投资目标；复制 [目标示例](examples/investment-objective.json)，
   修改为自己的事前预算，放入研究 recipe 的 `objective`，与配方一起注册。
2. 固定数据、价格/收益/股数口径、成本、币种、日期和代码。提前注册研究家族及所有成员，
   各 study 使用共同 `family_id`、`measurement_basis` 和共享 SQLite registry。
3. 先做可重现的单次账户与金融不变量测试，再做连续 OOS。默认独立折模式仍可使用，报告必须区别。
4. 需要调方向、中性化、窗口或模型时，调用嵌套选择 API；仅开启连续账户不会自动启用嵌套调参。
   保存每折内层分数、选中配方和选择哈希，再评估外层测试。
5. 对整个比较族生成统计证据；明确同日同币种的基准序列。失败、缺失、重试和未启动研究都披露。
6. 对经济原因使用配对实验。分别比较无策略风控的被动组合、同风险约束组合和本币零息现金。
   每次只改一个因素，核对净收益差额与残差，而不是直接拿掉亏钱的风控。
7. 用事前目标验收。收益、风险、费用、容量/执行、数据、停止条件分别判定；未提供容量模型时，
   高收益也不能被标记为可投资。agent 只读解释，禁止自动改目标或授权交易。
8. 将最终方法冻结到另一独立时期/市场；`register_transfer` 固定规则，结束后只做一次
   `seal_holdout`。本地哈希/时间戳不证明研究者从未看过目标市场，需诚实披露人为接触历史。

## 目标字段与单位

示例数字仅演示配置，并非对任何投资者的资金或风险建议。所有货币数值使用研究的本币。
目标阈值适用于 recipe 固定的评价区间，不同区间不得直接混用。收益、费用率、回撤用小数；
回撤是正幅度；费用率 = 总费用 / 初始资金；周转 = 区间内双边总成交额 / 初始资金。
容量是可持续部署的本币资金量，需要独立容量模型，不是日成交量。Sharpe、跟踪误差须写明年化频率。

`primary.metric` 支持净超额、净收益、Sharpe、跟踪误差、回撤幅度、净现金流收益率和资金效率。
现金流与资金效率须另写分子/分母，不能把会计利润随意当作现金流。数据与停止条件是预先命名的
布尔检查项：缺少实际测量时保持未知，不得由代理根据好看的收益推断为通过。

同样一份结果，例如净超额 2%、最大回撤 10%，可能通过以 1% 超额为主目标、20% 回撤上限的
研究，却不通过回撤上限 5% 的研究。两者都合理，前提是各自目标事前登记，且容量、数据等其他
硬条件有证据。不得在第一个结果失败后修改原研究；新假设要新 ID，并保留旧失败。

## 验收证据

各仓 tests 新增独立手算、噪声/弱信号、候选列置换、arch 差分、AR(1) 覆盖率、外层标签扰动、
真实账户分段/单次一致性、退市归零、缺失终值、哈希篡改和注册不可变测试。软件通过不证明
真实市场 alpha。方法说明、输入要求、CLI/Python 示例和限制在各仓 README 的 11–20 链接中。

## 方法来源

- [Bailey / López de Prado：Deflated Sharpe Ratio](https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf)
- [Bailey 等：Probability of Backtest Overfitting](https://www.davidhbailey.com/dhbpapers/backtest-prob.pdf)
- [arch SPA](https://bashtage.github.io/arch/multiple-comparison/generated/arch.bootstrap.SPA.html)、[MCS](https://bashtage.github.io/arch/multiple-comparison/generated/arch.bootstrap.MCS.html)
- [arch StationaryBootstrap](https://bashtage.github.io/arch/bootstrap/generated/arch.bootstrap.StationaryBootstrap.html)

参考实现的价值是明确检验对象和假设，不是借别人的显著性为自己的数据背书。
