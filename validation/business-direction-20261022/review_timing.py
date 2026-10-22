"""Recompute the missing descriptive benchmark risk on the existing protocol."""
import hashlib
import json
import sys
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

repo = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(repo / 'src'))
from quant_timing.config import load_yaml, resolve_config
from quant_timing.inputs import load_market
from quant_timing.study import run_study

receipt = json.loads((repo / 'studies/market_comparison/2026-10-01-regression/receipt.json').read_text())
for name, expected in receipt['input_sha256'].items():
    data = (repo / name).read_text(encoding='utf-8-sig').replace('\r\n', '\n').replace('\r', '\n')
    assert hashlib.sha256(data.encode()).hexdigest() == expected, name
config = repo / 'configs/market_comparison.yaml'
raw = load_yaml(config)
raw['position'] = {'model': 'tsmom', **raw['models']['tsmom']}
raw['style'] = None
raw['overlay']['mode'] = 'cash'
prices, extras = load_market(raw, resolve_config(raw), config)
result = run_study(prices, raw, **extras)
prior = pd.read_csv(repo / 'studies/market_comparison/2026-10-01-regression/model_comparison.csv')
prior = prior[(prior.book == 'position_hs300') & (prior.model == 'tsmom')].iloc[0]
sample = result.realized.dropna(subset=['net_return'])
for metric in ('descriptive_full_sample_net', 'descriptive_full_sample_benchmark'):
    assert abs(result.summary[metric] - prior[metric]) < 1e-12, metric

def metrics(series):
    nav = (1 + series).cumprod()
    peaks = nav.cummax().clip(lower=1)
    return {'sessions': len(series), 'return': float(nav.iloc[-1] - 1),
            'drawdown': float((nav / peaks - 1).min()),
            'annualized_volatility': float(series.std(ddof=1) * np.sqrt(252)),
            'annualized_downside_deviation_zero_target': float(np.sqrt(np.mean(np.minimum(series, 0) ** 2) * 252)),
            'daily_historical_var_5pct': float(series.quantile(.05)),
            'daily_historical_cvar_5pct': float(series[series <= series.quantile(.05)].mean())}

output = Path(__file__).resolve().parent
output.mkdir(parents=True, exist_ok=True)
value = {'scope': 'Retrospective descriptive comparison, not a preregistered risk objective or promotion.',
         'source_commit': subprocess.check_output(['git', '-C', str(repo), 'rev-parse', 'HEAD'], text=True).strip(),
         'book': 'position_hs300', 'model': 'tsmom', 'start': str(sample.index[0]),
         'end': str(sample.index[-1]), 'inputs': receipt['input_sha256'],
         'original_return_metrics_reproduced': True, 'leakage': result.leakage,
         'strategy': metrics(sample.net_return), 'benchmark': metrics(sample.benchmark_return),
         'risk_objective_verdict': 'insufficient_evidence',
         'limitations': ['No preregistered risk-reduction threshold or power calibration.',
                        'No uncertainty interval for the paired risk difference.',
                        'Maximum drawdown is one observed path, not proof of risk reduction.']}
(output / 'timing-risk-review.json').write_text(json.dumps(value, indent=2), encoding='utf-8')
sample[['net_return', 'benchmark_return']].to_csv(output / 'timing-paired-returns.csv')
print(json.dumps({k: value[k] for k in ('strategy', 'benchmark', 'risk_objective_verdict')}))
