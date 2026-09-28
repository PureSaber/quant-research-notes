# 约束、PIT、风控与前向观察验收

本轮从联合约束和风险输入缺陷出发，完成跨仓修复、真实固定ETF数据接线、历史滚动验证以及未来账户登记。代码已上传功能分支并提交PR；默认分支未合并。历史研究暴露的问题、失败attempt和修复前结果全部保留。

## 实际修复

|模块|已完成的行为|验收边界|
|---|---|---|
|QPortfolio|预算、单标的、行业、L1换手、线性因子边界联合求解及最终复验|不可行/不收敛拒绝；不允许逐项裁剪破坏前项约束|
|QRisk|缺失暴露/成本/压力数据拒绝，矩阵有限性与PSD检查，按观测和可得时间处理迟到数据|只减仓不能绕过无效数据；L1完整轮换可达2，普通权重仍不超过1|
|风险模型|PIT期初X、因子收益、F、D、Σ、绝对与主动暴露、风险归因、年化TE|防御副本与Σ恒等式复验；真实ETF试验只使用market统计代理|
|ASM|风险协方差进入优化，整手目标再验，每日检查实际账本|超限锁存，撤销挂单并释放预约，按配置停止或只减仓清仓，部分成交后继续按实际持仓重试|
|现金退出|全现金的基准相对TE/主动因子超限作为warning保留|非空组合严格限制；绝对因子约束和非法模型仍拒绝；交易规则仍可阻止成交|
|QF/QLab|中性化→截面排序→延迟，训练方向证据与实际执行信号一致|旧执行器或不匹配信号证据拒绝|
|QDK|官方附件哈希绑定主表断言，多版本发布时间/可得时间/生效时间；不可变快照|bind不改写既有history字节；未知费用保持空，回放明确使用假设费率|
|Pipeline/Hub|预登记全部候选、训练/隔离/测试、保留风险事件与失败、连续前向账户|代码和数据前缀被冻结；历史修订或已有收益变化拒绝|

跟踪误差是执行门禁，尚未成为优化器的二次约束。回撤上限是检测和触发线，不能保证跳空、次日成交和滑点后NAV不穿透。r2的15%触发线实际穿透至15.40%，具体账本解释见[FAILURES.md](FAILURES.md)。

## 真实数据范围

池内只有510300、510500、159915、588000四只股票指数ETF。原始与复权价格各1684行、每只421个交易日，覆盖2025-01-02至2026-09-24；基准421行、现金行动5项。9月25日为交易所公告的中秋休市，下一交易日为9月28日。

行情经AKShare适配器访问Sina，分红和公告来自EastmoneyF10，上市和交易规则由10份交易所/发行材料核证。主表每ETF保存2023与2026两版，共8行；只有执行字段在目标区间一致，才投影为4行给现行消费者。费用不是官方PIT费率，研究使用佣金万三、最低5元、滑点10bp等显式假设。

- 数据快照：`sha256-78142a01721f7cdc523fc2e728f730a185409cf0e3fdedc1ea6d424e945fa315`。
- 主表包：`9d90dc22eb16ddf8566e2c82342608605cafa42e20f286093b5daca569487f0d`。
- 实际规则核验截至2026-09-26T08:50:36.044423400Z；未来必须重新核验，不填写未来有效期。
- 来源URL、附件哈希、字段断言与可得时点见[evidence/source-index.json](evidence/source-index.json)。断言由人工提取，代码验证结构与绑定完整性，不自动认证附件语义。

这不是完整动态PIT：缺逐日停复牌、盘中状态、历史动态全集和供应商逐日vintage。信号使用当前历史复权版本；风险收益使用原始价加此前已公告权益。未来复权历史修订会阻断账户，不能偷偷覆盖。

## 研究与前向结果

固定方案见[PROTOCOL.md](PROTOCOL.md)。126日训练、5日隔离、63日测试形成3个完整折、189个测试日，末尾11日不足完整折未评估。每折重新投入相同本金；拼接收益不是连续持仓账户。只有base可选，buy_hold为对照，cost_2x和delay_1仅诊断，不据其收益换策略。

最终版本的结果和活跃前向账户见[RESULTS.md](RESULTS.md)。原始失败及r2现金退出冲突保存在[FAILURES.md](FAILURES.md)。全部参数与数据冻结不变；现金语义是在看到历史结果后修正，因此任何重跑都属于开发期历史验证，不能称为未触碰样本外证明。

前向账户固定base、2026-09-28至2026-12-31，在起点之前注册。只有真实日期推进并取得合格新快照后才能增加观察；登记当天观察数0。操作和不可绕过的阻断见[FORWARD_RUNBOOK.md](FORWARD_RUNBOOK.md)。

## 本地与远端

集成根目录为`H:/Documents/ChatGPT/temp/quant-risk-pit-20260926`，工作树与锁定的GitHub功能分支提交一致。精确应用SHA见Workspace的`profiles/research-workbench/stack.json`以及真实study中记录的code_identity；不能用包版本号代替提交身份。

|PR|作用|
|---|---|
|[QDK#21](https://github.com/PureSaber/quant-data-kit/pull/21)|真实来源主表、绑定与PIT前缀|
|[QLab#11](https://github.com/PureSaber/quant-lab/pull/11)|配方、风险和证据契约|
|[QFactors#11](https://github.com/PureSaber/quant-factors/pull/11)|信号证据与执行顺序|
|[QExecution#16](https://github.com/PureSaber/quant-execution/pull/16)|执行依赖冻结|
|[QPortfolio#12](https://github.com/PureSaber/quant-portfolio/pull/12)|联合约束优化|
|[QRisk#12](https://github.com/PureSaber/quant-risk-monitor/pull/12)|风险输入、模型与换手边界|
|[QAgent#11](https://github.com/PureSaber/quant-agent/pull/11)|研究依赖与证据接线|
|[QReport#18](https://github.com/PureSaber/quant-report-hub/pull/18)|真实风险报告|
|[ASM#16](https://github.com/PureSaber/a-share-multifactor/pull/16)|整手目标与真实账本风险执行|
|[Pipeline#14](https://github.com/PureSaber/quant-pipeline/pull/14)|滚动验证和前向冻结|
|[Workspace#13](https://github.com/PureSaber/quant-workspace/pull/13)|可复建入口、精确提交与指南|
|[Notes#25](https://github.com/PureSaber/quant-research-notes/pull/25)|协议、来源、失败和真实结果|

期货价差和加密基差仍保留独立冻结的既有样例，没有把ETF证据扩展宣称为这些产品的真实验证。旧工作目录未被本轮依赖升级覆盖。

## 尚未达到的验收条件

完整Barra风格模型尚未完成。已实现可消费PIT描述子的线性风险框架，但真实研究没有规模、价值、成长、质量、杠杆、流动性等完整描述子，也没有宽股票截面的行业约束加权回归、波动率偏差校准、时变特异风险或ETF成分穿透；不是MSCI授权模型。下一步需要可核验的财务披露与修订时点、行业与历史成分、流通市值和交易状态数据，先通过覆盖与时间因果验收，再估计与前向校准。4只ETF不具备估计完整风格体系所需截面。

未来收益不能提前完成。真实前向数据只能在注册起点之后积累。此处的软件通过、历史收益或模型统计代理都不构成实盘通过条件。

QDK旧采集模块曾出现同SHA偶发CI失败，重跑和本地10次重复均通过，但文件生命周期首因未确定；本轮没有修改该采集模块，残余风险与原日志已保留，不能把重跑通过当作已修复。
