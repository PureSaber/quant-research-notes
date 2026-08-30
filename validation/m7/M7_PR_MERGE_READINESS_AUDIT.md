# M7候选PR合并就绪独立审计

日期：2026-08-30（Asia/Shanghai）

角色：验证负责人（只读，`gpt-5.6-sol·xhigh`）

结论：`BLOCKED`（P1=1、P2≥2）

## 1.范围和验收结论

只读核验`quant-data-kit#6`、`quant-execution#6`和`quant-workspace#3`的精确HEAD、GitHub三版本CI、工作树、依赖锁定、独立验证证据及合并风险。

| PR | 单仓结果 | 合并结论 |
|---|---|---|
| `quant-data-kit#6` | HEAD`5b15c2c`，三版本CI成功，软件/fixture独立验证P1=0、P2=0 | 中央证据归档后重新核验 |
| `quant-execution#6` | HEAD`b99245d`，三版本CI成功，单仓P1=0、P2=0 | P2：仍锁定`quant-data-kit@v0.6.1`，需对新数据版本完成组合认证 |
| `quant-workspace#3` | HEAD`c894c80`，三版本CI成功 | P1：认证声明未与证据内容语义绑定，禁止合并 |

`quant-workspace#3`只校验证据文件存在和SHA-256，没有解析证据内容并与事件数、吞吐、RSS、市场窗口、供应商、能力和CI声明逐字段对账。现有测试使用任意文本文件配合自报指标也能得到`rc_ready/ga_ready=True`，因此CI成功不能消除该P1。

## 2.修改文件

无。验证负责人严格只读，没有修改、提交、推送、合并、打tag或继续委派；三个候选工作树在审计结束时均为clean，且与远端PR HEAD一致。

## 3.实际检查和证据

- `quant-data-kit#6`：HEAD`5b15c2c26a5a2f2b125e912d7f9412caf477b31c`；GitHub Actions运行`33315502321`；Python3.10、3.11、3.12全部SUCCESS；v5证据17/17哈希和字节数一致。
- `quant-execution#6`：HEAD`b99245d9145d44f481a41b2311b7a9c8d764f7b3`；GitHub Actions运行`33252013765`；三版本全部SUCCESS；性能报告SHA-256为`a26c9f0eefeb9b0150c9c1ed93b8163a57ec603c8349082847b3927755bec634`。
- `quant-workspace#3`：HEAD`c894c80929084a71f84718f11073a550c04acb3e`；GitHub Actions运行`33249314954`；三版本全部SUCCESS。
- 15个正式仓库默认工作树均clean、0ahead/0behind；三个PR工作树均clean、与远端HEAD一致；未发现活跃候选的未推送commit。
- 风险定位：`quant-workspace/src/quant_workspace/m7_certification.py`证据校验段和`tests/test_m7_certification.py`的任意文本fixture；`quant-execution/pyproject.toml`及`requirements.lock`的数据依赖仍为`v0.6.1`。

## 4.剩余风险和交接依赖

1. 为M7各类证据定义闭合JSON Schema，并将所有认证声明与证据内容逐字段绑定。
2. CI证据必须绑定仓库、运行ID、事件、精确`headSha`、结论和完整Python job矩阵；不能信任清单中的自报字符串。
3. 增加“任意文本证据”“伪造指标”“伪造CI”和“哈希正确但语义不符”负向测试。
4. `quant-data-kit`合入并通过默认分支CI后，只能创建组件版本tag；该tag不代表平台`v2.0 GA`或真实市场认证。
5. `quant-execution`更新到该组件tag后，重新执行三版本组合CI、正确性和性能认证，再申请合并。
6. 公共网络、连续30天、归档恢复和国内合法L2仍为外部/时间阻塞，`market_data_certified=false`。

在P1关闭并形成新精确HEAD独立PASS前，不得合并`quant-workspace#3`。
