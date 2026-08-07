# Cursor Cloud Agent 访问 GitHub 私有仓库

> 来源：2026-08-07 实践 — 在 Cloud Agent 中读取/更新 `PureSaber/agent-toolkit`（私有）  
> 关联仓库：[React_TaskSolver](https://github.com/PureSaber/React_TaskSolver)、[agent-toolkit](https://github.com/PureSaber/agent-toolkit)（private）

## 问题现象

| 场景 | 典型结果 |
|------|----------|
| Cloud Agent 只绑定公开仓（如 `React_TaskSolver`） | 对话里 `gh repo view PureSaber/agent-toolkit` → **404** |
| 终端 `gh auth login` 切到个人账号后 | `gh repo view` / `gh api` **可读** 私有仓 |
| 同一环境下 `git clone` 私有仓 | 仍可能 **Repository not found**（Cloud 工作区 git 凭据 ≠ 终端 `gh`） |
| 用 `cursor[bot]` 或 Cloud 默认 token 推 `quant-research-notes` | **403** — 无写权限 |

结论：**「终端能看见」≠「Agent 工作区能 clone」≠「能 git push」**，需分层处理。

## 三层授权（各司其职）

| 层 | 做什么 | 你怎么配 | 解决什么问题 |
|----|--------|----------|--------------|
| **A. 终端 `gh`** | 本机/Cloud 终端里 `gh repo view`、`gh api`、有时 `git push` | `gh auth login` → `gh auth switch -u <你的用户名>` | 人工在终端验证私有仓、用 API 改文件 |
| **B. Cursor 账号连 GitHub** | Cursor 产品侧识别你的 GitHub 身份 | Cursor Settings → **Connect GitHub**（授权 `repo` 等 scope） | Cloud / IDE 集成、部分 Agent 能力 |
| **C. Cloud Environment 仓库列表** | **新一次** Cloud Agent run 的工作区挂载范围 | Environment 配置里加入目标私有仓 | Agent **对话内**直接读/改该仓代码 |

**重要：** 已在跑的 Cloud Agent **不会**因你后来在终端 `gh auth` 而自动获得新仓库的工作区；通常需要 **新开 run** 且 Environment 已包含该私有仓。

## 可复现步骤（推荐顺序）

### 1. 检查当前身份

```bash
gh auth status
```

期望：Active account 为你的个人账号（如 `PureSaber`），且 token scopes 含 `repo`。

若有多账号：

```bash
gh auth switch -u PureSaber
```

### 2. 验证私有仓可读（终端）

```bash
gh repo view PureSaber/agent-toolkit --json name,isPrivate,defaultBranchRef
gh api repos/PureSaber/agent-toolkit/contents/README.md --jq .name
```

若仍 404：GitHub 网页确认你对该私有仓有 access；或重新 `gh auth login` 并勾选私有仓权限。

### 3. Cursor 侧连接 GitHub

1. 打开 Cursor → Settings → GitHub → Connect / Re-authorize  
2. 确认授权包含私有仓库（classic token 需 `repo`；fine-grained 需对该仓 Read/Write）

### 4. Cloud Environment 绑定私有仓（Agent 工作区）

1. Cursor → Cloud Agents → 你的 **Environment**  
2. 在 **Repositories** 中加入 `PureSaber/agent-toolkit`（及其他需要的私有仓）  
3. **新建** Cloud Agent run（旧 run 工作区通常只有当时绑定的仓）

### 5. 验证 Agent 是否真能碰目标仓

在新 run 里让 Agent 执行：

```bash
test -d /workspace/../agent-toolkit && echo OK || ls /workspace
gh repo view PureSaber/agent-toolkit
```

（实际挂载路径以 Environment 为准；多仓时可能是并列目录而非 `/workspace` 唯一根。）

### 6. 当 `git clone` / `git push` 失败时的 API 写法

终端 `gh` 已能访问私有仓，但 Agent 环境 `git clone` 失败时，可用 **Contents API** 读/写（2026-08-07 更新 `agent-toolkit` 即用此路）：

**读目录：**

```bash
gh api repos/PureSaber/agent-toolkit/contents/cursor/skills/workflow/ --jq '.[].name'
```

**读单文件（解码 body）：**

```bash
gh api repos/PureSaber/agent-toolkit/contents/tasksolver/README.md \
  | python3 -c "import sys,json,base64; print(base64.b64decode(json.load(sys.stdin)['content']).decode())"
```

**更新文件（需文件当前 `sha`）：**

```bash
SHA=$(gh api repos/PureSaber/agent-toolkit/contents/tasksolver/README.md --jq .sha)
CONTENT=$(base64 -w0 /path/to/local/README.md)
gh api repos/PureSaber/agent-toolkit/contents/tasksolver/README.md \
  -X PUT \
  -f message="docs: example update via API" \
  -f content="$CONTENT" \
  -f sha="$SHA"
```

**新建文件：** 同上，但不传 `sha`。

**拉整仓快照（clone 失败时本地展开）：**

```bash
gh api repos/PureSaber/agent-toolkit/tarball/main -H "Accept: application/vnd.github+json" > /tmp/agent-toolkit.tar.gz
mkdir -p /tmp/agent-toolkit-work && tar -xzf /tmp/agent-toolkit.tar.gz -C /tmp/agent-toolkit-work
```

## 案例：agent-toolkit（2026-08-07）

**目标：** Cloud Agent 更新私有仓 `agent-toolkit` 里 TaskSolver 相关 Skills / README。

**过程摘要：**

1. 初始：仅绑定 `React_TaskSolver` → `agent-toolkit` 404  
2. 用户在 **Cursor 终端**执行 `gh auth login` 并 `gh auth switch -u PureSaber`  
3. `gh repo view` / `gh api` 成功；`git clone` 仍失败  
4. Agent 通过 `gh api` PUT 更新 `tasksolver/README.md`、`CATALOG.md`、skills 等  
5. 决策记录写在 agent-toolkit：`decisions/2026-08-07-tasksolver-v0.3-upstream-docs.md`（长文仍放 React_TaskSolver）

**本机后续（有 clone 权限时）：**

```bash
git clone git@github.com:PureSaber/agent-toolkit.git
cd agent-toolkit
./scripts/install-cursor-skills.sh   # 或 Windows 下 .ps1
```

## 常见失败与对策

| 现象 | 可能原因 | 对策 |
|------|----------|------|
| `gh repo view` 404 | 未登录个人账号 / 无仓权限 | `gh auth login` + `gh auth switch` |
| Agent 仍看不到私有仓 | 旧 Cloud run / Environment 未绑仓 | 新 run + Environment 加仓库 |
| `git clone` not found | Cloud git 凭据与 `gh` 不一致 | 用 `gh api` tarball 或 Contents API |
| push `quant-research-notes` 403 | Cloud 用 bot token，非你的 push 权 | 本机 `git push`，或 `gh api` PUT（PureSaber 账号） |
| `gh api` PUT 422 | 未带最新 `sha` | 先 GET 取 `sha` 再 PUT |

## 与 agent-toolkit 维护分工

| 内容类型 | 放哪里 |
|----------|--------|
| 运维/账号/GitHub 授权步骤（本文） | **quant-research-notes** |
| Agent Skills、Hook 模板、TaskSolver 行为约定 | **agent-toolkit** |
| TaskSolver 编排器、Goal、长文档 | **React_TaskSolver** |

agent-toolkit README 原则：知识正文在 ops-notes / quant-research-notes；toolkit 只存 **Agent 怎么行为**。

## 相关笔记

| 文档 | 说明 |
|------|------|
| [tasksolver-running-modes.md](tasksolver-running-modes.md) | TaskSolver 模拟 / Cloud / IDE 三种运行模式 |
| [repos.md](repos.md) | 量化 monorepo 仓库地图 |
| [React_TaskSolver docs/running-modes.md](https://github.com/PureSaber/React_TaskSolver/blob/master/docs/running-modes.md) | 上游运行模式全文 |
| [agent-toolkit decisions](https://github.com/PureSaber/agent-toolkit/blob/main/decisions/2026-08-07-tasksolver-v0.3-upstream-docs.md) | v0.3 文档分工决策 |

## 快速检查清单

```bash
# 1. 身份
gh auth status

# 2. 私有仓可读
gh repo view PureSaber/agent-toolkit

# 3. API 读写
gh api repos/PureSaber/agent-toolkit --jq .full_name

# 4. （可选）本机 clone
git clone git@github.com:PureSaber/agent-toolkit.git
```
