# 2026-10-08 仓库群维护与资源评估

本批承接 GitHub 仓库群检查：补默认分支保护、验收共享时间精度和消费者修复、
准备归档部署，以及验收外围仓已有 PR。用户确认暂无独立归档存储；面试仓范围为
完成已有两个 PR 并整理剩余待办。完整真实业务与 M9 GA 按实际证据单独保留。

## 默认分支保护

五个缺失保护的公开仓现已启用 active ruleset：必须通过 PR 合入、解决审查讨论、
基于最新主线通过固定 CI，禁止删除和强推，无 bypass actor。单维护者仓未设置
必须由第二人批准的门槛。核心 23 仓中，20 个公开仓默认分支受保护。

| 仓库 | 规则 |
|---|---|
| quant-research-notes | [24698556](https://github.com/PureSaber/quant-research-notes/rules/24698556) |
| quant-hk-equity | [24698560](https://github.com/PureSaber/quant-hk-equity/rules/24698560) |
| quant-timing | [24698569](https://github.com/PureSaber/quant-timing/rules/24698569) |
| quant-regime | [24698572](https://github.com/PureSaber/quant-regime/rules/24698572) |
| quant-studio | [24698762](https://github.com/PureSaber/quant-studio/rules/24698762) |

Studio 的上游矩阵任务名包含提交 SHA，新增稳定 `upstream-integration` 汇总检查：
任何上游矩阵失败、取消或跳过均不能通过。其 [PR #25](https://github.com/PureSaber/quant-studio/pull/25)
及合并后主线 CI 均通过后才开启规则。

三个 private 仓 quant-stat-arb、quant-us-equity、quant-infra-workspace 的规则 API
返回 403，要求 GitHub Pro 或公开仓库。该账户条件不能靠代码修复解决，本轮不改变
私有可见性，也不声称这三个仓已受平台保护。

## 纳秒时间贯通

- [QDK #34](https://github.com/PureSaber/quant-data-kit/pull/34)：固定候选 `61b571bdb9bba5d0a8c3aff8b406864539d0a9fc`，新 Windows/Python 3.12.14 全量 856 通过、2 跳过，24 个核心纯分支门槛通过，全源码纯分支覆盖 83.09%。
- [Execution #26](https://github.com/PureSaber/quant-execution/pull/26)：固定候选 `b2ab4fc8c8705b7ae0a78991318880245a47b29d`，372 测试通过，总覆盖 94.73%，十个既有核心纯分支门槛均通过。
- 执行层增加 11 个精度回归，覆盖 JSON、流式订单恢复、幂等重试、分红回放、晚到事实、公司行为和美股现金时点；使用新 QDK 时，旧消费者代码在其中 10 个案例失败。
- [HK #6](https://github.com/PureSaber/quant-hk-equity/pull/6)：修复 JSON 解析、事实可得性、汇率准入和时间线精度；场景专用依赖栈固定到以上两提交，默认日频研究栈保持冻结。GitHub 固定依赖安装后 46 场景测试通过，纯分支覆盖 330/366 = 90.16%；候选栈下另有 18 项默认测试通过。

本批新回归不是旧 21 个外部消费者用例的原样重跑；历史失败证据保留。
软件时间精度通过不证明真实数据的历史发布时间、公司行为或实际到账真实完整。
实际 PR 合并与最终主线检查记录见 GitHub 及 [交付清单](delivery.json)。

## 外围仓

- [currency-converter #1](https://github.com/PureSaber/currency-converter/pull/1)：修正导出列表排序导致的 Ruff CI 失败，9 测试及 Python 3.10/3.11 CI 通过，已合并且主线通过。
- 面试仓 [#1](https://github.com/PureSaber/quant-interview-intelligence/pull/1) 与 [#19](https://github.com/PureSaber/quant-interview-intelligence/pull/19) 已合并；分别重跑 18/21 测试，Schema 再生成无差异、策略校验和 Python 3.11/3.12 CI 通过，合并后主线通过。
- [17 条待办](https://github.com/PureSaber/quant-interview-intelligence/blob/main/docs/backlog-2026-10-08.md) 已按依赖、已有基础和未满足验收标准整理。19 条来源记录仍为待人工复核，26 项许可主题索引不能替代幂等导入器；不以 PR 合并关闭开发待办。

## 第 3 项：资源与完成条件

| 工作 | 本机是否可推进 | 完成还需要什么 |
|---|---|---|
| A 股完整历史 PIT | 可继续小样本、字段校验和分区导入；约 343 GiB 空闲不是当前样本验证的主要阻碍 | 合法可用的完整数据、历史成分/退市/行动及可证明的历史 `available_at`。当前源缺获知时点，增加磁盘不能补证据；先实测样本后估算全量容量。 |
| 基金真实申赎与到账 | 账本、日历接口和核验程序可在本机完成，样本级对账通常不是容量问题 | 历史条款、真实披露时点、用途日历、登记权益、交易确认及实际现金到账资料；当前 13386 条净值只能支持净值/回顾研究验收。 |
| 其他市场完整业务 | 可继续软件模型、导入器与回放测试 | 各市场真实公司行为、历史状态、结算与权利证据，不能以合成场景替代。 |
| 报告 iframe 宿主 MutationObserver | 已有独立打开完整报告入口；与磁盘容量无关 | 宿主源码/调用栈或宿主修复后的复验。先前无脚本 iframe 仍复现异常，本轮不宣称修好第三方宿主。 |
| 八流 L2 连续采集 | 软件和离线预检已具备；当前不能完成 GA | 独立归档、实测增长速率、留存与恢复计划、持续供电网络，以及八流 30 个完整 UTC 自然日。 |

这些事项可以分阶段推进，但目前无法将完整真实业务宣布完成。资源实测、配置、
安装和上线步骤见 [部署准备](DEPLOYMENT.md)；Notes #11/#12/#13 继续开放。

2026-10-08 后续已推进[第三项软件与小样本验收](SMALL_SAMPLE_ACCEPTANCE.md)：新增基金外部凭证对账、两只公募 5529 条真实净值检查、A 股 42 条缺发布时间记录的拒绝验收，以及两份官方材料的真实采集时点验证。[宿主 iframe 交接](HOST_IFRAME_HANDOFF.md)保留本次复现和可用查看路径；详细证据及临时数据清理回执在同目录。
