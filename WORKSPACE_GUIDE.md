# 工作区维护说明

更新时间：2026-09-30。

## 三类目录

|目录用途|版本依据|更新方式|
|---|---|---|
|日常源码检出|仓库默认分支或正在审查的PR|确认工作树干净、没有独有未推送提交后，fetch并仅快进默认分支|
|研究集成环境|`quant-workspace/profiles/research-workbench/stack.json`中的精确提交|使用该配置的bootstrap与verify；依赖更新通过新的集成PR验收|
|冻结历史研究和前向账户|登记时的代码身份、依赖锁、输入与账户定义哈希|保持原样；变更必须另建有明确起点和证据的研究版本，不能直接pull覆盖|

工作树clean只说明没有未提交改动，不代表本地HEAD等于远端默认分支，也不代表已安装环境匹配当前源码。
仓库版本号、源码提交和研究登记是不同的身份，不能互相替代。

## 日常源码同步

先检查`git status --short --branch`、`git branch -vv`及运行中的研究任务，再执行`git fetch origin --prune`。
只有目标默认分支没有独有本地提交且没有其他任务使用时，才切回默认分支并执行`git merge --ff-only origin/<default-branch>`。
`quant-agent`当前默认分支仍为`master`，其余按实际仓库元数据判断，不批量猜测。

有未提交工作、分叉历史或冻结代码身份时应停止同步并保留证据；不要用reset、强推或批量删除来制造“干净”。
合并了功能PR的历史研究目录也可能仍需保留原提交。日常源码副本与冻结目录可以同时存在。

## 依赖更新验收

- 将`pyproject.toml`、约束输入及其生成的锁文件作为同一个变更审查。Dependabot修改声明不会自动保证自定义`.lock`文件已重建。
- 使用仓库记录的生成器和最低支持Python版本重建锁，保留无关依赖的现有版本偏好；禁止手改传递依赖来绕过解析失败。
- 从锁安装后，再以`--no-deps --no-build-isolation`安装当前项目并检查依赖兼容性，最后运行仓库的完整测试、覆盖率与CI矩阵。
- Pipeline的研究约束还必须与`requirements-research.lock`一致，否则CI可能在旧版依赖上通过；基础锁和研究锁分别说明适用范围。
- 单仓CI通过不等于跨仓集成通过。Workspace需要Windows/Linux上的独立折和连续账户检查；Studio需要上游模板集成检查。
- 取消的检查不算通过，基于旧主线通过的PR也需要满足当前分支保护要求后才能合并。

## 保留研究边界

M8状态保持`M8_SOFTWARE_RELEASE_COMPLETE / MARKET_DATA_GA_BLOCKED`。
独立归档与恢复、Crypto八流连续30日、国内授权L2认证仍分别由Issue[#11](https://github.com/PureSaber/quant-research-notes/issues/11)、[#12](https://github.com/PureSaber/quant-research-notes/issues/12)、[#13](https://github.com/PureSaber/quant-research-notes/issues/13)跟踪。
目录同步、依赖更新和CI成功均不能关闭这些真实市场门禁。

9月26日登记的四ETF前向账户在9月30日仍为零有效观察：重新采集的五条历史分红经济字段未变，但`captured_at`更新与冻结历史前缀契约冲突。
原账户和执行代码保留，来源及失败证据已保存于[不可变阻断记录](https://github.com/PureSaber/quant-research-notes/blob/16726b41e5dbdf11dbfb5af31e8c9c835eb65165/validation/risk-pit-20260926/evidence/forward/20260930T141242Z/README.md)。
该阻断需要单独处理采集溯源与经济记录的版本契约、回归验证和登记安排，不能靠改写旧时间戳、放宽冻结校验或补填观察解决。

当前风险研究仍是market统计代理，完整Barra描述子、宽截面数据及校准尚未完成；既有历史结果不支持策略优于买入持有。
具体数据与统计边界见[历史验收](validation/risk-pit-20260926/VALIDATION.md)和[历史结果](validation/risk-pit-20260926/RESULTS.md)。
