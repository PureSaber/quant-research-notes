# 八项量化研究升级交付（2026-10-12）

本批完成八项有限范围的软件实现、四组同模型/同推理强度开发、协调审查及候选组合验收。
所有更改保留在 PR；未合并、部署、发送实盘订单或恢复暂停账户。

运行说明见 [quant-workspace evidence-research](https://github.com/PureSaber/quant-workspace/blob/3e9d63182bd56bc4088fd83957c1f20fd5dc3622/profiles/evidence-research/README.md)。

| 项目 | 实际交付 | PR |
|---|---|---|
| 1 | 统一经济计量声明，实际比较/排名门禁和原生复利报告 | [Lab #20](https://github.com/PureSaber/quant-lab/pull/20)、[ReportHub #31](https://github.com/PureSaber/quant-report-hub/pull/31) |
| 2 | 独立 Decimal 基准调用真实公司行动、期货、FOF 和 FX API | [Lab #20](https://github.com/PureSaber/quant-lab/pull/20) |
| 3 | 冻结留出预测进入固定政策和 QExec 现金/费用/基准回放 | [Adapters #3](https://github.com/PureSaber/quant-strategy-adapters/pull/3) |
| 4 | 连续共享资金、交收、FX、保证金和配置绑定检查点 | [Execution #32](https://github.com/PureSaber/quant-execution/pull/32)、[Portfolio #24](https://github.com/PureSaber/quant-portfolio/pull/24) |
| 5 | 不可变修订血缘和冻结控制下的旧新配对重算 | [DataKit #42](https://github.com/PureSaber/quant-data-kit/pull/42)、[Portfolio #24](https://github.com/PureSaber/quant-portfolio/pull/24) |
| 6 | 七类分开的模型/风险/费用诊断、样本限制与不确定性 | [Risk #21](https://github.com/PureSaber/quant-risk-monitor/pull/21) |
| 7 | Linux Docker 实际隔离及 Studio Notebook 显式执行政策 | [Pipeline #23](https://github.com/PureSaber/quant-pipeline/pull/23)、[Studio #42](https://github.com/PureSaber/quant-studio/pull/42) |
| 8 | 答案分离的助手评测与离线无标签基线 | [Agent #19](https://github.com/PureSaber/quant-agent/pull/19) |

## 独立验收

- [组合复验](cross-group-review.json)：预测两笔成交后现金 1017.60；修订前后损益 34/26、差额 −8；旧输入保留，普通比较拒绝不同输入，配对研究可执行；菱形血缘八组哈希顺序完整；删除一条不利观测后不再给完整窗口置信结论。
- [金融基准](financial-benchmarks.json)：四类真实 API 适配全部通过，期望先于生产调用写入；QExec/FX 为精确 Decimal，FOF 明示 1e-9 绝对容差；执行前后源码身份一致。
- [检查点](checkpoint-review.json)与[保证金](margin-review.json)：资金/合约配置不符拒绝恢复且保持原状态；区分初始保证金不足与维持保证金追缴，允许部分补款且不改变总损益。
- [助手反例](assistant-review.json)：13 例、18 条主张；另换未登记数字验证 −5/−0.025，错误财务结论、遗漏失败和冲突不拒答均被拒绝。在线模型质量未测。
- [Linux 原始 CI 产物复核](linux-review.json)：真实容器资源/网络/文件边界、恶意 PID 饱和失败清理，以及 Notebook 成功、失败和取消均有证据。Windows 不获得容器执行认证。
- 协调仓库 [208 passed、1 skipped](workspace-tests.xml)，覆盖率 87.44%；[核心分支门槛](workspace-core-gate.json)与 lint/format 通过。首次 Windows 长临时路径失败记录保留在工作区，缩短路径后全套复跑通过。

## 可核查的边界与阻塞

精确提交、干净状态与 PR 见 [source-snapshot.json](source-snapshot.json)；远端候选检查见 [github-candidates.json](github-candidates.json)。本地、Linux CI、跳过项、未运行项分别记录，不合计成一个认证分数。

尚需操作者给 quant-lab 的 financial-benchmarks、quant-strategy-adapters 的 full-suite 提供既有约定的 QUANT_RESEARCH_READ_TOKEN 私有仓库只读权限并重跑。未创建或修改凭据；这两项失败不会被本地通过替代。

预测入口为单期货/单币种/多头空仓/固定初始资本；连续账户采用固定合约子账归属及显式比例保证金。成交结算现金衔接通过不证明固定每张与比例保证金约束等价。修订影响仅覆盖已登记血缘，当前适配器未执行的 features/forecasts 明确 unavailable。诊断假设独立有界块，缺失观测不产生完整区间。助手评测限定结构化回答和公开回归集，合成结果不证明真实市场收益。

## 证据与复跑

- 四组原始交付：[A](group-a.json)、[B](group-b.json)、[C](group-c.json)、[D](group-d.json)，包含具体环境、命令、计数、跳过原因和 CI URL。
- [审查返修](review-findings.json)记录每个问题与复验依据。
- 本目录的 probe 脚本属于协调验收，要求本批 mission 的 group-a/b/c/d 工作区或对等源码路径；请使用新的输出目录，保留已有结果。生产用户入口及依赖安装按上方运行说明。
- [evidence-manifest.json](evidence-manifest.json)记录本目录文件哈希；运行 `python verify_evidence.py` 核对保留字节。目录禁用 Git 换行归一化，历史 M8 和前批证据未改写。
