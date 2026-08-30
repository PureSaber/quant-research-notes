# M7数据性能独立验证交接

日期：2026-08-29（Asia/Shanghai）

角色：验证负责人（只读，`gpt-5.6-sol·xhigh`）

结论：`PASS`

## 1.范围和验收条件

只读复核`quant-data-kit`PR#6的大diff、约2700行`normalized_v3.py`、公开接口兼容性、PIT/sequence/L2校验、lake-wide claim冲突、失败回滚、不可变发布、严格重载、OKX 2026语义、性能报告和CI。未发现阻止M7数据性能专项验收的代码或证据缺陷。

确认：`checksum=0`不作为完整性证明；等序列空心跳不产生Normalized事件；维护重置保持等待新snapshot；非零CRC32仅为legacy fixture；snapshot和claim索引在lake-wide锁内发布；claim冲突覆盖v3和历史legacy snapshot；内存结论仅限本次1000万行基准。

## 2.修改文件

无。验证前后工作树为空，未提交、推送、合并、打tag或委派。

- 证据提交：`bb796ad49f5c69e9b31d1813d9ca12641755f876`
- 被测源提交：`009a36162a2ec1a48fc4f96b93b2e675196e9263`

## 3.实际测试和证据

- `python -m pip check`：PASS。
- `python -m ruff check --no-cache src tests tools`：PASS。
- `python -m ruff format --check --no-cache src tests tools`：PASS，65个文件。
- 内存Coverage运行：263 passed、1 skipped，91.28秒。
- 分支覆盖率：`normalized_v3.py`90.45%、`data_lake.py`90.32%、`l2_replay.py`95.83%、`okx.py`94.00%，全部核心模块≥90%，全源码83.98%。
- 性能报告SHA-256：`69416eeba389ff520043c9382ed7e1ff7380f4d5937030a02cb84cb1ab80c08f`，复算一致。
- 三次1000万行：155,932.27、155,071.20、153,097.30events/s；峰值RSS分别2.943、2.949、2.967GiB；每次接受1000万、隔离0、提交精确、`dirty=false`、临时目录位于F盘、`cleanup=false`。
- 三次逻辑snapshot、物理partition、manifest、16个claim分片和最终L2 checkpoint哈希一致。
- 三个保留run均复算1000万条event claim，重复`event_id`为0；DuckDB临时落盘配额0B；36个文件共3,310,487,778字节，验证前后大小和mtime不变，`FAILED`文件为0。
- PR#6保持OPEN、merge state为CLEAN；Python3.10/3.11/3.12 CI均SUCCESS，CI run `33252479550`。

证据：

- `quant-data-kit/validation/performance/m7-data-arrow-10m-final-okx-contract.json`
- `quant-data-kit/validation/performance/m7-command-results.md`
- `quant-data-kit/.m7/quant-data-kit-10m-final-clean2-009a361`
- https://github.com/PureSaber/quant-data-kit/pull/6
- https://github.com/PureSaber/quant-data-kit/actions/runs/33252479550

## 4.剩余风险和交接依赖

- 性能证据是单盘口、单snapshot加连续upsert的合成Binance-style L2，不代表OKX真实网络数据、断线重连或全部盘口形态。
- 内存认证只覆盖本次1000万行规模；内存仍随活跃stream、checkpoint和partition数量增长，不是通用O(1)证明。
- 公共严格loader在claim索引缺失时具有自修复写入行为；只读验证使用全分区哈希复算和纯内存claim重建。只读挂载环境若索引缺失，仍需独立审计入口或预先保证索引完整。
- 真实Binance/OKX采集、连续30天数据、归档恢复和国内L2合法数据认证不在本次PASS范围内。
