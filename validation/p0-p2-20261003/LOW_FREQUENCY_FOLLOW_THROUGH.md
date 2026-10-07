# 2026-10-07低频维护后续验收

本批继续界面与操作体验、低频数据和账本一致性、跨仓兼容及运行维护。可独立完成的软件修复、依赖维护和文档同步已交付；完整真实业务及新的视觉验收仍有明确缺口。旧P0—P2总目标保持进行中，不新增策略研究、自然前向或高频部署。原ETF自动化仍为`PAUSED`。

[机器状态摘要](evidence/low-frequency-follow-through-20261007.json)将软件证据、真实净值检查和未完成业务验收分别记录。

## 逐项签收

|项目|实际完成内容|验收状态与限制|
|---|---|---|
|界面与新手流程|成功报告新增“独立打开完整报告”；同步SPEC中的11模板、10原生预检、设置保存与重启、只读账户、失败隔离及账本核验|234项Studio测试、固定上游Linux/Windows集成和HTTP流程通过；本轮未完成新视觉截图|
|报告嵌入问题|保留同一原生报告路径、iframe和相对链接，提供独立打开入口|静态最小复现继续支持宿主环境方向；具体MutationObserver注入调用栈和修复仍未确认，见[诊断记录](FUND_EMBED_DIAGNOSTIC.md)|
|低频净值一致性|真实样本暴露源日增长率漏分红的问题；修正公募采集器，保留四份原始来源并严格核对现金合计|四基金13386条新快照逐行独立对账、入库/导出、重试和冲突回滚通过；真实历史申赎业务仍未签收|
|常用跨仓兼容|Studio的现有固定提交组合通过Linux/Windows七应用及择时集成|不等于23仓最新默认分支组成的单一运行环境已认证；各应用固定依赖及旧发行标签保留|
|依赖维护|10个DependabotPR：七项Python声明与锁同步、三项CodeQLActions升级|各候选及实际主线CI通过；Notes八包264个SHA-256逐项属于对应PyPI官方发布文件|
|文档同步|Studio现有产品契约、Fund数据口径与软件接入、Agent已实现路线、Infra已归档状态、A股公共来源时点限制|按实际实现和来源证据更新，不将真实业务缺口改为完成|
|A股真实输入|匹配环境的原生预检确认缺真实价格缓存；另取单股21条基本面记录核查来源可得性|全部`available_at`未知，未通过历史PIT；完整真实价格、历史成员、H00300全收益及其他必需输入仍待齐备|

## 真实公募净值与分红

本次从AKShare公共接口分别取得单位净值、累计净值、现金分红和拆分四份来源资料，使用独立维护环境和新目录。四只样本为股票型110022易方达消费行业、000309大摩品质生活精选A，以及债券型000191富国信用债A/B、000171易方达裕丰回报A。首日至2026-09-30分别3897、3106、3201、3182条，共13386条；实际获知日期全部为2026-10-07。

旧采集器直接连乘源“日增长率”，在部分除息日遗漏现金分红。例如000191在2014-12-16的源增长率为-1.1707%，单位净值从1.025降至1.013，每份现金分红0.011；含再投资的实际研究日收益约-0.0975609756%。2015-02-16源增长率为-1.4423%，而1.040到1.025加每份0.015现金对应再投资日收益为0。旧快照保留为失败证据，不覆盖原字节。

