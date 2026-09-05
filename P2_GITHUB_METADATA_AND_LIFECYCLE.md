# P2 GitHub元数据与生命周期闭环

更新时间：2026-09-05（Asia/Shanghai）

## 结论

18个治理范围仓库的GitHub topics与description已按实际职责校准，homepage保持为空，未虚构项目站点。17个活跃仓继续维护；`spread-backtest-viz`是唯一生命周期收敛对象，已在修复安装根因、取得三版本绿色CI、建立恢复锚点并获得维护者明确授权后归档。

该闭环不改变[M8权威状态](validation/m8/M8_STATUS.md)：`M8_SOFTWARE_RELEASE_COMPLETE / MARKET_DATA_GA_BLOCKED`。元数据中的研究、回测、fixture或paper trading表述不构成真实市场数据认证、平台GA或实盘批准。

## 元数据

- 18/18仓topics与治理清单一致；
- 18/18仓description与职责一致，其中`quant-futures-spread`、`quant-paper-sim`、`quant-risk-monitor`和`quant-regime`补齐缺失描述；
- `quant-data-kit`、`quant-workspace`、`quant-research-notes`和`spread-backtest-viz`修正过时或过窄描述；
- 18/18仓homepage保持`null`；
- `quant-crypto-basis`和`quant-futures-spread`保持public，文档不再保留private旧口径。

## `spread-backtest-viz`归档

归档前根因不是shim代码失败，而是`pyproject.toml`依赖未发布到PyPI的`quant-report-hub>=0.2.0`。PR[#1](https://github.com/PureSaber/spread-backtest-viz/pull/1)将依赖固定到已验证的canonical commit`b334b34a61f6e563916add32af94d70dc7ed7494`，同时收紧workflow权限、固定Action完整SHA并禁用checkout凭据持久化。PR检查与默认分支运行[`33502122906`](https://github.com/PureSaber/spread-backtest-viz/actions/runs/33502122906)在Python3.10、3.11、3.12均成功。

2026-09-05，维护者明确授权保持仓库无LICENSE、创建两个annotated tag并归档：

| tag | tag object | peeled commit | 用途 |
|---|---|---|---|
| `spread-backtest-viz-v0.1.0-pre-merge` | `bed66d8f776a1d4cff0b062b8f80ebadf92f363b` | `cf492d3e73ceee712889e74dab0766e11cc48bee` | 合并前实现的恢复锚点；在2026-09-05新建，不伪称历史上已存在 |
| `v0.2.0` | `a5bdd78e7dd789400f66b297acf5032c41d31973` | `8b80ceebe84492de60133f2f9432cf7f002f8327` | 最终绿色兼容shim |

归档后实时状态为：`public`、`archived=true`、`disabled=false`、`license=null`、默认分支`master@8b80ceebe84492de60133f2f9432cf7f002f8327`，只有一个默认分支、两个annotated tag、0个open PR、0个open Issue、0个GitHub Release。归档只把仓库设为只读，没有删除Git历史，也没有移动、重建任何既有tag或执行force push。

## 恢复原则

若确需恢复维护，必须重新获得明确授权后将`archived=false`，并以`v0.2.0`作为最终兼容shim基线；读取合并前实现时使用`spread-backtest-viz-v0.1.0-pre-merge`。两个tag不得移动、重建或删除。canonical实现始终是[`quant-report-hub`](https://github.com/PureSaber/quant-report-hub)，新项目不得重新依赖已归档shim。
