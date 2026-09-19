# P0–P2 日常研究交付与验收（2026-09-19）

这套工程现在能够把公开行情、研究结果、模拟账本、账户对账和报告展示串起来，并在失败时停止输出可用建议。工程运行成功不等于策略有投资价值；此次真实案例没有跑赢同仓位基准，前向观察天数仍为 0。

## 使用

统一安装及一条命令入口在 [quant-workspace 的 daily-research profile](https://github.com/PureSaber/quant-workspace/tree/codex/daily-research-workflow/profiles/daily-research)。从包含各仓库的目录执行：

```powershell
.venv-daily/Scripts/python.exe quant-workspace/profiles/daily-research/run.py
```

安装说明和精确依赖见该目录 README、requirements.lock、stack.json。入口先验证依赖版本、VCS 来源和锁哈希。所有内部包使用不可变 GitHub 提交，全新 Python 3.10 环境通过 `pip check`，不依赖 editable 相邻仓库覆盖。AKShare 派生 wheel 绑定提交及文件哈希。

## 交付范围

| 优先级 | 已实现并验收 | 证据与边界 |
|---|---|---|
| P0 基础与版本 | 前一批 5 个 PR 合并；新增模块统一依赖、干净安装 | 固定 SHA，保留旧标签 |
| P0 日常闭环 | 决策→索引→可选账户→看板；日志、失败刷新、并发锁、重复运行 | 真实输入重放成功，抓取失败仍刷新 blocked |
| P1 公司行动 | CNInfo 日期/单位/来源保留，现金与拆股进入精确账本 | 109 条真实记录；仅支持可核对的同日交付 |
| P1 交易状态 | 当前 ST/停牌接入，required/advisory 两种策略 | 本次源不可用；不代表完整历史 ST、退市库 |
| P1 账户 | CSV 期初、成交、入出金、期末、价格精确对账，按真实 NAV 计算差额 | 合成账单验收；用户账户尚未提供 |
| P1 研究 | 新 daily/case 流程冻结假设/参数/代码，保留成功失败，未来留出一次评估 | 旧 legacy 脚本不因此自动获得认证；未来留出尚未观测 |
| P2 案例与报告 | 真实数据、双账本、扣费基准、因子诊断、统一看板 | 40 日成功案例与 126 日失败尝试同时保留 |

## 真实案例不支持策略胜出

固定四只示例股票，20 日动量与波动率因子，周频信号。初始现金 10 万元、最多两只各 25%，使用次日价格撮合、费用和滑点。对照为同一执行引擎中的 50% 仓位等权买入持有；沪深 300 为未扣费价格指数，另列而不冒充同口径净基准。

区间为 2026-07-27 至 2026-09-18，共 40 个交易日（首日建账，39 个收益观测）：

| 序列 | 区间收益 | 最大回撤 | 成交数 |
|---|---:|---:|---:|
| 策略，扣费后 | +0.1971% | -2.5817% | 12 |
| 同仓位等权持有，扣费后 | +1.1890% | -2.6782% | 4 |
| 沪深 300 价格指数，未扣费 | -4.1475% | -6.1390% | 不适用 |

策略落后净基准约 0.9919 个百分点。全历史因子诊断有 8 个滚动折，正向折占 37.5%，FDR 后发现数为 0；这组样本不支持有效 alpha。窗口内含 1 次现金分红，保存两套成交、费用、现金账本及组合快照。

126 日窗口先执行并失败：000333 在 2026-06-29 的 CNInfo 每股现金分红为 3.80，腾讯复权价历史变化为 3.72，无法核对。40 日窗口是在排除该**已知数据冲突区间**后用于工程演示，不是未触碰留出，也不能取代失败的长窗口。所有尝试见 [attempts.json](cases/daily-2026-09-19/attempts.json)，固定环境结果见 [case.json](cases/daily-2026-09-19/supported-40/case.json)。

案例目录保存真实输入、来源清单、逐日收益和双账本，约 370 KB；[SHA256.json](cases/daily-2026-09-19/SHA256.json) 可核查文件。禁止修改原样本来得到更好结果。

```powershell
.venv-daily/Scripts/python.exe -m a_share_multifactor.research_case --config quant-workspace/profiles/daily-research/decision.yaml --inputs quant-research-notes/cases/daily-2026-09-19/inputs --output new-case-output --sessions 40
```

## 验收记录

- 新环境实际抓取：复权行情接口对 000333 请求失败，发布 blocked 并登记 failed；索引、看板成功更新。
- 当日已保存的 1,948 行、四标的真实输入重放：模拟卡、索引、看板成功。交易状态 unverified，投资有效性 unproven。
- 同一输入重复运行：截止日、状态、持仓、目标、拟交易完全一致。前向账户尚无成交，历史回放收益不能算作前向业绩。
- 合成账户：期初现金 1,000、100 股成本 10；入金 500；卖出 100 股×11，费用 5；期末现金精确为 2,595、持仓零。入金计权益而非收益。
- 自动测试：ASM 143 项，QExec 202 项，Pipeline 80 项，Portfolio 50 项（1 个既有 skip），QLab 31 项，Hub 88 项（4 个既有 skip）；QDK 新接口 4 项。GitHub 完整矩阵覆盖三种 Python，ASM 还覆盖 Windows/Linux。
- QDK 首轮 Python 3.11 CI 在既有 L2 并发采集测试出现文件移动/状态竞争失败，原提交重跑通过。保留这个间歇风险，不把重跑描述为已修复 L2 问题。

## 尚不能提前完成的验证

1. 前向留出固定为 2026-09-21 至 2026-12-31。未到来的交易日、实盘成交和独立收益验证不能预造；结束后用 holdout_review 核验完整区间再封存。
2. 用户未提供实际持仓、成交、资金流水，因此只完成导入能力与合成验收，不能称为真实账户已对账。
3. 免费接口仍会断连，000333 分红冲突仍需来源核验；完整历史证券主表、ST/退市、个人分红税、延迟应收款不在当前验收范围。
4. 尚未创建定时任务。入口可重复执行并自动生成报告；首次配置未来留出必须发生在开始日之前，不能事后补登记。

## GitHub 交付

新增实现 PR：[QDK #17](https://github.com/PureSaber/quant-data-kit/pull/17)、[QLab #8](https://github.com/PureSaber/quant-lab/pull/8)、[QExec #13](https://github.com/PureSaber/quant-execution/pull/13)、[QFactors #8](https://github.com/PureSaber/quant-factors/pull/8)、[Portfolio #10](https://github.com/PureSaber/quant-portfolio/pull/10)、[Pipeline #9](https://github.com/PureSaber/quant-pipeline/pull/9)、[ASM #12](https://github.com/PureSaber/a-share-multifactor/pull/12)、[Report Hub #14](https://github.com/PureSaber/quant-report-hub/pull/14)、[Workspace #8](https://github.com/PureSaber/quant-workspace/pull/8)。看板沿用了另一任务完成的扩展，再统一依赖和日常入口。
