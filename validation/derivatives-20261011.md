# 衍生品研究工程验收 · 2026-10-11

本轮目标是让工作台支持期权及海外期货研究，验证数据→配置→预检→运行→报告→重开与复现的开发链路。不是筛选盈利策略，不进行真实交易。只新增 quant-options 一个私有仓库，其余能力扩展既有仓库。

|层|完成能力|实现 PR|
|---|---|---|
|数据|不可变合约/行情包、严格身份与可得时间、CSV导入、受限Dataway/Databento采集|[QDK #36](https://github.com/PureSaber/quant-data-kit/pull/36)|
|账户|精确金额、幂等多腿成交、保证金、逐日结算、到期/行权及因果回放|[QExec #27](https://github.com/PureSaber/quant-execution/pull/27)|
|期权|BSM/Black-76/CRR、IV/Greeks、链和观察切片、多腿情景及回放|[Options #1](https://github.com/PureSaber/quant-options/pull/1)|
|海外期货|具体月份合约、期限结构、跨月价差、到期/成交量换月|[Futures #15](https://github.com/PureSaber/quant-futures-spread/pull/15)|
|工作台|中文配置、数据集采集、不可变方案、预检、异步任务和报告下载|[Studio #29](https://github.com/PureSaber/quant-studio/pull/29)、[预检详情修复 #31](https://github.com/PureSaber/quant-studio/pull/31)|
|工作区|24仓能力目录、新目录独立安装、精确提交与锁文件字节校验|[Workspace #54](https://github.com/PureSaber/quant-workspace/pull/54)|

操作说明集中在 [Studio 衍生品指南](https://github.com/PureSaber/quant-studio/blob/main/DERIVATIVES.md)，安装说明集中在 [独立环境配置](https://github.com/PureSaber/quant-workspace/tree/main/profiles/derivatives-research)，避免多份文档重复参数后失同步。

## 验收证据

- QDK：869 项通过、2 项跳过；Linux Python 3.10/3.11/3.12、Windows 3.12及CodeQL通过。
- QExec：382 项通过，原账户回归及新结算/行权/回放路径通过；Python 3.10/3.11/3.12及CodeQL通过。
- Options：13 项通过，含独立定价数值、平价、Greeks差分、IV反解、CLI和损坏拒绝；分支计入覆盖率85.07%。Linux/Windows锁安装及CLI通过。
- 海外期货：6 项通过，分支计入覆盖率83.41%；Linux/Windows通过。原认证子路径Python 3.10/3.11/3.12回归通过，旧依赖未升级。
- Studio：312 项回归及2项实际上游集成，共314项通过。集成覆盖行情分析/账户回放、自定义初始资金54321、只读输入、哈希/分录检查及损坏输入拒绝，并打开两种预检详情核对258/43行情行数。
- Workspace：156 项通过、1 项已有跳过；历史M8 14仓清单保持不变。

浏览器期权任务：通过页面生成12合约258行演示数据，方案 `2a0adef9f3374f139b27744c5ac73372`，版本 `fabadc14cbccfcdab2ce4c2836f59cc896f7539f82e9aa6d070c3d57e3742ee2`，预检通过、运行 `96588e1034ae41b598b436490e6583e8` 成功，期初54321，期末54323.4 USD。数字为合成工程样例；报告包含IV切片和多腿情景图。390像素浏览器视口检查未出现页面横向溢出，这不是新增模块的真实手机验收。

海外期货通过页面保存初始资金65432的换月方案 `e32f38958a6e4f119a7816586d0a6f9f`，版本 `7c157110f4e467e55b632c1ebd93b5ce1056773e3cd49c31eaf63ef990575651`，原生预检通过，运行 `1e914313f64c4c2a8791641c71074e1d` 成功，期末65461.6 USD，属于合成工程样例。

## 数据实测与适用范围

经已授权的汇升Dataway接口进行了小规模只读探测：2025-04-18期权行情16712行，但指定合约的描述信息查询未取得有效记录；不能凭行情代码编造乘数、到期条款和标的价格。2025-04-17国际期货表取得9行连续/参考代码且成交量为0，不能作为具体月份合约的可成交换月数据。

真实来源接口能访问不等于完整研究输入已齐。完整真实期货回放需要明确交割合约和结算；期权链需要完整条款和同步标的价格。没有执行付费下载，没有把合成数据标记为市场数据。供应商原始响应和本机私有访问资料留在本机，未提交公共GitHub。

当前采用日频下一观察开盘价成交模型、显式费用/跳数滑点及逐合约保证金。未包含SPAN/组合保证金抵扣、跨币种账户、负价格成交、奇异期权或自动美式最优行权。IV图展示观察切片而非拟合无套利曲面。产物核验检查哈希与逐币种分录平衡，不等于独立市场认证。

## 保留与部署

旧方案、旧数据、历史前向账户及认证fixture环境保留。服务继续使用原Tailscale HTTPS地址、登录和受控访问范围。操作系统重启/重新登录的自启动验收仍按用户要求暂缓，不计入完成项。实际ROG/Android跨设备基线见 [此前工作台验收](workbench-20261010.md)。

PR评审记录明确为实施者自审及自动检查，没有声称独立人工审查。

## 正式服务验收

服务安装到 `D:/qe4/release-final/env`，应用使用非editable wheel；源码、共享依赖与锁文件SHA固定于 Workspace 的 `profiles/derivatives-research/stack.json`。全新目录安装及 `pip check` 通过，旧认证期货解释器仍使用原依赖，额外复查211项通过、1项已有跳过。部署前验证原有16份方案可读取，随后新增两份合成演示方案。

2026-10-11 00:37（北京时间），通过原有 HTTPS 服务，使用现有CA并保留主机名校验完成：未登录跳转、登录安全Cookie、保存版本的预检/运行提交、异步任务完成、预检详情打开、结果列表重开、净值/上游JSON/完整HTML下载、退出后会话失效。正式验收任务如下：

|研究类型|已保存方案|预检记录|运行记录|
|---|---|---|---|
|期权组合|`e030869bb5814cb1860a922bb8c5fa03`|`7df1b41649dc4ffd9771f2ac5fa7a0cb`|`37f3cdc8c0294e62a99580e4ddca3c9c`|
|海外期货换月|`65fac4d61ac8481da554e8c5bd66cce0`|`702805121f9149c0bbf1f47ec23d0a45`|`b0212fae921b4a8d8c57165ac1daf7e4`|

两次正式运行的产物哈希和逐币种分录平衡再次验证通过。只生成工程演示结果，不发送真实订单。后续使用真实数据时须重新经过输入完整性预检。

内置浏览器的本机系统代理原先截获私网地址，已添加仅该服务IP的代理例外；随后内置浏览器报告不信任私有CA，未跳过警告。此次新模块的界面操作在localhost浏览器完成，正式HTTPS路径通过上述CA校验的HTTP验收完成，不将二者混称为新的跨设备或手机验收。此前ROG/Android基线继续保留。

服务已平滑重启，最新健康检查通过、异常重启次数为0；重复启动会识别现有监护进程。Windows登录启动入口保留隐藏窗口并指定进程级ExecutionPolicy Bypass，没有修改全局脚本策略。部署脚本首次等待健康状态25秒，早于监护30秒轮询而超时；随后正式HTTPS及新健康检查通过，不是服务崩溃。实际系统重启验收继续暂缓。

部署前备份：`D:/qe3/backups/workbench-20261010T162156Z-f03e6c44.zip`，SHA-256 `4bdbbf73ad5bb0f7019b3496a7fc38823650a142095fed40d941ddb9ac232544`。部署后备份：`D:/qe3/backups/workbench-20261010T163750Z-d5bc27e2.zip`，SHA-256 `a431513e4e20ade00395e9e724eb749fd5bdf54f7e50e87f32500fbaea3bb1cf`，1990个文件，完整性验证通过。原配置和启动项回滚副本保存在本机 `D:/qe4/deployment-backup`，不进入公共仓库。

工程证据归档：`F:/QuantArchive/derivatives-research-20261011/engineering-evidence.zip`，SHA-256 `bd2ea2ce4f0361d33bee9d93dead61b074f5fe3687949c031cc2458e2f4e65e9`。包含86项测试、浏览器截图、演示输入、报告、固定版本、HTTPS验收和上述备份等文件；归档内manifest逐项哈希核验通过。该归档不含私密凭据或供应商原始响应。最终文档与工作区PR合并回执另存同目录 `closure.json`，避免修改已冻结归档。
