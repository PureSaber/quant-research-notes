# 期货与Crypto原生只读预检

2026-10-04补齐两条离线样例路径的原生预检，作为P1.1剩余资产接入的前置能力。当前仍为synthetic、fixture-only、backtest-only；完整Studio模板、净值/报告适配和GUI首次使用验收尚未完成，不增加P0.3真实双腿或P2连续采集、L2证据。

## 实现与根因

原实现把输入加载与策略、执行、账本创建放在完整回放入口内。两仓现在分别抽出静态准备路径，预检与正式运行共用，避免在Studio中复制业务校验或用完整回测冒充预检。

- 期货检查配置、主表、事件、信号唯一性及触发引用、有限正初始现金与整数精度。缺失触发事件在创建策略前拒绝。配置和两个输入文件在加载前后核对SHA-256与修改时间；写认证产物之前再次检查回放期间是否变化，产物绑定实际加载的摘要。
- Crypto检查来源、种子、有限正现金、USDT现货与线性永续的匹配身份、目录和两来源哈希及质量。选择单一来源也必须验证另一来源。加载与回放期间内容、修改时间或文件集合变化均拒绝。
- 预检不创建策略、撮合器、执行引擎或账户，不写运行目录。JSON显式保留数据性质、适用范围、参数或配置摘要、币种、输入指纹和限制；`investable=false`。
- 正式运行重新读取输入，继续使用QExec唯一账户事实。静态预检不证明成交、双腿完整性、流动性或保证金足够，不验证输出目录可写，也不替代正式运行源码身份检查。

入口：

```text
qfs-certified-backtest --config config/certified_local_sample_v1.yaml --preflight
qcb-run-fixture --source binance --seed 7 --preflight
qcb-run-fixture --source okx --taker --preflight
```

## 实际验收

[机器可读回执](evidence/fixture-native-preflight.json)使用LF换行，SHA-256为`33758e3c9c6d1cb23d89ef53e604269a2803310a9bfb335c1da4c5e0aa95fa8f`。

|仓库|本地验证|原生执行证据|
|---|---|---|
|[Futures#13](https://github.com/PureSaber/quant-futures-spread/pull/13)|211项通过、1项既有跳过；覆盖率84.49%，standard/v2核心纯分支45/46|同一配置预检→回放，23事件、4个双腿信号；12份标准文件原生回读通过|
|[Crypto#9](https://github.com/PureSaber/quant-crypto-basis/pull/9)|93项通过；覆盖率96.09%，产物核心纯分支38/38|Binance/OKX各maker/taker，共4条相同参数预检→回放；每条12份标准文件原生回读通过|

测试用独立Windows/Python3.12环境按各仓正式锁安装；Ruff和pip check通过。依赖来源均核对为QDK v0.8.1、QExec v0.5.1、QLab v0.3.1的精确提交，没有复用版本过旧的仓内环境，也未修改r4/r5冻结环境。

五次CLI执行共60份标准产物通过验证，期货原配置与标准配置一致，Crypto共同参数及run_id与原生产物一致。三份期货输入和三份Crypto输入共六文件的内容、修改时间和清单保持不变。真实CLI负例中，缺失触发事件与负种子在预检、正式运行均以非零退出且没有输出目录。单元测试另覆盖损坏未选择来源、加载中变化、回放中变化，以及禁止预检创建执行状态。

实际运行源码为期货`d9a918115686eee101489da3fa25fa32b1edb447`、Crypto`cbeec78c64e4fe8373a091dc79926566fd0c371b`。两PR全部Python3.10—3.12及CodeQL检查通过，合并主线分别为`f01d6afd87ca0556d6e2f44e522cfecbf00cad56`、`d7aa41e914ff83e5d9668078b8901c80e2355397`；不能将合并提交记为先前CLI执行版本。

合并后两仓主线CI和CodeQL也已全部通过。

下一步将原生standard/v2账户结果接入Studio，保留事件时点、币种、初始资金和样例标识，再完成模板、失败路径及GUI验收。两仓原生预检完成不意味着Studio已从六模板增加到八模板。[全部P0—P2](PLAN.md)继续进行。
