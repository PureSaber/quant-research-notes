# Run output contract

Each research run directory should include enough metadata for `quant-lab`, `quant-agent`, and `quant-pipeline` to consume without repo-specific code paths.

## Standard v1 contract

Every new backtest run must write an immutable `standard/` directory. Legacy files remain optional
compatibility outputs.

| File | Required content |
|------|------------------|
| `standard/run_manifest.json` | schema version, code/config/data versions, artifact hashes |
| `standard/returns.csv` | gross/net/benchmark returns and NAV by date/strategy |
| `standard/positions.csv` | dated position snapshots with quantity/value/weight/side |
| `standard/orders.csv` | timestamped order intent and simulated/executed status |
| `standard/costs.csv` | commission, slippage, impact, borrow and total cost |
| `standard/exposures.csv` | factor/sector/currency or other named exposures |
| `standard/metrics.json` | project-specific metrics |

Validate before downstream use:

```bash
quant-lab validate --run-dir <run-directory>
```

See [research-integrity-v1.md](research-integrity-v1.md) for timing, validation, risk and attribution rules.

## Legacy compatibility files

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

Research backtest post-run flow: `quant-pipeline/configs/research_integrity_postrun.yaml`.

## Standard v2 RFC

Cross-asset and multi-frequency data/time semantics, the versioned`standard/v2`layout,
strict validation and v1/v2 coexistence rules are frozen in
[cross-asset-multifrequency-v2-rfc.md](cross-asset-multifrequency-v2-rfc.md). Standard v1
remains immutable and supported.
