# 基金嵌入报告控制台错误的最小复现

2026-10-04，重新打开已保存的基金合成运行，确认嵌入报告仍出现MutationObserver错误。随后移除Studio、基金代码、Plotly及所有页面JavaScript，用两个静态HTML重现了完全相同的错误。问题已缩小到宿主浏览器或自动化环境的iframe处理；具体注入来源尚未得到调用栈证据，不能宣布修复或确定责任组件。

## 实际对照

|页面|页面脚本|实际结果|
|---|---|---|
|Studio中的原基金报告|原报告含Plotly|出现一次MutationObserver错误，图表与表格可见|
|静态父页嵌入静态子页|父页0、子页0个script节点|出现一次完全相同错误，子页正常显示|
|直接打开同一静态子页|0个script节点|无错误或警告|

错误文本：`Uncaught TypeError: Failed to execute 'observe' on 'MutationObserver': parameter 1 is not of type 'Node'.`

两个静态源文件没有脚本，也没有MutationObserver文本。浏览器实际DOM检查同样为零个script节点。错误在Codex内置浏览器中被记录，复现不依赖业务应用或图表库；宿主在隔离环境执行的脚本不一定出现在页面script节点中。当前证据支持排除“只有基金报告代码才会触发”的判断，尚不支持定位具体宿主脚本或对其他浏览器作结论。

## 复现与证据

最小源文件为[embedded.html](reproductions/fund-embed/embedded.html)和[child.html](reproductions/fund-embed/child.html)。在该目录运行：

```powershell
python -m http.server 8774 --bind 127.0.0.1
```

在相同浏览器环境分别打开`http://127.0.0.1:8774/embedded.html`和`http://127.0.0.1:8774/child.html`，比较控制台错误。本文记录的是实际两标签对照，不能把复现命令当成未执行的验收结论。

[脱敏回执](evidence/fund-embed-diagnostic.json)保留三组日志、DOM脚本数量、源文件及截图哈希。诊断使用Studio合并提交`6207b8eccd5488e028139ba5e7abf4d63c9704ef`及原基金合成运行；没有重跑策略或修改原产物。临时服务与标签已关闭。

## 后续与验收边界

继续取得宿主错误的具体来源或在独立浏览器环境比较；修复后重新验收嵌入报告。当前保留P1.1的兼容性缺口，不通过吞掉异常、覆盖MutationObserver或删除嵌入报告来宣称成功。此次只新增诊断证据和最小复现，无生产代码或冻结研究环境变化。

## 2026-10-07后续

[Studio#22](https://github.com/PureSaber/quant-studio/pull/22)为成功报告增加“独立打开完整报告”，使用与iframe相同的原生报告路径并保留相对链接。两项入口回归、完整234项测试及主线集成检查通过；本机HTTP验证入口、报告资源和原有嵌入策略正常，查看前后30份已保存文件哈希未变，见[HTTP回执](evidence/http-acceptance-20261007.json)。无HTML报告的成功模拟盘及中断记录均不显示报告入口，符合已有契约。

本轮浏览器策略阻止本机视觉控制，没有取得新的截图、宿主注入调用栈或独立浏览器对照。独立打开入口改善查看流程，不代表MutationObserver问题已修复；本节不覆盖上方历史复现证据。
