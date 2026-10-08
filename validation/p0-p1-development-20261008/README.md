# P0—P1 开发验收（2026-10-08）

本轮把工作台日常操作、前向流程、成本与风险诊断、独立环境管理推进为可调用的软件功能。范围对应本轮约定的七项 P0—P1，不代表三个月真实观察已经发生，也不扩大既有 M8 发行认证。

## 功能与入口

| 优先级 | 功能 | 入口与交付 | 当前解释范围 |
|---|---|---|---|
| P0 | 数据证据页 | Studio 导航“数据可用性”，按模板读取最近原生预检 | 来源、缺项与阻断；没有契约声明的观察截止/可得时点显示 unknown |
| P0 | 任务中心 | Studio 导航“任务中心”，HTTP 预检/执行进入单 worker FIFO，任务状态持久记录 | 阶段、日志、排队/运行取消、服务重启中断记录；不自动重放旧任务 |
| P0 | 基金对账 | 已成功的基金运行→基金对账→CSV预览→显式执行 | 调用者提供的确认/到账 CSV，支持 observations 与 batches 两种原生只读核对；real_business_certified=false，不认证外部凭证真实性 |
| P1 | 日常前向流程 | Pipeline `quant-forward status/plan/run` | 显式交易日、收盘与采集时点、账户/配方/输入身份、同日幂等、中断恢复、外置回执；样例默认 paused |
| P1 | 成本与风险诊断 | ReportHub `execution-cost-diagnostics`及 verifier；Risk `validate-forecasts/verify-forecasts` | 成本按订单分组并隔离训练/留出；风险直接展示已有因果评分，保持未认证校准状态 |
| P1 | 多策略穿透与重叠 | Risk `portfolio-overlap`，可选`--risk-run` | direct+ETF、多层穿透、净/总敞口、未知/过期/未来/循环/深度桶、同向/反向共同持仓；缺证据时完整比例 unavailable |
| P1 | 固定独立环境 | Workspace `runtime-profile/doctor/bootstrap-env` | 精确提交、依赖锁字节、每项目独立环境、默认预览和显式创建；不修改冻结环境 |

本轮 P1 入口为 CLI、JSON/CSV 和成本 HTML 报告，未把 P1 表单嵌入 Studio。跨应用源数据仍由调用者按对应契约准备。

## 合并与复核记录

