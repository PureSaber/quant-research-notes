# 2026-10-08 宿主 iframe 异常复验与排查交接

当前状态：能在 Codex 内置浏览器复现，尚未取得抛错脚本 URL 或调用栈。不能声明已经修复，也不能据此认定具体宿主模块。独立打开完整报告是已验证可用的查看路径。

## 本次实际对照

沿用[两份静态 HTML](../p0-p2-20261003/reproductions/fund-embed/embedded.html)，服务绑定 `127.0.0.1:8878`。它们不包含业务脚本、Plotly 或外部资源。

|页面|结果|
|---|---|
|`embedded.html` 内嵌 `child.html`|父/子 DOM 均为 0 个 script 节点；子页正常显示；记录到下述异常|
|独立 `child.html`，含重载|error 日志为空|
|独立基金原生 `report.html`|图表、中文持仓表及合成标识正常显示；1 个 Plotly 图表，缩放按钮启用；error 日志为空|

实际错误记录时间为 `2026-10-08T06:04:23.974Z`：

```text
Uncaught TypeError: Failed to execute 'observe' on 'MutationObserver': parameter 1 is not of type 'Node'.
```

浏览器日志接口只返回 level、message、timestamp；本条没有来源 URL，也没有 stack。诊断过程中一次只读 DOM 查询本身触发的工具 TypeError 不计入应用错误。以上结果不代表 Chrome/Edge 对照已执行，也不代表每次重载都会新产生一次异常。

报告为本轮 `quant-fund demo --historical-terms` 生成的合成输入，equal 策略运行区间 2026-07-01—2026-08-31。未用公开净值拼装“真实交易”。报告及输入在本轮数据清理范围内；最小复现 HTML 为仓库源码，保留用于后续排查。

## 宿主维护者的下一步

1. 在同一宿主构建中用这两个静态文件复现，并在异常抛出点暂停，取得包含隔离执行环境的完整调用栈、来源脚本和行列号。记录宿主构建、WebView/Chromium 版本及是否只在自动化连接时出现。
2. 在 `observe` 调用处检查实际 target、节点所属 document/window、frame 是否已 detach、导航/重载生命周期。跨 frame 对象处理和过早初始化只是待验证方向，不能代替调用栈根因。
3. 根据证据修正节点选择、所属执行环境或导航期间 observer 的创建与清理时机，并加入静态 iframe、新增/移除 iframe、重载、嵌套 frame 的回归测试。
4. 用相同无脚本样本和真实报告复验：子页渲染正常、日志无异常、重载后无残留 observer；再回到 Studio 内嵌报告验收。

业务仓现有“独立打开完整报告”入口对应 [Studio #22](https://github.com/PureSaber/quant-studio/pull/22)。不能通过全局覆盖 MutationObserver、吞异常或降低 iframe 安全策略宣称宿主修复。

本代理可以维护量化仓、准备复现和核验修复；当前未获得宿主相关源码和可定位调用栈，不能直接交付宿主内部修复。此文是可交接的排查材料，未代用户发送给外部客服或创建外部反馈工单。
