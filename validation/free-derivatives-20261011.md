# 免费海外衍生品数据接入 · 2026-10-11

本阶段扩展现有研究工作台，无新增仓库。目标是接入与工程研究能力，不是策略盈利验收。

| 来源 | 本次真实输入 | 已验证的能力 |
| --- | --- | --- |
| Cboe VX | 2025-02-19、2025-03-18 到期合约；2025-01-08 至 10 | 6 行日线、期限结构与价差、明确保证金假设的回放 |
| NSE 指数期货 | NIFTY25FEBFUT；同一三日窗口 | 3 行日线、历史每手 75、分析与模型回放 |
| NSE 指数期权 | NIFTY25JAN23500PE；同一三日窗口 | 3 行日线、历史每手 25、IV / Greeks / 情景分析 |
| Deribit 历史期权 | BTC-31JAN25-100000-C；同一三日窗口 | 381 笔成交、3 行聚合数据、美元折算分析 |
| Deribit 当前快照 | BTC-30OCT26-80000-C/P | 两个合约的参考估值与组合风险输入；保留采集区间及原始时间 |

网页增加公开源采集表单、两个新模板；选数据集创建方案时自动带入合约/品种，默认
只分析。旧模板文件保持原定义，避免使不可变方案版本失效。采集清单记录请求范围、
原响应摘要、排除记录、历史手数和使用限制。原始市场数据留在本机，不进入 Git。

边界：Cboe/NSE 当前接入为日线、具体合约、最多 32 天一次；不自动拼接长期历史。
日线发布时间和首次观察上市时间是回顾研究假设，不是 PIT 认证。HTTP 404 仅披露
缺文件，不能直接解释为休市。零成交日线不补造行情。合约到期后最终交割不在本批输入范围。
NSE 支持指数 F&O，不支持股票实物交割合约。

Deribit BTC/ETH 原生权利金折算美元仅用于分析；币本位结算、抵押与反向账户模型尚未
实现，因此在数据层、应用预检和共享回放入口阻止账户回放。历史各腿最后成交不同步时
不能当同期行情使用。当前参考估值也不是原子化、可成交买卖报价。

验证：QDK 901 passed / 2 skipped，Execution 383 passed，Options 14 passed，
海外期货子项目 6 passed，Studio 324 passed；新增两项原生 CLI 集成通过。
浏览器完成 Cboe 采集 → 数据登记 → 自动合约 → 保存方案 → 运行 → 报告显示。

使用说明以 [Studio 免费源指南](https://github.com/PureSaber/quant-studio/blob/main/FREE_SOURCES.md)
为准，文件导入与单位口径见 [QDK 适配器说明](https://github.com/PureSaber/quant-data-kit/blob/main/docs/free-derivatives.md)。
安装提交与依赖锁以 [固定组合](https://github.com/PureSaber/quant-workspace/blob/main/profiles/derivatives-research/stack.json)
为准，不在多份文档中复制可变默认配置。

部署与验收：新运行环境按固定提交和完整依赖锁独立重建，非 editable 安装与
`pip check` 通过。生产服务保留原 Tailscale、HTTPS CA、登录和目录配置。
五组输入均通过生产 HTTPS 的采集、方案保存、预检、执行、结果重新打开及 CSV/报告下载；
18 个原有方案保持原版本可读，新增五个真实数据研究样例。登录 Cookie 属性和退出后
访问撤销验证通过。新旧服务切换前后分别备份；本次未重启操作系统，也没有重复要求
用户验收已经完成的跨设备连接。

实现与验收 PR（CI、合并状态以链接为准）：
[数据层 #38](https://github.com/PureSaber/quant-data-kit/pull/38)、
[账户层 #28](https://github.com/PureSaber/quant-execution/pull/28)、
[期权 #2](https://github.com/PureSaber/quant-options/pull/2)、
[期货 #16](https://github.com/PureSaber/quant-futures-spread/pull/16)、
[工作台 #33](https://github.com/PureSaber/quant-studio/pull/33)、
[冻结安装 #55](https://github.com/PureSaber/quant-workspace/pull/55)。
PR 中记录实施者自审，不冒充独立第三方审批。

验证记录保留于本机 `D:/qe5/evidence`：`sources.json`、`frozen-install.log`、
`deployment-precheck.json`、`production-https.json`、备份清单及浏览器截图。
冻结安装引用经过验收的功能提交；主分支并行新增的数据准入或 Notebook 工作不自动
改变本次已安装的冻结环境，需在下一次组合升级中显式验证。