| 仓库 | PR | 合并提交 | 验证 |
|---|---|---|---|
| quant-risk-monitor | [#19](https://github.com/PureSaber/quant-risk-monitor/pull/19) | `7d935c89712211db29ff6c968745b7a8a4a91725` | 220 tests；独立复核17项及合成手算；main CI/CodeQL通过 |
| quant-report-hub | [#29](https://github.com/PureSaber/quant-report-hub/pull/29) | `968d7e943e53ae870a554b30fc36f6f42c8d2d2e` | 280 passed、5 skipped；独立报价桥接+诊断73项通过；浏览器合成报告验收 |
| quant-pipeline | [#20](https://github.com/PureSaber/quant-pipeline/pull/20) | `ffd0617c37084334ae4c3193e1d8fc0300ad3f3b` | 208 passed、1条Windows符号链接权限skip；Linux实际通过该回归；执行/提交/幂等复用身份、回执路径、并发与时间边界复核 |
| quant-studio | [#26](https://github.com/PureSaber/quant-studio/pull/26) | `7a716c1a6e4ae53a1297b886b6dbf845cf86a971` | 258 tests；服务生命周期、子进程、CSV变化与Windows读写竞争回归；Ubuntu/Windows及全部固定上游集成通过；桌面/390像素浏览器检查 |
| quant-workspace | [#51](https://github.com/PureSaber/quant-workspace/pull/51) | `1cda784470748ed0d42ec11c1f15cfdec407d2fb` | 156 passed、1条Windows符号链接权限skip；总覆盖率89.85%；独立复核只读元数据、锁外包、Git来源、extras闭合集与安装异常日志；最终提交专项46 passed、1 skipped；Python3.10/3.11/3.12及Ubuntu/Windows研究集成通过 |

代码审查独立于实现；发现的问题修复后重新跑针对性回归与所需全量检查，正常 PR 合并后核对主分支检查。没有关闭分支保护或降低测试门槛。

## 独立环境实机验收

在 Windows、Python 3.12.14 下执行。旧环境只读检查与新目录安装分别验收，profile 固定源码提交及依赖锁原始字节。读取目标环境元数据不启动目标解释器；安装阶段明确执行新环境的 pip。

| 场景 | 结果 | 解释 |
|---|---|---|
| 既有基金环境 | ready | 原环境只读检查通过 |
| 既有 A 股 uv 环境 | blocked / metadata_insufficient | pyvenv.cfg 只记录3.12，无法确定依赖中的补丁版本条件；未修改旧配置 |
| 全新 Workspace 环境 | ready | 新建venv、按原锁安装、安装本项目、pip check四步成功，最终doctor无缺项 |
| 全新 A 股环境 | ready | 使用原锁和Git固定的vendor/wheels；四步安装成功，最终doctor无缺项；不运行真实行情采集 |

最终环境管理实现及 Workspace 新环境源码为 `4d03e9e35586d04f61c0ad2f00ebd42752ca9b27`，A 股固定为 `2bec6dbe13637be287c715b00dc8e08ce7a7e2fe`。首次 A 股安装虽通过 pip check，但标准 venv 未记录实现类型而被最终检查阻断；修复在受控新建环境时记录创建器元数据，随后选择新目录重新完整安装。没有为通过验收而改写旧环境元数据。

已在本机保存 profile、最终 doctor JSON、各步日志及目录清单。验收中另有两次长时间停顿后的安装超时，失败日志保留后在新目录重试；最终两个项目均为 ready。7个临时验收环境的递归清理被自动审批以“blocked by policy”拒绝，约2.10 GiB的临时环境仍保留；没有将未完成的清理登记为成功。旧研究环境和历史账户未动。

## 复现文档

- [Studio工作台](https://github.com/PureSaber/quant-studio/blob/main/README.md)：本机服务、模板和基金输入目录设置。
- [前向流程](https://github.com/PureSaber/quant-pipeline/blob/main/docs/FORWARD_DAILY.md)：配置身份绑定、状态、显式运行和恢复边界。
- [成本诊断](https://github.com/PureSaber/quant-report-hub/blob/main/docs/EXECUTION_COST_DIAGNOSTICS.md)：报价、成本策略、输出和重算命令。
- [组合穿透](https://github.com/PureSaber/quant-risk-monitor/blob/main/docs/PORTFOLIO_EXPOSURE.md)：NAV权重、可得时点、覆盖率与重叠定义。
- [固定独立环境](https://github.com/PureSaber/quant-workspace/blob/main/docs/RUNTIME_READINESS.md)：profile、只读doctor、新环境安装与失败日志。

## 验收范围及未完成的外部条件

本轮使用仓内合成夹具和临时测试目录，没有下载新的真实行情、基金净值或大体积 L2 数据。真实历史时点、授权条款、申赎确认/到账凭证仍须通过已有导入和核验入口补足。对账成功不等于凭证真实性或真实业务认证，数据哈希也不证明数据来源。

成本报告是相对于订单接受时报价的历史诊断，包含等待期间行情变化；不宣称纯市场冲击或真实执行成本已经校准。最小订单组数是指定门槛，不是统计独立性证明。风险预测摘要不改模型参数、风险限额或账户；持仓重叠也不是收益相关性或分散化证明。

环境就绪只覆盖文档明确列出的源码、锁和元数据检查，不认证包字节或供应链，也不代替各应用集成。既有发行清单、冻结研究环境和历史账户没有被升级或覆盖。

没有恢复先前暂停的 ETF 自动观察，没有新增计划任务，没有开始真实交易或连续 L2 采集。自然前向需要真实日期逐日推进；物理独立归档仍需额外介质；宿主 iframe 问题仍需宿主侧修复，独立页面入口继续可用。
