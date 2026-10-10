# 研究操作补充开发验收

本轮接续Studio研究工作区开发，范围为用户选择的新方向1、2、3、4、6、8、9、10，以及此前的发布升级、迁移复现和问题导向Notebook模板。所有测试使用隔离目录与合成/仓库自带离线数据；未更新现有服务、冻结环境、账户或历史研究产物。

## 功能落点

| 方向 | 交付 | 验收方式 |
| --- | --- | --- |
| 1．数据导入 | CSV/TSV/Parquet原件留存、显式字段映射、编码与分隔符重试、全量质量报告 | 真实浏览器上传、独立QDK进程导入、质量负例与失败回执 |
| 2．统一数据接口 | 固定数据版本、用途与scope；QDK读取和Notebook冻结读取器 | 实际登记数据、独立Notebook解释器执行、快照/脚本/环境篡改拒绝 |
| 3．刷新与变化 | 父版本、字段结构变化提示、版本差异、失败刷新保旧版 | 新旧版本差异测试；字段变化阻止直接复用映射 |
| 4．批量实验 | 参数网格、候选上限、预检后执行、幂等派发、显式重试 | 真实crypto离线样例两候选；重复提交、重启、中断与profile冻结回归 |
| 6．研究质量 | 自动数据规则、用途准入、人工研究判断提示 | 重复键、日期、范围、PIT、篡改等负例；模板区分自动与人工检查 |
| 8．结果交互 | 2至4条可比曲线、显隐、范围缩放和CSV导出 | 浏览器验证四条曲线、隐藏剩三条、缩放、CSV公式字符处理 |
| 9．资源管理 | 批次任务排队时间、运行时间、进程树RSS、输出大小、软预算 | 实际子进程与离线执行记录；超限终止和采样不可用回归 |
| 10．新手引导 | 根据真实持久化状态提供配置→导入→准入→项目→Notebook→实验入口 | 空工作区/已有记录/异常记录/HTTP/手机页面验收 |
| 问题导向模板 | 数据质量探索、价格收益与观测缺口、历史财务可得性 | 默认行为兼容、草稿不覆盖、真实统一读取与Notebook执行 |
| 发布与迁移 | 精确源码/锁/环境绑定、实际验收、指针CAS、显式allowlist迁移 | 新目录clone/环境验收、固定产物哈希、迁移恢复后的样例结果一致 |

## 独立复核

验证负责人仅执行只读审查与隔离测试。复核发现的问题按根因修复，并加入先失败再通过的回归：

- 迁移生成文件可能覆盖payload：保留路径、大小写碰撞与Windows路径别名拒绝；生成文件独占创建；全部写入后再次核对payload。
- 迁移凭据漏检：拒绝`.env.*`、常见带前缀密钥赋值、Authorization和带密码连接URI。独立构造且摘要自洽的归档在verify和restore阶段同样被拒绝；占位引用保持可迁移。
- 严格日线用途不能依赖用户自行声明的主键，需核验所选范围内的自然键。
- CSV重复表头和字段宽度错位：在pandas自动改名或推断索引之前拒绝；实际构造的重复`close_px`和多字段行均失败，原件与失败回执保留。
- 严格用途字段类型：`date:string`不能绕过日期规范要求；错误类型以`purpose_required_type`阻断。
- 空日线刷新：新版本质量被阻断，`latest`保持旧有效版本；严格用途的零匹配范围被拒绝。
- 远程Linux暴露内存采样测试的启动竞争：原测试在子进程尚未完成初始化时就拿到非零RSS并断言失败。测试现等待子进程完成分配并输出`ready`，再采样；子进程通过stdin保持存活，原断言不降低。此次仅修测试同步，没有修改资源采样实现。

## 实际证据与边界

真实浏览器脚本为Studio的`integration/research_operations_browser.cjs`。它在新建隔离目录启动临时本机服务，退出时关闭；验证上传→映射→质量报告→项目连接、四曲线交互、CSV导出，以及390px宽度的导入、引导和批次页面。

本地证据目录：`H:/Documents/ChatGPT/temp/puresaber-quant-platform/.maintenance/research-operations-20261010/`。最终浏览器截图、`browser-result.json`和下载CSV位于其`browser-final/`目录，完整Studio测试记录为`studio-final-junit.xml`。证据中的数据为合成数据，不代表市场收益、交易可行性或市场数据认证。

资源预算目前只覆盖批次任务，采用轮询式软限额；不等同于操作系统级资源隔离。Notebook冻结解释器路径和环境身份，不打包解释器。全量读取受固定scope约束，匹配数据会进入内存。数据规则不能自动证明供应商PIT声明真实，也不能代替未来信息、选择偏差和多重检验的人工判断。

