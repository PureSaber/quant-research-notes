# 衍生品研究工程验收 · 2026-10-11

本轮目标是让工作台支持期权及海外期货研究，验证数据→配置→预检→运行→报告→重开与复现的开发链路。不是筛选盈利策略，不进行真实交易。只新增 quant-options 一个私有仓库，其余能力扩展既有仓库。

|层|完成能力|实现 PR|
|---|---|---|
|数据|不可变合约/行情包、严格身份与可得时间、CSV导入、受限Dataway/Databento采集|[QDK #36](https://github.com/PureSaber/quant-data-kit/pull/36)|
|账户|精确金额、幂等多腿成交、保证金、逐日结算、到期/行权及因果回放|[QExec #27](https://github.com/PureSaber/quant-execution/pull/27)|
|期权|BSM/Black-76/CRR、IV/Greeks、链和观察切片、多腿情景及回放|[Options #1](https://github.com/PureSaber/quant-options/pull/1)|
|海外期货|具体月份合约、期限结构、跨月价差、到期/成交量换月|[Futures #15](https://github.com/PureSaber/quant-futures-spread/pull/15)|
|工作台|中文配置、数据集采集、不可变方案、预检、异步任务和报告下载|[Studio #29](https://github.com/PureSaber/quant-studio/pull/29)|
|工作区|24仓能力目录、新目录独立安装、精确提交与锁文件字节校验|[Workspace #54](https://github.com/PureSaber/quant-workspace/pull/54)|

操作说明集中在 [Studio 衍生品指南](https://github.com/PureSaber/quant-studio/blob/main/DERIVATIVES.md)，安装说明集中在 [独立环境配置](https://github.com/PureSaber/quant-workspace/tree/main/profiles/derivatives-research)，避免多份文档重复参数后失同步。

## 验收证据

- QDK：869 项通过、2 项跳过；Linux Python 3.10/3.11/3.12、Windows 3.12及CodeQL通过。
- QExec：382 项通过，原账户回归及新结算/行权/回放路径通过；Python 3.10/3.11/3.12及CodeQL通过。
- Options：13 项通过，含独立定价数值、平价、Greeks差分、IV反解、CLI和损坏拒绝；分支计入覆盖率85.07%。Linux/Windows锁安装及CLI通过。
- 海外期货：6 项通过，分支计入覆盖率83.41%；Linux/Windows通过。原认证子路径Python 3.10/3.11/3.12回归通过，旧依赖未升级。
- Studio：312 项回归通过；两项实际上游集成分别覆盖行情分析/账户回放、自定义初始资金54321、只读输入、哈希/分录检查及损坏输入拒绝。
- Workspace：156 项通过、1 项已有跳过；历史M8 14仓清单保持不变。

浏览器期权任务：通过页面生成12合约258行演示数据，方案 `2a0adef9f3374f139b27744c5ac73372`，版本 `fabadc14cbccfcdab2ce4c2836f59cc896f7539f82e9aa6d070c3d57e3742ee2`，预检通过、运行 `96588e1034ae41b598b436490e6583e8` 成功，期初54321，期末54323.4 USD。数字为合成工程样例；报告包含IV切片和多腿情景图。390像素浏览器视口检查未出现页面横向溢出，这不是新增模块的真实手机验收。

海外期货通过页面保存初始资金65432的换月方案 `e32f38958a6e4f119a7816586d0a6f9f`，版本 `7c157110f4e467e55b632c1ebd93b5ce1056773e3cd49c31eaf63ef990575651`，原生预检通过。

## 数据实测与适用范围

经已授权的汇升Dataway接口进行了小规模只读探测：2025-04-18期权行情16712行，但指定合约的描述信息查询未取得有效记录；不能凭行情代码编造乘数、到期条款和标的价格。2025-04-17国际期货表取得9行连续/参考代码且成交量为0，不能作为具体月份合约的可成交换月数据。

真实来源接口能访问不等于完整研究输入已齐。完整真实期货回放需要明确交割合约和结算；期权链需要完整条款和同步标的价格。没有执行付费下载，没有把合成数据标记为市场数据。供应商原始响应和本机私有访问资料留在本机，未提交公共GitHub。

当前采用日频下一观察开盘价成交模型、显式费用/跳数滑点及逐合约保证金。未包含SPAN/组合保证金抵扣、跨币种账户、负价格成交、奇异期权或自动美式最优行权。IV图展示观察切片而非拟合无套利曲面。产物核验检查哈希与逐币种分录平衡，不等于独立市场认证。

## 保留与部署

旧方案、旧数据、历史前向账户及认证fixture环境保留。服务继续使用原Tailscale HTTPS地址、登录和受控访问范围。操作系统重启/重新登录的自启动验收仍按用户要求暂缓，不计入完成项。实际ROG/Android跨设备基线见 [此前工作台验收](workbench-20261010.md)。

PR评审记录明确为实施者自审及自动检查，没有声称独立人工审查。
