# PureSaber量化仓库P0-P2最终独立只读验收

完成时间：2026-09-05T07:25:49Z

## 结论

| 阶段 | 结论 | 实时验收摘要 |
|---|---|---|
| P0 | `PASS` | 14/14运行时仓public；14个M8 annotated tag对象与peeled commit精确匹配；28个branch/tag Ruleset全部active、无bypass；45个required check上下文成功；14/14启用Secret Scanning与Push Protection；跨仓健康检查成功 |
| P1 | `PASS` | 17/17治理文件与Dependabot安全更新完整；16/16个public仓当前HEAD CodeQL成功；三类public open alerts为0；34个workflow、92个外部Action引用、37次checkout全部合规；陈旧可达分支债务为0 |
| P2 | `PASS` | 18/18 topics与description匹配；7个治理/收口PR均merged且精确merge HEAD运行成功；`spread-backtest-viz`tag、无LICENSE与归档状态全部符合授权 |
| 总评 | `PASS` | P0-P2治理与生命周期收口完成；权威状态仍为`M8_SOFTWARE_RELEASE_COMPLETE / MARKET_DATA_GA_BLOCKED` |

验证负责人自行读取GitHub实时状态，没有修改本地仓库文件、GitHub设置、Issue、PR、tag或ref，也没有沿用未签发的部分结论。

## P0关键证据

- 14个M8tag均为annotated tag；线上tag object与peeled commit逐仓精确匹配[`validation/m8/M8_STATUS.md`](../m8/M8_STATUS.md)。
- 28个branch/tag Ruleset全部`active`、`bypass_actors=[]`、`current_user_can_bypass=never`。
- branch Ruleset均匹配默认分支并启用`deletion`、`non_fast_forward`、`pull_request`和strict`required_status_checks`；tag Ruleset匹配`refs/tags/v*`并禁止update/deletion。
- 14仓当前默认HEAD的45个required check上下文全部成功，Secret Scanning与Push Protection均enabled。
- 跨仓健康检查成功；release日志确认不可变manifest精确包含14个M8项目。private仓库精确运行与作业信息不在公开报告中披露。

## P1关键证据

- 17仓默认HEAD递归Git tree均包含`SECURITY.md`、`CODEOWNERS`、Issue/PR模板与Dependabot配置；17/17`automated-security-fixes`为enabled且未暂停。
- 16个public仓当前默认HEAD CodeQL成功；17仓Dependabot open alerts为0，16个public仓CodeQL与Secret Scanning open alerts均为0。
- 34/34个workflow声明最小顶层permissions；92/92个外部Action固定完整40位SHA；37/37次checkout设置`persist-credentials:false`；无作业级权限扩大或`pull_request_target`。
- 非默认分支只剩两条活动Dependabot PR分支和`quant-portfolio`的3个unique commit保留分支；没有满足安全删除条件的陈旧可达分支。

## P2关键证据

- 18仓topics、description与职责清单逐一匹配，homepage全部为空。
- 5个首轮文档PR与2个归档收口PR均已合并；其精确merge HEAD CI、CodeQL或Contract运行全部成功。private仓库的精确PR信息不在公开报告中披露。
- `spread-backtest-viz`实时为`public`、`archived=true`、`disabled=false`、`license=null`、唯一默认分支`master@8b80ceebe84492de60133f2f9432cf7f002f8327`；CI[33502122906](https://github.com/PureSaber/spread-backtest-viz/actions/runs/33502122906)成功。
- `spread-backtest-viz-v0.1.0-pre-merge`tag object`bed66d8f776a1d4cff0b062b8f80ebadf92f363b`精确指向`cf492d3e73ceee712889e74dab0766e11cc48bee`。
- `v0.2.0`tag object`a5bdd78e7dd789400f66b297acf5032c41d31973`精确指向`8b80ceebe84492de60133f2f9432cf7f002f8327`。
- 两个tag均为annotated tag，tagger为`PureSaber <88314620+PureSaber@users.noreply.github.com>`；恢复tag注释明确它在2026-09-05新建，不冒充历史release。
- 仓库0个open PR、0个open Issue、0个Release；`cf492d3...8b80cee`的compare为ahead=2、behind=0且merge-base为`cf492d3...`，前代历史仍在最终HEAD祖先链。

## 非阻塞残余风险

1. private`quant-infra-workspace`的CodeQL与Secret Scanning受当前套餐限制，不能声称17仓获得同等扫描覆盖。
2. 验收时仍有未合并的活动Dependabot版本建议；默认HEAD保持全绿且安全告警为0。
3. `quant-portfolio`unique分支的3个独有commit必须保留。
4. 单人维护Ruleset的`required_approving_review_count=0`，没有第二个人账号审批；两个新tag为annotated但未签名。
5. M9 Issues[#11](https://github.com/PureSaber/quant-research-notes/issues/11)、[#12](https://github.com/PureSaber/quant-research-notes/issues/12)、[#13](https://github.com/PureSaber/quant-research-notes/issues/13)仍open，继续阻断真实市场数据GA。

## 证据完整性

[公开证据清单](PUBLIC_EVIDENCE_MANIFEST.json)固定全部最终快照的SHA-256。只涉及public仓库的原始归档快照随本报告发布；含private仓库精确状态的机器快照仅登记SHA-256并按公开披露规则保留在受限位置。
