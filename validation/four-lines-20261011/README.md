# 四条并行开发线交付

日期：2026-10-11。按用户授权使用相同模型与推理配置并行实现，由主线负责独立复核与合并。记录的是本轮软件实现与指定环境验收；真实市场数据、实际交易、生产环境升级和历史 M8 认证各有独立范围。

## 新增能力与入口

| 开发线 | 已实现内容 | 入口与说明 |
| --- | --- | --- |
| 一：平台与版本 | 26 仓能力索引；源码、安装、候选验收、发布指针分别核对；Studio 当前进程身份与磁盘源码漂移；完整因子族目录 | [Workspace 平台状态](https://github.com/PureSaber/quant-workspace/blob/main/docs/PLATFORM_STATUS.md)、[Studio 平台状态](https://github.com/PureSaber/quant-studio/blob/main/PLATFORM_STATUS.md)、[完整因子目录](https://github.com/PureSaber/quant-factors/blob/main/docs/COMPLETE_CATALOG.md) |
| 二：研究闭环 | 项目关联 Notebook、原生运行、失败任务和显式 Lab 登记；完整尝试清单、证据失效、人工结论及生命周期 CAS；Agent 与 Studio 独立进程 | [证据工作台](https://github.com/PureSaber/quant-studio/blob/main/RESEARCH_EVIDENCE.md)、[联邦复核](https://github.com/PureSaber/quant-agent/blob/master/docs/RESEARCH_FEDERATION.md) |
| 三：任务与容量 | 原 Job/Attempt/Worker 上的原子批次、取消和显式重试；共享不可变输入包及保护引用；Studio 多窗口研究入口；保存容量原始数值 | [批次调度](https://github.com/PureSaber/quant-pipeline/blob/main/docs/durable-batches.md)、[共享输入](https://github.com/PureSaber/quant-data-kit/blob/main/docs/input-bundles.md)、[网页批次入口](https://github.com/PureSaber/quant-studio/blob/main/DURABLE_RESEARCH.md) |
| 四：业务模型 | 固定资本 FOF 自身费用、利息、应付、支付、业绩准备金及高水位；多市场同币种 CTA 风险预算和整数合约、同约束基准、QExec 单账户 | [FOF 经济账](https://github.com/PureSaber/quant-fund/blob/main/docs/FOF_ECONOMICS.md)、[多市场 CTA](https://github.com/PureSaber/quant-strategy-adapters/blob/main/docs/MULTI_MARKET_TREND.md) |

期权已存在曲面拟合、离散分红美式模型、保证金研究及联合生命周期账本，本轮修正 README 基础/高级入口混淆。互换仓库已存在双曲线、抵押与 CVA，本轮未重复实现这些模型。

## 日常使用顺序

```mermaid
flowchart LR
    A[检查源码与各独立环境] --> B[登记数据与研究问题]
    B --> C[保存方案或 Notebook]
    C --> D[原生运行或持久批次]
    D --> E[保存成功、失败与中断证据]
    E --> F[复核证据和研究结论]
    F --> G[候选、复核、观察、暂停或淘汰]
    G --> H[另行决定部署与执行权限]
```

1. 用 `quant-workspace platform-status` 核对指定源码、运行配置和候选组合。Studio `/platform-status` 显示实际服务进程身份及保存的最近观测。单纯合并代码不会更新正在运行的服务。
2. 在 Studio 项目保存研究问题、数据和方案；Notebook 与原生方案运行共用项目证据页。Lab 绑定必须显式配置，只读获取登记和事件，不自动把探索性项目当成预登记实验。
3. `/durable-research` 使用已配置的独立 Pipeline 环境进行多窗口批次研究。失败或取消后显式选择重试，旧 Attempt 与证据保留；旧 Pipeline 环境经能力探测仍可使用已有单任务功能。
4. `/projects/{id}/evidence` 复核当前证据、失败原因和结论，关联文件或尝试清单变化会要求重新复核。生命周期进入观察不等于允许执行交易。
5. FOF 与 CTA 各从自己的原生 CLI 和固定环境运行，输出原生账本及报告。保持历史研究环境和已冻结账户独立；新版本组合必须另建和验收。

## 验收与审阅

精确提交、PR、CI 结果和合并回执保存在同目录 `delivery.json`。本地完整测试与远端固定提交检查分别列出，跳过项不计通过。合成样本和小规模容量不代表真实投资有效性或全量容量认证。

| 本地最终回归 | 通过 | 跳过 |
| --- | ---: | ---: |
| Workspace | 208 | 1 |
| Factors | 231 | 0 |
| Agent | 131 | 0 |
| Studio | 536 | 11 |
| Pipeline | 267 | 1 |
| QDK | 1018 | 7 |
| Fund | 155 | 0 |
| Strategy adapters | 16 | 0 |

Studio 的 10 个可选期权/互换集成在另一次明确隔离的固定环境补跑，与模板契约共 20 项全部通过；明确断言导入当前 Studio 源码，原生应用继续使用历史冻结解释器，未修改旧环境。剩余 Crypto 可选本地测试由相同 PR 的独立 Windows/Linux 上游 CI 覆盖。其余平台权限及条件跳过见机器清单和各仓测试日志，不统计为通过。Agent 总语句/分支合并覆盖率约 84.716%，纯分支为 75.85%，核心 standard 模块为 100%，不能把总覆盖率写成纯分支覆盖率。

- FOF：主线独立重放 109 个账户日、15 个指令；资产负债最大核对误差约 `2.33e-10 CNY`。包括费用欠付、准备金损失转回、结晶后不重复收费、净资产耗尽时整日回滚。
- CTA：独立样本波动率与整数张数核验，逐决策风险/名义/保证金约束；平仓后资金独立恒等式，同约束长仓基准与真实 CLI 报告。
- 批次：主线独立运行原子提交、幂等冲突、取消/重试、只读快照与输入损坏测试。Windows 测试子进程终止需要正常系统权限；沙箱拒绝终止的 `lease_lost` 不被改写成成功取消，获批在隔离测试目录重跑后通过。
- 研究复核：审阅发现“文件删除后保留旧实际哈希”的失效漏洞，已修复并覆盖删除、不可读和符号链接负例；Lab 新事件与新尝试也使旧复核失效。
- 故障展示：关联 Lab 数据库损坏或当前方案 HEAD 缺失/损坏时，仍保留完整历史、原复核理由与失效原因；拒绝据此进入观察状态。两种故障都经过独立负例复验。
- 平台状态：独立审阅修正“历史候选证据认证当前脏源码”的口径。候选历史证据与当前组合状态分开；重新签哈希的重复 case/output 及畸形凭证仍被拒绝。
- 容量观测：1,000 / 5,000 / 20,000 行，每规模 3 窗口冷暖两轮，共 18 个候选成功。原始测量见 [Pipeline 容量记录](https://github.com/PureSaber/quant-pipeline/blob/main/validation/durable-batches-20261011/capacity.json)。只观测本机单 Worker；未指定生产容量目标。

## 需要所有者处理的事项

`quant-workspace` 的机构研究工作流缺少 `QUANT_RESEARCH_READ_TOKEN`。代码已改为访问检查真实失败，后续验收明确未执行。所有者需要为固定私有依赖配置只读访问凭据，然后重新运行 `Institutional research acceptance`。无需把令牌发送到聊天或提交到 Git。软件 CI、本地已授权环境验收与这个尚未执行的远端私有组合验收不能互相替代。其余必需软件检查及四项公开研究集成全部通过，合并遵循现有保护规则，未绕过或关闭门禁。

真实基金合同费率/结晶日期、授权历史数据与具体生产环境切换仍由相应业务流程决定。这些不阻止本轮软件交付，但当前报告不把它们描述为已完成。

## 继续保留的技术边界

- 通用证据联邦只检查显式关联来源；哈希证明字节身份，不证明统计有效性。静态 CLI 清单无法自动发现未列入的任意文件。
- 共享 CAS 的读取校验仍有 I/O，当前读锁会串行；因子缓存仍仅覆盖已有显式算法，比较输入仍为 O(N)。没有把完整因子名称目录冒充全面增量计算。
- 本地 SQLite/子进程队列不等于多机调度，不承诺恰好一次执行；未自动迁移或删除旧 Notebook 输入。
- FOF 为固定投资者资本、CNY、ACT/365F，不含外层投资者份额申赎、税和外币；高水位是费用后口径。
- CTA 为初始已知固定风险资本，不随盈利再投资、不隐式换汇；风险绝对和为保守预算，不是实现波动率预测。下期开盘跳空仍由原生账户约束决定是否拒绝。
- GitHub 保存本轮源码和可复现证据索引，不是整台机器、虚拟环境和所有历史草稿的完整备份。
