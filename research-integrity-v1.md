# Research Integrity v1

本规范定义PureSaber量化投研从数据进入到绩效解释的第一版强制链路。目标不是把所有研究都塞进一个仓库，而是让每个研究引擎共享同一组可审计边界。

## 五项能力与所有者

| 能力 | 主要仓库 | 强制证据 |
|------|----------|----------|
| 1.数据真实性 | `quant-data-kit`、`a-share-multifactor` | `available_at`、历史成分、交易日历、内容哈希快照、数据质量摘要 |
| 2.研究验证 | `quant-factors`、`a-share-multifactor` | walk-forward折、purge/embargo区间、泄漏审计、FDR校正、折间稳定性 |
| 3.统一运行契约 | `quant-lab`、股票/期货研究引擎 | `standard/run_manifest.json`及哈希校验通过的标准产物 |
| 4.组合与风险 | `quant-portfolio`、`quant-risk-monitor` | 协方差、约束优化、换手/冲击成本、容量、VaR/CVaR、压力与流动性指标 |
| 5.绩效归因 | `quant-report-hub` | 证券贡献、成本对账、因子贡献/特异收益、Brinson-Fachler归因 |

## 1.数据真实性

基本面事件日期不能代替可获得日期。所有因果合并必须使用`available_at<=observation_time`，并保留`source_available_at`作为审计证据；超出`max_age`的事实不得无限向后填充。

股票池使用历史成分事件和上交所实际交易日重建。回测取历史期间所有曾入选标的的并集下载行情，不能先用当前成分过滤价格。若历史成分源不可用，不应把当前成分平铺到整个历史期间并称为历史股票池。

价格目前明确采用`qfq`口径并写入快照元数据。每个输入数据集写入不可变、内容寻址的Parquet快照，记录内容哈希、schema哈希、数据源、采集时间、查询区间、复权口径和上游快照。历史结果必须引用快照ID，不得只引用可覆盖的缓存文件。

质量门至少检查：必需字段、重复symbol-date、日期合法性、OHLC逻辑、正价格、非负成交量、缺失比例和交易日覆盖。上市/退市区间可通过`apply_symbol_lifecycle`裁剪。

## 2.研究验证

时间序列验证禁止随机打乱：

1. expanding walk-forward只在过去训练，在未来测试；
2. 标签区间重叠时使用purged K-fold；
3. 在训练/测试边界应用embargo；
4. 特征`available_at`晚于样本时间时验证直接失败；
5. 多因子同时检验使用Benjamini-Hochberg FDR，不以未校正p值挑因子；
6. 输出每折IC、样本数、方向、显著性和折间稳定性，不能只报告全样本最优结果；
7. 可用probabilistic Sharpe ratio评估有限样本、偏度和峰度下的Sharpe可信度。

`a-share-multifactor`默认写入`validation/fold_metrics.csv`、`validation/fdr_results.csv`、`validation/leakage_audit.csv`和`validation/summary.json`。

## 3.统一运行契约

标准目录不可覆盖，schema版本为`1.0`：

```text
<run>/standard/
├── run_manifest.json
├── returns.csv
├── positions.csv
├── orders.csv
├── costs.csv
├── exposures.csv
└── metrics.json
```

`run_manifest.json`记录项目、run ID、策略、UTC创建时间、代码版本、配置哈希、数据快照ID、标签以及每项产物的SHA-256。`quant-lab validate --run-dir <run>`在进入归因、索引或比较前验证文件存在、schema和哈希。

股票多因子和期货价差引擎均已写入该契约。旧的项目专用产物可以保留用于兼容，但跨仓库消费者以`standard/`为优先来源。

## 4.组合与风险

组合层包含：

- 收缩协方差与PSD修复；
- 带预期收益、风险厌恶、线性交易成本和换手惩罚的均值-方差优化；
- 资产上下限、组合总权重、分组上限和最大换手约束；
- 基于ADV、参与率和资金规模的容量估计；
- 平方根市场冲击成本；
- 历史VaR/CVaR、组件风险贡献、情景压力损失、流动性退出天数和因子暴露；
- 风险检查结果同时返回告警和机器可读指标。

风险模型是研究和模拟交易门禁，不是交易所级实时风控。实盘前仍需加入订单前风控、涨跌停/停牌状态、保证金、券源、断线恢复和券商回报对账。

## 5.绩效归因

`quant-report attribute`消费标准运行契约。默认将某一持仓快照用于其后的收益期间，不允许同日持仓解释同日收益，以避免前视偏差。

输出包括：

- `holdings.csv`：证券级权重、收益、贡献和缺失标记；
- `summary.csv`：毛贡献、成本、净贡献及与组合收益的残差对账；
- `factors.csv`、`factor_summary.csv`：因子暴露×因子收益和特异收益；
- `brinson.csv`：相对基准的配置、选择和交互效应；
- `manifest.json`：归因文件哈希、行数和持仓时点规则。

残差不是自动归零项。残差过大表示收益频率、持仓时点、资产收益、现金、衍生品乘数、公司行动或成本口径中至少一项没有对齐，应先修复数据口径再解释结果。

## 端到端门禁

研究运行的推荐顺序为：

```text
PIT数据+快照
  → 特征/标签泄漏审计
  → walk-forward/purged验证
  → 含成本与成交约束的回测
  → standard运行契约
  → 契约哈希验证
  → 组合与风险检查
  → 绩效归因及残差对账
  → quant-lab索引与报告
```

股票研究完成后可设置`QUANT_RUN_ID`和`QUANT_ASSET_RETURNS`，运行`quant-pipeline/configs/research_integrity_postrun.yaml`执行契约验证、归因和实验索引。

## 版本发布顺序

内部依赖必须先发布被依赖仓库，再发布消费者：

1. `quant-data-kit v0.3.0`、`quant-factors v0.2.0`、`quant-lab v0.2.0`；
2. `quant-portfolio v0.3.0`、`quant-risk-monitor v0.2.0`、`quant-report-hub v0.3.0`、`quant-agent v0.2.0`；
3. `a-share-multifactor v0.3.0`、`quant-futures-spread v0.2.0`；
4. `quant-pipeline v0.2.0`。

消费者通过tag锁定自己的内部库。外部Python依赖仍由各仓库的`pyproject.toml`声明版本范围，正式部署应再生成环境锁文件。

## 当前边界

v1覆盖可复现的日频/调仓频率股票多因子和期货价差投研主链路，但不代表已经覆盖所有市场与策略。尚不在本版本承诺内的能力包括逐笔撮合、期权波动率曲面、债券现金流、跨币种资金成本、实时风控、券商/交易所回报对账、分布式数据血缘服务和模型在线漂移监控。新增资产类别时必须扩展标准契约或增加版本，不能把含义不同的数据硬塞进现有字段。
