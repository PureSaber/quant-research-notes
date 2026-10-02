# 2026-10-01维护验收与r4前向登记

本轮修复公司行动重复采集与冻结前缀的契约冲突，更新研究集成源码及依赖，补齐Agent本地环境。按用户选择，旧账户及失败证据完整保留，在新环境验收后另行登记r4。

本日后续11个应用仓的正确性、安全与报告完整性修复另见[应用修复发布验收](APPLICATION_FIX_RELEASE.md)。10月2日已补齐独立review环境并完成两种账户模式、双腿fixture及QDK跨仓验收，最终发行提交及证据以该记录为准；软件发布状态与市场数据GA状态分别判定。

## 根因与修复

旧实现每次采集都把五条既有分红的`captured_at`替换为最新抓取时刻，即使完整记录没有改变，也会使前向输入前缀变化。QDK现在区分完整记录版本的首次receipt与本次观察回执：相同版本继承经哈希验证的父快照receipt，本次原始规范化响应另存`action-observations.json`并纳入证据哈希。

版本比较包含经济字段、公告及支付日期、事件身份、provider和来源记录。新增、删除、来源或经济内容修订仍产生差异；无效、未来或倒退receipt被拒绝。Pipeline的冻结输入门禁没有放宽，也没有改写历史快照。实现见[QDK#28](https://github.com/PureSaber/quant-data-kit/pull/28)。

首次跨仓测试正确拒绝了晚于测试主表实际核验时刻的cutoff；[QDK#29](https://github.com/PureSaber/quant-data-kit/pull/29)修正了测试日期，生产源码没有变化。原失败CI保留在[验收记录](evidence/local-integration.json)。

## 验证结果

|范围|实际检查|
|---|---|
|Agent本地维护环境|从锁安装72个包，依赖兼容；55项测试通过，覆盖率84%，标准适配器纯分支14/14|
|QDK|全量614项通过；外部集成回归在单仓环境按依赖可用性跳过，在完整工作台中19项全部执行并通过；Linux/Windows及Python3.10–3.12的CI通过|
|Workspace|100项本地测试通过；依赖输入、锁哈希及10种解释器/平台组合检查通过；跨仓矩阵见[Workspace#19](https://github.com/PureSaber/quant-workspace/pull/19)|
|账户与恢复|独立折、连续账户各4个合成候选成功，续跑结果不变；连续路径缓存指标被修改时拒绝恢复|
|冻结软件样例|独立fixture环境通过精确依赖身份核验，期货2候选、Crypto3候选成功，原fixture锁保持不变|
|真实开发回放|固定4候选成功，500项产物哈希通过；base全部参数与r3一致，结果未因本次维护改变|

13项研究源码按精确提交安装到新目录，旧环境没有升级。QDK固定`6ec373afae94daa572263501e2a3c5c586cb3271`，与其主线合并提交`c0985c0c70315c71314f0f3179805db86981d00c`的文件树一致。新外部锁SHA-256为`060196207ab7303d2e4002a5642a81ba23a3249f6efb1590d04e8dd9147fafcc`。本机GitHub工件直连失败后，安装使用仓库内SHA-256完全一致的原AKShare工件；没有更换版本或修改正式锁，后续`pip check`和工作台`verify`通过。远端CI使用正式URL安装。

## 真实重复采集

2026-10-01T03:33:32.928542200Z以原`live_public_api`来源重新获取截至9月30日的数据：五条行动全部不变，原始价、复权价和基准修订数均为0。完整lineage及截至9月30日的输入前缀一致。

消费视图保留9月30日的真实首次receipt，今天的实际采集时间保存在独立回执中。新快照为`sha256-f0e51a309d65afcf8a080c66675a981f03754a9d9cebb49f1b621acf3fd843e0`。这次检查是重复采集验收，没有运行`paper observe`。详见[真实采集核验](evidence/live-repeat-verification.json)。

## 新账户

- 账户：`etf-risk-forward-20261008-r4`。
- 实际登记时刻：2026-10-01T11:35:34.708103+08:00。
- 观察区间：2026-10-08至2026-12-31，初始输入截止日2026-09-30。
- 定义SHA-256：`544aef91d598b939a2da9dc6d01da30ba630349f1edfb411a805ed60b926da2d`。
- 固定原base候选，登记时0次attempt、0次观察。旧r3的4个本地文件逐一核对，字节哈希未变。

初始输入是9月30日真实快照的逐文件哈希一致副本，共263个文件。复制不代表重新采集；后续真实重复采集也已证明与该登记前缀一致。旧账户9月28日至30日没有成功观察，不能补入新账户。

本次开发回放仍为3折189个测试日：base净收益-3.1909%、最大回撤14.6810%、Sharpe为-0.1873；buy_hold为+7.3811%。不支持base优于对照，不因为收益选择新参数。[开发回放验证](evidence/development-verification.json)与[完整登记摘要](evidence/registration-receipt.json)记录真实哈希和冻结身份。

日常操作以[新运行手册](FORWARD_RUNBOOK.md)为准。9月26日目录中的active回执和旧手册只表示历史登记；旧账户、原始文件及[9月30日失败证据](https://github.com/PureSaber/quant-research-notes/blob/16726b41e5dbdf11dbfb5af31e8c9c835eb65165/validation/risk-pit-20260926/evidence/forward/20260930T141242Z/README.md)均保留。

## 仍未完成

独立归档及恢复、Crypto八流真实连续30日、授权国内L2仍被资源条件阻断；完整Barra所需宽截面PIT数据与校准也未完成。下一步需要的数据、授权及验收条件见[资源清单](RESOURCES.md)。本轮不改变市场数据GA状态，不启动长期采集，也不构成策略有效性或实盘认证。
