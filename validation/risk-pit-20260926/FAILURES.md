# 保留的失败与修复

## 首次真实运行

`etf-risk-walkforward-20260926`的4个候选全部失败，未产生可评价的样本外收益。执行器在首个训练窗口发现`max_turnover must be between 0 and 1`。

根因：QLab与QPortfolio对换手采用`sum(abs(target-current))`，完整轮换的卖出和买入两腿合计可到2；QRisk的DecisionPortfolioLimits却复用了普通权重的[0,1]验证。修复为换手独立使用[0,2]，其他权重限制仍为[0,1]，并补完整轮换2通过、1.99阻断和越界拒绝反例。ASM真实账本清仓测试同步覆盖配置值2。

QRisk修复提交为`a5c5a8ee5486c42f07e1539ad92cf1fb57c1e638`，完整103项测试通过。首次study与validation保存在`evidence/attempt-1-*`，本地完整attempt与traceback保留不变。后续使用新研究编号后缀`-r2`，只更新代码身份与编号，研究参数和数据快照不变。

## CI中的既有采集测试

QDK的Python3.11首次CI在`test_coordinator_reports_reconciled_epoch_before_network`出现采集状态失败，包含文件生命周期和PAUSED→RESYNC错误。同一提交重跑通过，另外两个Python版本也通过。该模块不在本次ETF研究执行路径中。保留原日志并独立只读排查；在未证实根因前，不把一次重跑成功称作修复。

独立只读复核确认capture_v2在本轮没有diff。首个stream报FileNotFoundError，其他stream的CancelledError是取消级联；异常处理可能从已清理的PAUSED状态尝试转回RESYNC，形成二次诊断噪声。原CI压缩日志缺少首个错误的具体路径，无法据此确定文件竞争根因。本地精确测试及额外10次重复均通过，残余风险保留为既有采集并发清理问题。原失败：https://github.com/PureSaber/quant-data-kit/actions/runs/36231780343/job/108376173312；同SHA重跑：https://github.com/PureSaber/quant-data-kit/actions/runs/36231780343/job/108377000026。