发布激活只切换受管候选指针，不自动重启服务或回滚业务数据。迁移状态分别记录完整性、缺失配置、环境重建与研究复现，不能把哈希通过解释为所有研究已复现。凭据扫描用于常见误打包拦截，allowlist仍需逐项审查。

## 首版验收（2026-10-10）

| 范围 | 实际结果 |
| --- | --- |
| Studio全量及所有可选真实环境 | 376通过、无跳过，84.72秒；ruff检查、格式检查、diff检查通过 |
| QDK全量与覆盖率 | 888通过、2跳过；纯分支覆盖率4682/5744=81.51%，达到80%门禁；ruff检查、150个文件格式检查、diff检查通过 |
| Workspace全量与覆盖率 | 184通过、1跳过，125.62秒；总覆盖率86.41%；stack_manifest纯分支90.78%，m7_certification纯分支94.06% |
| Workspace静态最终复核 | `68cd33b`工作树干净；ruff检查通过，20个文件格式检查通过；最终格式提交未改变行为 |
| 数据负例独立复验 | 数据准入/快照27项通过；独立重做原始重复表头、多字段错位、错误日期类型、缺省主键冲突、空刷新五个复现均关闭 |
| 最终浏览器 | 所有7组检查通过，进程正常退出；查看了最终桌面结果截图 |
| CI时序修复补核 | `f3952f6`资源测试6项通过，独立重跑6项通过；静态检查通过，最新Linux和Windows单元CI确认通过 |

Workspace的1项跳过为当前Windows主机不可创建目录符号链接；远程Linux矩阵负责执行该路径。Studio最终全量启用了独立Notebook、QDK、Agent和crypto离线解释器，因此不存在将可选集成跳过当作通过的情况。

验证负责人已在QDK最终提交重新执行已报负例与OHLC字符串类型案例，确认阻断全部闭环；Workspace与Studio集中复核也没有剩余已确认阻断。

## 首版提交与依赖（2026-10-10）

