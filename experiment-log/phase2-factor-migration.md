# Phase 2 — quant-factors migration experiment log

Date: 2026-08-07

## Scope

- Migrated `a-share-multifactor/factors.py` to delegate OHLCV factors to `quant_factors.compute_factors`.
- Added IC smoke pipeline (`configs/ic_smoke.yaml`, `ic_smoke.py`).

## Factor list (quant-factors)

- momentum_20d, reversal_5d, volatility_20d, turnover_20d
- Extended library includes momentum/reversal/volatility/liquidity/value families (≥12 registered).

## IC smoke (post-migration)

```powershell
cd D:\quant_projects\a-share-multifactor
pip install -e ../quant-factors
python -m a_share_multifactor.ic_smoke --config configs/ic_smoke.yaml
```

Outputs: `outputs/ic_smoke/ic_summary.csv`, `manifest.yaml`

## Repro commands

```powershell
cd D:\quant_projects\quant-factors && python -m pytest -q
cd D:\quant_projects\a-share-multifactor && python -m pytest tests/test_ic_smoke.py -q
cd D:\quant_projects\quant-pipeline && quant-pipe run --config configs/pipelines/factor_compute_postrun.yaml --dry-run
```

## Notes

- IC magnitudes on synthetic smoke data are for pipeline validation only, not research conclusions.
