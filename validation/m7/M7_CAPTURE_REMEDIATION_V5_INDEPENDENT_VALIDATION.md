# M7 Crypto L2采集器v5独立验证交接

日期：2026-08-30（Asia/Shanghai）

角色：验证负责人（只读，`gpt-5.6-sol·xhigh`）

候选HEAD：`5b15c2c26a5a2f2b125e912d7f9412caf477b31c`

源码提交：`13e004a80296bb3a49c4bd54e64cb64670e56b01`

结论：`PASS`（P1=0、P2=0、无新增P3代码缺陷）

## 1.范围和验收结论

只读验证覆盖`quant-data-kit`PR#6的v5候选、17项内容寻址证据、journal→snapshot语义绑定、四类持久状态的闭合Schema与精确文件名绑定、真实Windows子进程硬退出恢复、bootstrap锁junction防护、独立stream身份锚点、测试、覆盖率、六轮8流fixture性能、3×1000万标准化、容量拒绝及精确HEAD远端CI。

历史v4候选发现的两项P2均已关闭：

1. 恢复不再接受仅有相同行数和Raw血缘的自洽替代快照；系统会从sealed journal重算分区集合、每分区行数、规范行摘要、`available_at`上界及最终L2 checkpoint，并与Parquet快照逐项核对。
2. PREPARED、COMMITTED、显式ABORTED和failure均采用闭合字段集合、严格非强制转换类型及完整哈希/attempt文件名绑定。

独立负向复现构造了相同provider、venue、Raw引用和行数但内容不同的合法快照，并重写、重哈希COMMITTED receipt；恢复以`Normalized epoch COMMITTED receipt does not match its journal content`拒绝该重绑定。

最终判定为`PASS`，满足“只有无P1/P2才能PASS”的门禁。

## 2.修改文件

无。验证负责人严格只读，未修改、提交、推送或委派；验证前后`git status --short --untracked-files=all`均为空。

被审查源码提交涉及以下6个文件，`git diff --check`通过：

- `src/quant_data_kit/capture_v2/epoch.py`
- `tests/test_capture_v2_remediation.py`
- `src/quant_data_kit/_version.py`
- `tests/test_m2_integration.py`
- `README.md`
- `docs/m7-crypto-l2-capture.md`

## 3.实际测试和证据

- 17/17个artifact的文件名SHA-256、实际SHA-256、字节数与`evidence-manifest.json`完全一致；6份性能报告和2份容量报告的内部`report_sha256`也复算一致。
- 定向pytest：14项通过，耗时6.52秒，覆盖快照重绑定、unknown field、严格类型、attempt文件名、真实`spawn`+`os._exit(87)`、junction锁和stream anchor。
- JUnit复算：主分区430项通过、1项既有平台skip；隔离硬退出分区1项通过；合计431项通过、1项skip、0失败。
- 全源码纯分支覆盖率`2217/2546=87.08%`；`epoch.py`为`251/276=90.94%`；17个配置核心模块全部≥90%。
- `pip check`、`ruff check --no-cache`和`ruff format --check --no-cache`全部通过；包版本`0.7.4`。
- Dense三轮为310.60/299.17/309.99messages/s，p99为37.73/36.54/36.97ms；Sparse三轮为575.18/578.13/573.59messages/s，p99为15.97/15.45/15.17ms；六轮均通过8流完整结束、恢复哈希和密度安全倍数门禁。
- 3×1000万为188,411.35、188,473.94、182,097.14events/s；最大峰值3.136GiB；每轮1000万全部接收、0隔离、严格重载和跨轮确定性通过；保留3,310,487,778字节且未清理。
- 安装后的CLI在`preflight`和显式`run --confirm-long-running`下均以退出码2返回`PAUSED_PREFLIGHT_FAILED`；8流均为0WebSocket、0Raw、0Normalized，`network_started=false`。
- GitHub Actions运行[33315502321](https://github.com/PureSaber/quant-data-kit/actions/runs/33315502321)精确绑定候选HEAD，Python3.10、3.11、3.12均SUCCESS；PR#6保持OPEN/MERGEABLE。
- 候选证据：`quant-data-kit/validation/m7-capture-remediation-v5/evidence-manifest.json`、`summary.md`和`technical-handoff.md`。

## 4.剩余风险和交接依赖

- 当前归档容量不足，公共Binance/OKX网络采集被正确阻断；本次PASS仅收口软件、fixture和本机性能门禁。
- 尚未完成连续30天真实采集、归档恢复演练、真实消息质量和跨源质量认证，`market_data_certified=false`。
- 国内L2仍缺合法授权数据，只能保持`fixture-certified-not-market-data-certified`。
- journal→snapshot恢复验证会线性重读journal和Parquet；未来大规模运行需监控启动延迟，任何优化不得弱化语义重算。
- PR仍未合并、未打tag；旧FAIL验证记录永久保留，不通过改写历史证据升级结论。