| 仓库 | 首版提交 | 首版草稿PR |
| --- | --- | --- |
| quant-data-kit | `0dae9b570cf23ee4f8c1091699194b4ec03cb2da` | [#37](https://github.com/PureSaber/quant-data-kit/pull/37) |
| quant-workspace | `68cd33b` | [#53](https://github.com/PureSaber/quant-workspace/pull/53) |
| quant-studio | `f3952f6b6a17179960fd4d01ef5d71fd1ab360d8` | [#30](https://github.com/PureSaber/quant-studio/pull/30) |

Studio#30以`codex/research-workspace-v2`为base，叠加在另一开发对话的[Studio#28](https://github.com/PureSaber/quant-studio/pull/28)之上，避免重复审查其研究工作区改动。Research workspace CI固定上述QDK完整提交，使用独立Notebook/QDK/Agent环境执行真实读取；跨平台crypto上游CI另执行实际两候选批次测试。

首版交付时所有PR保持草稿，未合并或部署。以下记录用户要求继续处理后的主线同步、独立复核和合并收尾，不覆盖首版证据。

## 主线同步与合并收尾（2026-10-11）

本轮主线已增加衍生品能力，原功能分支需要重新整合，且Studio#30依赖尚未合并的Studio#28。处理保留原提交历史，以merge commit同步主线，再按Agent助手、Studio前置、数据准入与交付迁移、Studio整合的依赖关系合并。Studio#30已改为直接合入`main`。

Workspace唯一冲突为`src/quant_workspace/capabilities.json`。逐字段整合主线24仓、衍生品能力与关系，以及本轮delivery/transfer能力、CLI入口、契约和证据。独立复核确认两个父提交的能力资产无缺项、41条关系包含双方全部关系、14仓M8发行scope不变；旧release/transfer实现和主线衍生品profile均保持原样。未以整个文件选择一方覆盖另一方。

| 验证范围 | 同步后的实际结果 |
| --- | --- |
| Agent前置 | 独立10项测试通过；真实CLI离线子进程网络尝试为0 |
| Studio前置 | 全量332项通过；ruff检查及95文件格式检查通过 |
| Studio整合 | 全量381项通过，零失败、零跳过；启用真实Lab/Notebook、QDK、Agent和crypto两候选批次；独立针对37项通过；ruff检查及116文件格式检查通过 |
| Studio主线接合 | `1eac1a90bcc3039bfc74a5dff31e6960c4b59a9f`与已测`18597d3c4900b21e312c54b9b8247877a07b4d82`源码树一致，仅接合前置PR的主线合并提交；随后`651db4a586ee0ef3b19de3a84ecac6ca22ef262b`仅修复以下独立集成测试读取器，应用源码未变 |
| QDK | 全量894项通过、2项跳过；纯分支覆盖4804/5934=80.96%，达到80%门禁；独立intake与derivatives联合31项通过；旧intake实现及新衍生品模块完整保留 |
| Workspace | 全量184项通过、1项跳过；覆盖率86.41%，stack_manifest纯分支90.78%、m7_certification纯分支94.06%；定向97项通过、1项跳过；独立能力目录/升级/迁移37项通过 |
| 真实浏览器 | 再次完成上传→映射→导入→质量报告→项目连接、四曲线显隐/缩放/CSV导出、390px页面无横向溢出及无浏览器错误 |

本轮JUnit位于本地证据目录的`parent-main-sync-junit.xml`和`operations-main-sync-junit.xml`；浏览器证据位于`browser-main-sync/`。QDK和Workspace覆盖率来自各独立工作树的`coverage.json`。独立验证负责人只读复核以上最终提交，没有剩余已确认阻断。原有跳过原因和离线验证边界不变。

最后一轮Linux CI曾暴露独立账本验证子进程在完整打印JSON后退出崩溃，`returncode=-6`、`terminate called without an active exception`，见[失败job](https://github.com/PureSaber/quant-studio/actions/runs/38095446874/job/114340275514)。检查锁定的pandas2.3.3/pyarrow25.0.1实现确认，原`pd.read_parquet`单文件读取仍启动dataset扫描；现象与[Arrow#34314](https://github.com/apache/arrow/issues/34314)记录的解释器退出和后台线程清理问题一致。仅将`integration/test_fixture_upstream.py`中oracle改为`with ParquetFile(..., pre_buffer=False)`，读取及转换均禁用线程；保留`ArrowDtype`、逐单元格比较、时区、文件哈希与退出码断言。没有添加sleep、重试、忽略异常或修改冻结上游依赖。

同版本Windows原四个crypto集成案例全部通过（29.44秒，`crypto-oracle-sync-junit.xml`）。独立复核确认四案例新旧子进程输出完全一致、均正常退出且无stderr；32次DataFrame精确比较通过，覆盖156个空值，保留类型和时间语义。本地WSL因已有磁盘挂载错误无法启动；修复后的[远程矩阵](https://github.com/PureSaber/quant-studio/actions/runs/38096100829)中Linux与Windows crypto实际CLI及真实批次检查均通过。本修复消除oracle自身末尾的异步扫描，不声称解决上游QLab或Arrow的所有同类风险。

| PR | 最终功能提交 | 合并记录 |
| --- | --- | --- |
| [Agent#15](https://github.com/PureSaber/quant-agent/pull/15) | `887bec50d530a06171756204281c7322a4855d3c` | 已合入`master`，`474528d4a9ba005e2907651166951753dbba3178` |
| [Studio#28](https://github.com/PureSaber/quant-studio/pull/28) | `40ae0ee8933b9c36cb99c00cd855192f1cc7b2bc` | 已合入`main`，`d28adb84f73004b4dbfc28eb8415f2417f47c9e1` |
| [QDK#37](https://github.com/PureSaber/quant-data-kit/pull/37) | `902eb095f922429f327d7c713adde79a6787839c` | 已合入`main`，`2e1596e1c9bfde3e3a1b4e0dbe51974324ccc668` |
| [Workspace#53](https://github.com/PureSaber/quant-workspace/pull/53) | `7aeea6c85d17c04a091f8a36e707b4c938b6367b` | 已合入`main`，`959bb91d3e5426a394a08f9ebea6170b029c3462` |
| [Studio#30](https://github.com/PureSaber/quant-studio/pull/30) | `651db4a586ee0ef3b19de3a84ecac6ca22ef262b` | 已合入`main`，`25baa2f7550507d50c6f7ae280f06e465ac25688` |

上述5个代码PR已全部合并；合并前各自最终head的全部检查均通过，其中Studio#30为24项、QDK#37为6项、Workspace#53为9项。Studio真实研究CI固定QDK功能提交`902eb095f922429f327d7c713adde79a6787839c`，并使用独立环境执行数据读取。所有合并遵循仓库保护规则，并匹配实际验收的head提交；没有管理员绕过、force push或虚构人工Approve。代码入主线与生产运行是不同阶段：本轮没有切换现有服务、升级冻结环境或执行业务数据迁移。
