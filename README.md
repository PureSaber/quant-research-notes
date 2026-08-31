# Quant Research Notes

Knowledge base and roadmap for the PureSaber quant research monorepo (local workspace).

## Contents

| Doc | Description |
|-----|-------------|
| [roadmap.md](roadmap.md) | Learning path and project phases |
| [repos.md](repos.md) | Repository map and dependencies |
| [TECH_DEBT.md](TECH_DEBT.md) | Security / maintainability debt register |
| [pitfalls.md](pitfalls.md) | Common backtest / ML mistakes |
| [research-integrity-v1.md](research-integrity-v1.md) | PIT data, validation, run contract, risk and attribution standard |
| [cross-asset-multifrequency-v2-rfc.md](cross-asset-multifrequency-v2-rfc.md) | Cross-asset data, time and standard/v2 contract RFC |
| [validation/m7/](validation/m7/) | M7状态、验收规范、历史FAIL、修复PASS和PR合并就绪审计 |
| [validation/m8/](validation/m8/) | M8全栈软件发布、14仓不可变清单、tag、CI和独立验证证据 |
| [experiment-log/](experiment-log/) | Short summaries of important runs |

## Repo stack (2026-07)

```text
currency-converter        → Python CLI warmup
sklearn-stock-trend       → supervised learning + walk-forward
a-share-multifactor       → factor IC + quantile + retail backtest
quant-data-kit            → shared AKShare + Parquet + validation
quant-lab                 → cross-project experiment index
quant-report-hub          → unified charts (spread + equity adapters)
spread-backtest-viz       → legacy futures viz (frozen reference)
future_spread_analysis    → futures spread backtest engine
```

## Local workspace (Desktop)

Clone sibling repos under `C:\Users\ASUS\Desktop\quant_projects` and set:

```powershell
$env:QUANT_WORKSPACE_ROOT = "C:\Users\ASUS\Desktop\quant_projects"
```

Use `quant-workspace/configs/desktop.workspace.yaml` for path resolution. Stack health:

```powershell
cd quant-infra-workspace
powershell -File scripts/health-check.ps1
```

## Conventions

- Config: YAML under `configs/`
- Outputs: gitignored under `outputs/` or `output/`
- CLI: `pip install -e .` then project-specific commands
- Tests: `pytest -q` before push

