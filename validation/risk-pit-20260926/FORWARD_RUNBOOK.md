# 真实前向观察操作手册

工作目录为`H:/Documents/ChatGPT/temp/quant-risk-pit-20260926`，解释器为其`.venv/Scripts/python.exe`。未来观察是固定四ETF的研究模拟账户，没有券商订单。活跃账户以本目录最终验收记录和`evidence/active-forward-registration-receipt.json`为准；旧r2账户已经替代，不能追加观察。

观察区间为2026-09-28至2026-12-31，固定base候选。禁止因后续收益变更策略、因子方向、参数、代码、观察起点或账户本金。研究失败、数据缺失和输入修订必须原样保留。只有未来真实交易日才能产生前向证据。

## 每次收盘后的操作

1. 读取活跃账户的`account.json`和`account.db`，执行`quant_pipeline.research_paper.load_account`核验定义。用`equity_code_identity()`比较冻结代码身份，所有参与执行的仓库必须保持干净；不得拉取新代码后继续原账户。先核验工作台`run.py verify`。Notes证据追加和Workspace清单更新不属于策略代码，但必须提交并保持清单一致。
2. 确认交易所日历、当前北京时间已晚于目标交易日15:00、供应商已发布完整数据。周末、休市或上游尚未完整时不制造观察。如果某日漏跑，允许在以后真实时刻重放冻结起点至最新完成日，但记录实际捕获和观察时间，不能伪装成当日已观察。
3. 实际重取并核验官方规则及上市证据，保存HTTP来源、原始字节、哈希和真实捕获时间。在新的source目录保存旧版本及新证据；不得覆盖`artifacts/pit-sources/bundle-v7`。现行规则原本仅核验至2026-09-26T08:50:36.044423400Z，不能仅复制文件后抬高有效期。若经本次真实核验仍有效，可以延长对应现行版本的`effective_to`至本次核验时刻；新发现规则使用诚实的`available_at`，不得倒填。
4. 调用`quant_data_kit.instrument_master import --source <新source> --output <新master>`，随后`inspect --root <新master>`。新输出目录必须未存在。用`instrument_master_prefix`比较新旧master在账户初始cutoff及最近观察cutoff处的前缀；两处都须完全相同。初始cutoff读取账户字段，本轮为2026-09-24，9月25日休市。
5. **先bind新master，再update行情**。当前数据根为`artifacts/pit-sources/qdk-etf-research-v3-pit-20260925`，source模式是`live_public_api`，provider为`akshare_sina_etf`。执行：

   ```powershell
   .venv/Scripts/python.exe -m quant_data_kit.research_dataset bind-master --root artifacts/pit-sources/qdk-etf-research-v3-pit-20260925 --instrument-master <新master> --captured-at <真实核验时刻>
   .venv/Scripts/python.exe -m quant_data_kit.research_dataset update --root artifacts/pit-sources/qdk-etf-research-v3-pit-20260925 --end <已完成交易日> --captured-at <真实抓取时刻> --overlap-sessions 5
   ```

   不传`--source-dir`，不切换来源。旧master覆盖不到9月28日，先update会被拒绝。不得通过伪延长master或跳过验证解决。
6. inspect新快照，核验4只ETF、requested_end、行情/权益/基准/日历完整性、来源身份和master哈希。为观察创建新recipe副本，仅更新inputs中的bundle和catalog，二者指向同一新snapshot；移动目录时修正相对路径或使用绝对路径。其他参数原样冻结。
7. 验证`input_lineage(new_inputs)`等于账户冻结lineage；`input_prefix(new_inputs, initial_cutoff)`等于初始前缀；已有观察时，最新`as_of`处前缀也等于该观察保存值。任一不相等即保存差异、停止，不得重写旧数据或旧观察。
8. 执行`quant_pipeline.research_paper observe <活跃账户目录> --recipe <新输入recipe> --as-of <已完成交易日>`。程序从冻结起点连续重放同一账户，并再次校验已有逐日收益完全一致。不可注入受控时钟，不可提前观察。
9. 核验result及全部产物哈希、已有前缀不变、观察日期单调递增；记录实际风险拒绝、成交、费用、持仓和现金。将精简派生结果、来源索引和哈希追加至Notes当前功能分支并推送GitHub，原始行情和完整附件仍本地保留；更新Workspace对Notes的精确提交引用并提交推送。不得改动冻结的执行仓。

## 必须停止并报告的情况

- 任何冻结的源代码身份变化、模型无效、证券缺失、历史字段或可得时间被改写。
- 原始价、复权价、基准、日历、公司行动或旧收益被供应商修订。特别是未来分红可能改变全部前复权历史，原账户会被前缀校验拒绝。不能拼接旧值伪装通过；停止并保留证据。是否使用新账户需明确重新登记，不能静默换起点。
- 新交易规则导致整个区间无法投影为单一lot、tick、执行属性或费用范围。此时需要新的时变执行规格开发，不能硬编码继续。
- 官方材料不可核验、上游数据不足或网络失败。临时问题可稍后以新的真实捕获时刻重试；不能把成交量或当前查询结果推断为历史可交易状态。

该账户仍缺完整逐日停复牌、盘中状态和动态全集，风格模型仍是market统计代理。前向观察不会自动消除这些局限，也不构成实盘适用性认证。

完成12月31日全部交易日观察后，等待更晚自然日再调用`paper seal`。封存前核对完整日历、前缀、注册时刻和失败历史；成功封存后停止本观察自动化。没有新完成观察且状态未变化时保持安静；新增有效观察、出现新失败、需要用户处理或完成封存时才通知。
