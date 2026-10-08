# Crypto L2 软件与部署准备

2026-10-08 用户确认暂无独立归档设备，本轮完成软件验收、配置和部署步骤。
本页不启动常驻进程或定时任务，不替代 M9 的真实运行证据。

## 已验收与当前阻断

- QDK 固定提交 `61b571bdb9bba5d0a8c3aff8b406864539d0a9fc`：Windows/Python 3.12.14 完整测试 856 通过、2 跳过，24 个核心模块纯分支覆盖均不低于 90%，全源码 83.09%。
- 使用真实 Windows 物理磁盘探针，在三个不同的 C 盘目录运行原生 CLI preflight，实际返回 `PAUSED_PREFLIGHT_FAILED`：热数据与归档属于同一物理设备。
- 八条流均为 PAUSED、收到消息 0、生成 Raw 段 0、归档回执为空、连续天数 0、`long_running_capture_started=false`、`market_data_certified=false`。这是阻断机制通过的证据，不是归档成功。
- [部署证据摘要](readiness.json)只保存容量和状态，不上传本机原始目录、卷标或运行数据。

## 容量与设备要求

本机唯一可用盘总容量约 951.87 GiB，验收时剩余约 343 GiB；内存约 31.37 GiB。
当前策略热数据上限 150 GiB，系统剩余空间底线为 `max(总容量 × 20%, 100 GiB)`，
在此盘约为 190.37 GiB。因此只有约 153 GiB 能用于新增写入，热区写满后余量很小，
还须扣除恢复临时文件、日志、其他软件和已有热数据。不能将 343 GiB 全部作为数据预算。

需要能被物理设备探针确认独立的归档块设备及足够剩余空间。配置保留的
150 GiB 归档余量是门槛，不能直接当成 30 天总容量估算。现有 Windows 实现要求
本地盘符并读取物理磁盘 extents；UNC/NAS 路径与 S3 URL 没有完成此后端适配，
不能直接填入模板后声称支持。另一分区或同盘另一目录也不满足独立归档。

容量规划须从有代表性的受控采样实测 Raw、Normalized、审计与归档的总增长速率。
若每天总增长为 D GiB，至少估算 30 × D，并另计重连/重放、恢复空间与安全余量。
采集器不会自动删除已归档的热数据；即使归档足够大，热区仍可能先达到 150 GiB。
须另行审查留存方案，只能对已验证归档及恢复的数据制定显式清理流程。

## 固定版本安装与预检

在准备好的运行目录执行以下 PowerShell 命令；首次 clone 使用不存在的目标目录。
已有本轮验收环境可以直接复用，无需再次安装。

```powershell
git clone https://github.com/PureSaber/quant-data-kit.git qdk-capture-release
Set-Location qdk-capture-release
git checkout --detach 61b571bdb9bba5d0a8c3aff8b406864539d0a9fc
py -3.12 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r requirements.lock
& .\.venv\Scripts\python.exe -m pip install --no-deps --no-build-isolation -e .
& .\.venv\Scripts\python.exe -m pip check
```

将 [capture.template.json](capture.template.json) 复制到运行目录的 `capture.json`，
填写三个已存在的绝对目录。JSON 中 Windows 路径需使用 `/` 或双反斜杠。
不得加入凭据字段；默认八条公开流保持不变。先只执行：

```powershell
& .\.venv\Scripts\python.exe -m quant_data_kit.capture_v2.cli .\capture.json --mode preflight
```

preflight 不开网络，仍会创建本地运行回执，并在独立设备满足条件时执行归档复制、
临时恢复和 SHA-256 校验。只有状态为 `PREFLIGHT_PASSED_NETWORK_NOT_STARTED`、
退出码为 0 且存在有效归档恢复回执，才进入网络探测阶段。保存原始回执与对应提交。
当前无独立盘时应继续拒绝，不修改磁盘探针或容量门槛。

## 外部条件具备后的验收顺序

1. 预检成功后，显式执行有界公开行情探测：`python -m quant_data_kit.capture_v2.cli capture.json --mode probe --max-messages 3`。其成功只证明该次连通和准入。
2. 实测八条流的峰值/常态增长、重连与恢复开销，确认网络、供电、睡眠策略、容量和留存责任。
3. 审查完成后才使用 `--mode run --confirm-long-running` 开始持续采集，并保留中断、重同步、时间覆盖和质量证据。任何中断均按原验收规则计算，不能把离散片段拼成连续 30 天。
4. 独立验证归档恢复、八流 30 个连续自然日及授权国内 L2 来源，分别签收 Notes #11/#12/#13。国内 L2 授权不由公开 Crypto 数据或软件测试替代。

当前三个 M9 问题继续开放；本轮不宣称市场数据 GA 或实盘可用。
