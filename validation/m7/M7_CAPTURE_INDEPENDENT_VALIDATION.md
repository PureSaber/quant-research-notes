# M7 Crypto L2采集器独立验证交接

日期：2026-08-29（Asia/Shanghai）

角色：验证负责人（只读，`gpt-5.6-sol·xhigh`）

候选：`quant-data-kit`提交`63f49b0e0cb19aea2a68d39641c005551f70928f`

结论：`FAIL`

## 1.范围和验收结论

只读审查基线`bb796ad`至候选`63f49b0`的5430行diff、完整新增源码/测试/文档、供应商规则、Raw/Normalized、状态机、归档、CLI、证据和CI。默认8流、无密钥/账户/下单路径、Binance首事件与后续连续性、USD-M Combined解包、OKX 2026语义、统一Normalized契约及基本单进程归档均通过检查。

候选仍有8项P1，不能标记为代码或fixture认证PASS：

1. 状态机先推进状态，再吞掉`audit_sink`异常；磁盘满时可出现状态已变但不可变Raw审计为0。
2. preflight失败报告直接写`audit_events=1`，但未实例化状态机或Raw审计写入器，属于合成计数。
3. 每条Raw/audit消息执行热目录全树扫描和磁盘探测，每条Normalized记录执行flush/fsync，复杂度和事件循环阻塞不适合真实L2。
4. `CancelledError`只转PAUSED后立即重抛，不flush、归档或finalize；长期CLI的Ctrl+C可丢失未封段Raw和PAUSED审计。
5. 全部子流失败/PAUSED仍可汇总为`BOUNDED_PROBE_COMPLETE`或`STOPPED_WITHOUT_CERTIFICATION`并由CLI返回0。
6. Normalized发布前先清空runner journal并置closed，发布异常后不可重试且没有不可变abort记录。
7. M7范围只按symbol是否含BTC推导能力并核对能力集合，`BTCFAKE/ETHFAKE`也可通过。
8. 不可变写采用exists检查后`os.replace`，跨进程竞态可覆盖；归档子目录未拒绝Windows junction/reparse，可能绕过物理卷独立性。

P2：probe上限未覆盖snapshot同步阶段；run report直接`xb`写正式文件，崩溃可留部分文件；`asyncio.gather`遇到未捕获finalize异常时缺少统一取消、收尾和失败报告。

## 2.修改文件

无。验证前后工作树clean，本地和远端均为`63f49b0`；PR#6保持OPEN，未提交、推送、合并、tag或启动采集。

## 3.实际测试和证据

- `git diff --check bb796ad..63f49b0`：PASS。
- Ruff检查：PASS；格式检查76个文件。
- `python -m pytest -p no:cacheprovider`：299 passed、1 skipped，105.59秒。
- 新增核心纯分支均≥90%，最低collector 90.38%；全源码1800/2092=86.04%。
- `pip check`：PASS；`websockets==15.0.1`；包与运行版本均0.7.0。
- `tools/check_branch_coverage.py`未缩小门禁，新增7个采集核心模块90%要求。
- 正式coverage SHA-256：`f10c7056c07202e9df80387fc5f98968e6d2db446a3d255e5dbc8e7aea93005b`。
- 正式JUnit SHA-256：`12d46df3d93b2c577bfb23724f77cdb0ce74e182ea52a95f01c2c23fe4fe7a97`；300项、0 failure、0 error、1 skip。
- GitHub Actions run`33255725193`：候选提交精确匹配，Python3.10/3.11/3.12均SUCCESS。
- 两份F盘preflight报告均为8流PAUSED、0消息、0 Raw segment、未启动network collector；但合计声称16个audit event而无对应Raw审计，也未记录候选`collector_commit`。

复现证据：审计sink注入磁盘满后`state=BUFFERING,persisted=0`；100次Raw append产生100次tree scan和100次disk probe；取消后`pending_raw_frames=2,segments=0`；全部runner失败仍得到成功总体状态；Normalized publish异常后`runner_journal_is_none=True,aborted_markers=0`；伪造`BTCFAKE/ETHFAKE`仍通过范围断言。

## 4.剩余风险和交接依赖

重新申请独立验证前必须完成：审计与状态迁移fail-closed提交、真实preflight审计或零计数、摊销容量检查和批量fsync、取消/finalize/gather统一收尾、子流状态归约、精确8流身份、跨进程不可覆盖写、junction/reparse与最终卷身份验证、同步阶段有界及报告原子发布。修复后还需8流fixture吞吐与事件循环延迟基线。

即使代码修复通过，真实Crypto采集、30天数据、跨源质量和`market-data-certified`仍未完成。
