# 本轮证据与重跑

此目录只保存汇总回执、文件摘要和验收脚本，不包含原始 PDF、文本摘录、历史数据快照或客户交易资料。`official-source-receipts.json` 记录本轮真实采集时间；重跑不得复用该时间充当新文件的采集记录。

- `disclosure-source-acceptance.json`：三条官方披露摘录的实际导入、时点边界及篡改拒绝结果。
- `fund-terms-source-acceptance.json`：三个公开数学算例；没有真实客户确认单或银行流水。
- `download-inventory.json` 与 `cleanup-receipt.json`：删除前的逐文件清单，以及删除后零数据文件的复核。
- `software-validation.json`：开发 PR、精确提交号、本地测试汇总及合并后的逐作业 CI 通过记录。
- `scripts/`：本轮实际执行的脚本。它们以自身所在目录作为工作目录，故重跑时应复制到仓库之外的新空目录，不直接在此目录执行。

重跑需分别使用两项目按锁文件建立的 Python 3.12 隔离环境及 Poppler `pdftotext`，不增加项目依赖。将三个脚本复制到新工作目录并创建其 `scratch` 子目录后：

1. 用已安装 `requests` 的项目环境运行 `fetch_official.py`。核对生成的回执中两个来源均为 `downloaded`。脚本只访问列出的官方 URL，每份文件上限 20 MB；源站变化或不可用会记录失败，不能沿用旧的通过结论。
2. 在该工作目录运行下列提取命令，重新人工核对半年报第 5 页的三个字段和招募说明书第 70–72 页的算例、口径及份额类别：

   ```powershell
   pdftotext -layout scratch/official/sse-600519-2025H1.pdf scratch/official/sse.txt
   pdftotext -layout scratch/official/fullgoal-000191-202606.pdf scratch/official/fullgoal.txt
   ```

3. 用已安装本轮 A 股实现的环境运行 `accept_disclosure_source.py`，用已安装本轮基金实现的环境运行 `accept_fund_terms.py`。不要用 `python -O`，验收断言必须启用。脚本要求导出目录不存在，避免覆盖旧快照。
4. 保留新汇总回执，按本次新生成文件的实际清单和哈希清理 `scratch` 中的原文与派生数据，复核为零后记录新清理回执。不要删除其他轮次数据，也不要把新回执覆盖到本轮归档中。

三条结构化摘录是人工核对输入，字符串出现检查不能替代对字段和报告期的复核；公开算例中的指定赎回费率也不代表完整产品费率表。本轮文件已删除，以上是重跑流程，不表示原文仍在本地保留。
