# Pitfalls

## Data

- **Survivorship bias**: use historical index constituents (`pit_fundamentals`, `use_historical_universe`).
- **Look-ahead**: fundamentals must be lagged; AKShare report dates ≠ availability dates.
- **Adjustments**: use qfq (forward adjusted) consistently.

## Machine learning

- **Random train/test split** on time series → use walk-forward or purged CV.
- **Overlapping labels** (N-day forward return) → use `purged` CV with embargo.
- **High in-sample accuracy** with zero OOS edge → check label threshold and class balance.

## Backtest

- **T+1**: A-share sells cannot settle same day; retail mode must enforce this.
- **Lot size**: 100-share lots; fractional shares inflate performance.
- **Limit up/down**: signals on limit-up days may not fill.
- **Additive vs compound returns**: futures spread framework uses additive NAV; do not mix formulas.

## Operations

- **AKShare rate limits**: reduce `max_workers`, increase `sleep_seconds`.
- **Lost experiment context**: run `quant-lab scan` after major backtests.