修正后的采集器显式解析每份或每10份现金金额，以除息日单位净值再投资。每日财富因子为`(unit_now + cash_per_share) / unit_prev`；累计净值仅核对区间现金分项，不能充当总收益序列。日期不齐、现金合计不一致、重复、金额非法、分红单位不明确和未支持的拆分均拒绝，不插值或猜测。相关实现见[Fund#11](https://github.com/PureSaber/quant-fund/pull/11)。

独立复核从一份初始持仓出发，逐个除息日将现金按当日单位净值买入额外份额，再计算持仓市值，未调用采集器的收益计算辅助函数。所有13386行与新序列相符，最大相对误差约`2.903e-16`。完整93项基金测试通过，其中采集器14项回归已包含在93项内；两项核心经济回归先确认失败后修复通过。

四快照导入独立数据库后再次导入均新增0行；导出的13386条与数据库排序结果一致。将旧错误快照导入同一不可变版本键被拒绝，冲突前后数据库相同。元数据、文件哈希与具体除息日回执见[真实基金证据](evidence/fund-real-acceptance-20261007.json)。原始CSV、数据库、运行环境和本机日志不提交公开仓库。

这只签收公开净值及回顾性再投资研究序列。当前采集日不是历史公告获知日；按除息日净值再投资不模拟登记权益、实际付款或到账。完整真实申赎验收仍需历史条款、真实披露获知日期、交易/确认/银行用途日历，以及人工逐笔现金和份额对账资料。

## A股与界面功能证据

原本地A股环境存在共享因子版本不匹配，改用已匹配的维护环境后，预检实际拒绝缺失的`data/cn_a/daily/prices.parquet`。这两个失败分别记录环境兼容和输入缺失，不能混为一个数据问题。公共`stock_value_em`默认源并不提供历史获知时点；QDK保持未知值。600519的2026-09单股探测取得21条记录，已知`available_at`为0条，见[A股来源探测](evidence/ashare-source-probe-20261007.json)及[缓存文档PR](https://github.com/PureSaber/a-share-multifactor/pull/27)。没有关闭PIT、伪造发布时间或用单股样本代替完整四因子缓存。

HTTP验收包括已有单次观测模拟盘核验页、中断诊断页和一个明确声明为合成的报告流程。前两者没有原生HTML报告，正确地不显示iframe或报告入口；合成报告同时提供独立打开入口和iframe，报告文件返回200。Studio父页维持`DENY`，同源报告维持`SAMEORIGIN`；查看前后30份已保存文件哈希相同，见[HTTP回执](evidence/http-acceptance-20261007.json)。本轮浏览器策略阻止本机视觉控制，未尝试绕过；HTTP通过不替代新的宽窄屏视觉验收或宿主调用栈验证。

## 交付与主线检查

十个依赖PR均已合并：[Agent#13](https://github.com/PureSaber/quant-agent/pull/13)、[Crypto#11](https://github.com/PureSaber/quant-crypto-basis/pull/11)、[ReportHub#28](https://github.com/PureSaber/quant-report-hub/pull/28)、[Paper#11](https://github.com/PureSaber/quant-paper-sim/pull/11)、[Paper#10](https://github.com/PureSaber/quant-paper-sim/pull/10)、[Portfolio#22](https://github.com/PureSaber/quant-portfolio/pull/22)、[Futures#14](https://github.com/PureSaber/quant-futures-spread/pull/14)、[Execution#25](https://github.com/PureSaber/quant-execution/pull/25)、[Risk#18](https://github.com/PureSaber/quant-risk-monitor/pull/18)、[Notes#67](https://github.com/PureSaber/quant-research-notes/pull/67)。Python锁由对应项目支持的解释器和解析器重新生成；Git依赖的固定提交保持。CodeQLActions采用[官方v4.38.2](https://github.com/github/codeql-action/releases/tag/v4.38.2)的不可变SHA。

Notes依赖锁生成时使用的镜像未写成强制索引；八包264个摘要逐项核对PyPI官方该版本文件集合，见[依赖摘要核对](evidence/dependency-lock-hashes-20261007.json)。独立锁定环境按`--require-hashes`安装、`pip check`、Ruff、格式、契约校验及14项unittest均通过，契约校验器覆盖率99%。

本批其余代码和文档交付为[Studio#22](https://github.com/PureSaber/quant-studio/pull/22)、[Fund#11](https://github.com/PureSaber/quant-fund/pull/11)、[Agent#14](https://github.com/PureSaber/quant-agent/pull/14)、[Infra#6](https://github.com/PureSaber/quant-infra-workspace/pull/6)及上述A股文档PR。实际候选、合并提交和合并时刻见[交付回执](evidence/merged-prs-20261007.json)，受影响仓库的实际默认分支提交与CI见[主线检查快照](evidence/main-ci-20261007.json)。本文档PR自身的最终合并及主线CI以GitHub记录为准，避免将尚未发生的自验收写入提交。

## 仍需完成的验收

1. 新宽窄屏视觉复核，以及宿主MutationObserver具体来源、调用栈和修复验证。
2. A股完整真实历史输入及有证据的`available_at`，通过保持开启的PIT门禁。
3. 基金真实披露、历史条款、用途日历、登记权益和实际到账逐笔对账。

纳秒贯通、Crypto连续30日、独立大归档、授权国内L2、完整Barra和实盘接入保持暂缓或原外部条件状态。旧冻结环境、r4/r5账户、历史市场产物和发行标签未更新；本页不声明全部旧P0—P2、市场数据GA、策略有效性或自然前向完成。
