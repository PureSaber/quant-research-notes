# Run output contract

Each research run directory should include enough metadata for `quant-lab`, `quant-agent`, and `quant-pipeline` to consume without repo-specific code paths.

## Required / recommended files

| File | Writer | Readers |
|------|--------|---------|
| `config.snapshot.yaml` | backtest engines | quant-agent, quant-lab |
| `run_meta.json` | backtest engines | quant-agent, quant-lab |
| `capital_curves.csv` | equity engines, paper-sim | quant-risk-monitor, quant-report-hub |
| `performance/summary.csv` | futures spread engine | quant-report-hub, quant-agent |
| `review_manifest.json` | quant-agent | quant-lab |
| `state/nav.csv`, `state/holdings.csv` | quant-paper-sim | quant-risk-monitor, quant-portfolio |

## Workspace resolution

All tools should resolve sibling repo paths via `quant-workspace` (`configs/default.workspace.yaml`) instead of hard-coded `../` paths in production configs.

## Post-run pipeline

Typical daily flow (`quant-pipeline/configs/daily_paper.yaml`):

1. `quant-regime detect` or `detect-multi`
2. `quant-paper step`
3. `quant-risk check`
4. `quant-lab scan`
5. `quant-lab export html`

Optional offline review: `quant-review run --offline`
