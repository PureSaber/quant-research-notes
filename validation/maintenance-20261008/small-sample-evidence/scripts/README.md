# 2026-10-08 小样本验收脚本

使用各仓 Python 3.12 独立锁定环境，勿把多个项目依赖混装到全局 Python。脚本记录本轮固定日期的验收，公共源会变化；以后运行应创建新批次并如实记录实际获取日，不能复用旧日期伪造 PIT。

基金仓环境先运行原生命令，输出目录为本文件所在目录的 `scratch/public-fund`：

```text
python -m quant_fund.cli fetch-public --code 000191 --out <此目录>/scratch/public-fund/000191.csv
python -m quant_fund.cli fetch-public --code 003318 --out <此目录>/scratch/public-fund/003318.csv
python <此目录>/accept_fund.py
python <此目录>/fetch_official.py
```

`accept_fund.py`要求新的 SQLite 路径，并额外创建明确标记的损坏输入；不修改原始 CSV。采集器保留四份原始侧文件，供独立分红收益核对。

A 股仓环境依次运行 `accept_ashare.py`、`accept_ashare_prices.py`。后者是另一次明确选择 Tencent 的检查，前者的 Eastmoney 失败保持记录，不会自动改写成成功或混合价格源。网络失败被写入 JSON，因此必须核对 JSON 的 status 和计数，不能仅用进程退出码判断通过。

QDK 当前环境运行 `accept_official_timing.py`，读取两份官方文件的实际采集回执，验证过去时点拒绝、当下时点接受。没有将 URL 日期当成精确发布时间，也没有复制固定哈希去假装取得不存在的文件。

所有原始数据、数据库、官方文档和文本均属于临时 `scratch`，完成检查并保存计数/摘要后删除。对账功能的完整软件测试位于基金仓 `tests/test_observations.py`，不需要账户凭据或真实用户资料。此目录不包含下载数据或私有交易凭证。
