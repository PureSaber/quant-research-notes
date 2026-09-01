# P0 GitHub治理控制

更新时间：2026-09-01（Asia/Shanghai）

## 结论

M8的14个运行时仓库现均为public，并全部启用两组`active`仓库Ruleset：`governance-default-branch`保护默认分支，`governance-release-tags`保护`refs/tags/v*`。`quant-crypto-basis`和`quant-futures-spread`由仓库所有者明确授权从private改为public，随后通过真实PR、默认分支CI、Ruleset、Secret Scanning和Push Protection验收；这次可见性变更是经审计的治理决定，不是对套餐限制的未授权绕过。

该平台控制不改变[M8权威状态](validation/m8/M8_STATUS.md)：`M8_SOFTWARE_RELEASE_COMPLETE / MARKET_DATA_GA_BLOCKED`。真实市场GA阻塞由[M9 Market Data GA](https://github.com/PureSaber/quant-research-notes/milestone/1)跟踪。

## 14个public仓的实时控制

| 仓库 | 默认分支 | 默认分支Ruleset | `v*`tag Ruleset |
|---|---|---:|---:|
| `a-share-multifactor` | `main` | [`21930008`](https://github.com/PureSaber/a-share-multifactor/settings/rules/21930008) | [`21930010`](https://github.com/PureSaber/a-share-multifactor/settings/rules/21930010) |
| `quant-agent` | `master` | [`21930011`](https://github.com/PureSaber/quant-agent/settings/rules/21930011) | [`21930013`](https://github.com/PureSaber/quant-agent/settings/rules/21930013) |
| `quant-crypto-basis` | `main` | [`22001086`](https://github.com/PureSaber/quant-crypto-basis/settings/rules/22001086) | [`22001092`](https://github.com/PureSaber/quant-crypto-basis/settings/rules/22001092) |
| `quant-data-kit` | `main` | [`21929867`](https://github.com/PureSaber/quant-data-kit/settings/rules/21929867) | [`21929882`](https://github.com/PureSaber/quant-data-kit/settings/rules/21929882) |
| `quant-execution` | `main` | [`21930016`](https://github.com/PureSaber/quant-execution/settings/rules/21930016) | [`21930020`](https://github.com/PureSaber/quant-execution/settings/rules/21930020) |
| `quant-factors` | `main` | [`21930024`](https://github.com/PureSaber/quant-factors/settings/rules/21930024) | [`21930029`](https://github.com/PureSaber/quant-factors/settings/rules/21930029) |
| `quant-futures-spread` | `main` | [`22001097`](https://github.com/PureSaber/quant-futures-spread/settings/rules/22001097) | [`22001099`](https://github.com/PureSaber/quant-futures-spread/settings/rules/22001099) |
| `quant-lab` | `main` | [`21930031`](https://github.com/PureSaber/quant-lab/settings/rules/21930031) | [`21930032`](https://github.com/PureSaber/quant-lab/settings/rules/21930032) |
| `quant-paper-sim` | `main` | [`21930039`](https://github.com/PureSaber/quant-paper-sim/settings/rules/21930039) | [`21930041`](https://github.com/PureSaber/quant-paper-sim/settings/rules/21930041) |
| `quant-pipeline` | `main` | [`21930043`](https://github.com/PureSaber/quant-pipeline/settings/rules/21930043) | [`21930047`](https://github.com/PureSaber/quant-pipeline/settings/rules/21930047) |
| `quant-portfolio` | `main` | [`21930051`](https://github.com/PureSaber/quant-portfolio/settings/rules/21930051) | [`21930053`](https://github.com/PureSaber/quant-portfolio/settings/rules/21930053) |
| `quant-report-hub` | `main` | [`21930055`](https://github.com/PureSaber/quant-report-hub/settings/rules/21930055) | [`21930059`](https://github.com/PureSaber/quant-report-hub/settings/rules/21930059) |
| `quant-risk-monitor` | `main` | [`21930061`](https://github.com/PureSaber/quant-risk-monitor/settings/rules/21930061) | [`21930065`](https://github.com/PureSaber/quant-risk-monitor/settings/rules/21930065) |
| `quant-workspace` | `main` | [`21930066`](https://github.com/PureSaber/quant-workspace/settings/rules/21930066) | [`21930067`](https://github.com/PureSaber/quant-workspace/settings/rules/21930067) |

默认分支Ruleset的共同控制为：

- 目标为`~DEFAULT_BRANCH`，`enforcement=active`，无bypass actor；
- 禁止删除和non-fast-forward更新，即禁止删除默认分支和force push；
- 变更必须通过PR，要求解决review conversation；
- 要求各仓当前真实存在的CI检查，`strict_required_status_checks_policy=true`，即合并前必须基于最新目标分支状态通过；
- `required_approving_review_count=0`，原因见下文。

`a-share-multifactor`要求Ubuntu/Windows×Python3.10/3.11/3.12共6个检查；其余13个public仓要求Python3.10/3.11/3.12共3个现有检查。tag Ruleset共同匹配`refs/tags/v*`，禁止update和deletion，无bypass actor；已有tag不得移动、重建或删除。

## 原private仓公开化闭环

授权前，两个private仓的Ruleset API均因GitHub Free套餐返回HTTP 403。2026-09-01，仓库所有者在[Issue#16](https://github.com/PureSaber/quant-research-notes/issues/16)治理审计中明确授权公开化；变更后完成以下验收：

- `quant-crypto-basis`：[PR#5](https://github.com/PureSaber/quant-crypto-basis/pull/5)合并前检查成功，默认HEAD运行[`33493519524`](https://github.com/PureSaber/quant-crypto-basis/actions/runs/33493519524)成功，Ruleset`22001086/22001092`均为`active`且无bypass actor；
- `quant-futures-spread`：[PR#5](https://github.com/PureSaber/quant-futures-spread/pull/5)合并前检查成功，默认HEAD运行[`33493532518`](https://github.com/PureSaber/quant-futures-spread/actions/runs/33493532518)成功，Ruleset`22001097/22001099`均为`active`且无bypass actor；
- 两仓均启用Secret Scanning和Push Protection，且未引入deploy key或Actions Secret。

公开化不改变软件认证边界：两个仓仍只在fixture、研究、回测或paper范围内通过验证，不得据此宣称真实市场数据认证、平台GA或实盘能力。完整审计结论保留在Issue#16最新评论，历史正文中的private状态仅表示事故发生时事实。

## 单人维护下的0审批设计

PureSaber当前是单人维护账号。若现在要求1名独立审批者，自有PR将没有合格审阅者并永久无法合并。当前因此保留`required_approving_review_count=0`，同时依靠强制PR、严格required checks、禁止force push/删除、review conversation解决和不可变`v*`tag维持可审计门禁。`CODEOWNERS`若后续加入，只承担责任路由，不能伪装为独立审批。

以下条件同时满足时，立即将public仓默认分支Ruleset升级为至少1名独立审批者：

1. 至少有一名持续可用、具备相应仓库review权限且不是该PR作者的独立维护者；
2. 已明确review职责、响应边界和离职/不可用时的替代责任人；
3. 用测试PR验证1名审批、required checks和最新分支要求不会形成死锁；
4. 更新本说明并保存Ruleset变更前后JSON和测试PR/CI URL。

## Break-glass

Break-glass仅用于Ruleset自身或GitHub平台故障导致紧急安全/数据完整性修复无法通过正常PR门禁。红色CI、缺少独立审批、赶发布日期或一般操作不便不构成使用理由。

使用流程：

1. 能正常访问GitHub时，先在`quant-research-notes`创建公开且不含敏感信息的治理Issue，记录目标仓库、Ruleset名称/ID、原因、影响范围、操作者、开始时间、计划恢复时间和关联修复PR；平台故障使事前记录不可能时，恢复后24小时内补录。
2. 保存Ruleset完整JSON和GitHub规则历史链接；仅临时把目标Ruleset的`enforcement`设为`disabled`，不得删除Ruleset、扩大匹配范围、添加永久bypass actor、force push、删除默认分支或移动/重建tag。
3. 紧急变更仍必须使用PR并保留可运行的检查；若平台故障使检查不可用，记录失败证据并在恢复后补跑，未补跑前不得发布tag或宣称通过。
4. 变更完成后立即把原Ruleset恢复为`active`，重新读取JSON并验证规则定义、目标、required checks和bypass actor与停用前一致。
5. 在治理Issue中记录停用/恢复时间、Ruleset历史、修复PR、补跑CI、恢复后API JSON和一次受保护PR验证；只有恢复验证通过后才能关闭Issue。

## 只读复核命令

```powershell
gh api "repos/PureSaber/<repo>/rulesets?includes_parents=true"
gh api "repos/PureSaber/<repo>/rulesets/<ruleset-id>"
gh api "repos/PureSaber/<repo>/branches/<default-branch>"
gh run list --repo "PureSaber/<repo>" --branch "<default-branch>" --limit 1
```

复核必须记录精确仓库、Ruleset ID、`enforcement`、条件、规则、bypass actor、required check名称、默认分支HEAD和CI URL。任何403或套餐限制必须保留原始API错误，不得用文档声明替代平台保护。
