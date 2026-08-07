# TaskSolver 运行模式：模拟 / Cloud / IDE

> 来源： [React_TaskSolver](https://github.com/PureSaber/React_TaskSolver) 使用实践（2026-08-07）  
> 避免把「脚本演示」当成「Cursor Agent 真跑了三轮」。

## 三种模式对比

| 模式 | Agent 是否真干活 | Stop Hook 是否自动触发 | 典型用途 |
|------|------------------|------------------------|----------|
| **脚本模拟** `simulate-*.ts` | 否（脚本直接改文件） | 否 | 快速验证编排器逻辑、CI、无 Agent 环境 |
| **Cloud Agent 窗口** | 是（对话里读文件、改代码、跑命令） | **否** — 需手动调用 `hook:stop` | Cursor Cloud / 无本地 IDE Hook |
| **Cursor IDE + hooks.json** | 是 | **是** — 每轮 Agent 结束自动触发 | 日常开发（推荐） |

**编排器**（lint、`done_when`、写 `state/*.json`）在三种模式下都可以是**真的**；差别在于 **谁改代码** 以及 **Hook 是否自动接上**。

## 脚本模拟（假 Agent，真编排器）

示例：

```bash
cd React_TaskSolver
npx tsx scripts/simulate-mini-score-loop.ts
```

- 会调用真实的 `Orchestrator.decide()` 和评测命令。
- 「Agent 思考」是脚本里写死的文案，文件用 `writeFileSync` 修改。
- 适合：先理解「发题 → 检查 → 下一题」流程，不消耗 Agent 轮次。

相关 Goal：`goals/beginner-demo.yaml`、`goals/mini-score-loop.yaml`。

## Cloud Agent 窗口（真 Agent，手动 Hook）

在 Cloud 对话里可以让 Agent 真改代码、真跑评测，但 **Stop Hook 不会在每轮结束时自动执行**，需要手动触发（等价于 IDE 里 Hook 跑的那一步）。

### 前置

```bash
npm ci && npm run build
cp goals/mini-score-loop.active-goal.json state/active-goal.json
npm run task:sync-hooks -- goals/mini-score-loop.yaml
```

### 手动触发 Stop Hook

每完成一轮 Agent 工作后，在终端执行（`loop_count` 从 0 递增）：

```bash
echo '{"status":"completed","loop_count":0,"workspace_roots":["/path/to/React_TaskSolver"]}' | npm run hook:stop
```

下一轮改为 `loop_count":1`，再下一轮 `2`，以此类推。

- 返回 JSON 里若有 `followup_message` → 还有任务，继续让 Agent 干活。
- 返回 `{}` 且无 followup → 通常表示 Goal `done` 或停止。

### 查看进度

```bash
npm run task:status
npm run task:goal -- status   # 或对话里 /goal
```

### mini-score-loop 真跑时间线（实测）

| 轮次 | Agent | 编排器（hook:stop 后） |
|------|-------|------------------------|
| 1 | 读 `demo/mini_classifier.py`，跑评测 → 80/100 FAIL | `followup`，继续 T1 |
| 2 | 改阈值 60→50，再评测 → 100 PASS | `followup`，仍 T1（lint 已过，评测在 done_when 里验） |
| 3 | 无新改动 | `stop`，`status: done` |

## Cursor IDE（真 Agent，自动 Hook）

1. 用 Cursor **桌面版**打开 `React_TaskSolver`（或已安装 `react-task-solver` 的项目）。
2. 确认 `.cursor/hooks.json` 指向 `dist/hooks/orchestrate-stop.js`，且已 `npm run build`。
3. 配置 `state/active-goal.json` 指向目标 YAML。
4. 在 Agent 对话中说：

   ```text
   Run the TaskSolver workflow for goals/mini-score-loop.yaml
   ```

5. 每轮 Agent 结束后 **Stop Hook 自动运行**，并注入 `followup_message`（无需手敲 `echo | hook:stop`）。

另开终端监视：`npm run task:status --watch`。

## 和 Codex `/goal` 的关系（简记）

| | Codex `/goal` | TaskSolver |
|--|---------------|------------|
| 定目标 | 对话里 `/goal 一段话` | YAML Goal 文件 |
| 过关判定 | 模型 + 证据，产品内置循环 | `done_when` / 自定义评测脚本 exit code |
| 生命周期 | `/goal pause/resume/clear` | 同名命令 + `npm run task:goal` |

量化场景可参考 Goal：`goals/cross-product-research.yaml`（回测 CSV + Python 断言指标）。

## 相关仓库文档

- [React_TaskSolver README](https://github.com/PureSaber/React_TaskSolver)
- [初学者指南](https://github.com/PureSaber/React_TaskSolver/blob/master/docs/beginner-guide.md)
- [mini-score-loop 演示](https://github.com/PureSaber/React_TaskSolver/blob/master/docs/mini-score-loop.md)
