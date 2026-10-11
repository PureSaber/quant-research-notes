"""Coordinator-owned synthetic integration; expectations precede production calls."""
from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import sys
from decimal import Decimal
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--root', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
root, out = args.root.resolve(), args.output.resolve()
out.mkdir(parents=True, exist_ok=False)
sys.dont_write_bytecode = True
owners = {
    'quant-lab': 'a', 'quant-report-hub': 'a', 'quant-factors': 'a', 'quant-fund': 'a',
    'quant-strategy-adapters': 'b', 'quant-risk-monitor': 'b',
    'quant-data-kit': 'c', 'quant-execution': 'c', 'quant-portfolio': 'c',
    'quant-agent': 'd', 'quant-pipeline': 'd',
}
repos = {p: root / ('group-' + g) / p for p, g in owners.items()}
sys.path[:0] = [str(path / 'src') for path in repos.values()]

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def snapshot():
    return {f'{name}/{p.relative_to(repo).as_posix()}': digest(p)
            for name, repo in repos.items() for p in sorted((repo / 'src').rglob('*.py'))}

def load_example(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def save(name, value):
    (out / name).write_text(json.dumps(value, indent=2, allow_nan=False), encoding='utf-8')

before = snapshot()
expected = {'forecast_final_cash': '1017.60', 'continuous_old_pnl': '34',
            'continuous_new_pnl': '26', 'revision_pnl_delta': '-8',
            'missing_outcome_status': 'partial_observation', 'diamond_join_inputs': 2}
save('expected.json', expected)
report = {'schema': 'quant.coordinator-cross-group-review/v1', 'evidence_kind': 'synthetic',
          'expectations': expected, 'checks': {}, 'source_hashes': before}

from quant_measurement import compare_measurements, content_id, validate_observations
from quant_data_kit.artifacts import ArtifactStore, canonical_json
from quant_data_kit.derivatives.bundle import load_bundle
from quant_data_kit.revision_impact import RevisionRegistry
from quant_strategy_adapters.forecast import run_forecast_replay
from quant_portfolio.continuous_study import freeze_plan, run_study, paired_study
from quant_risk_monitor.model_diagnostics import diagnose_models

# The public producer fixture is reused; the scalar economics are computed independently.
fixture = load_example('forecast_fixture', repos['quant-strategy-adapters'] / 'examples/forecast_demo.py')
fixture.create_fixture(out / 'forecast')
forecast = run_forecast_replay(out / 'forecast/ml/frozen-demo', out / 'forecast/policy',
                               load_bundle(out / 'forecast/bundle'))
save('forecast-result.json', forecast)
expected_cash = Decimal(1000) + Decimal(2) * (Decimal('101.29') - Decimal('100.21')) * Decimal(10) - 4
assert Decimal(forecast['strategy']['final_account']['nav']) == expected_cash
assert len(forecast['strategy']['fills']) == 2
measurement = forecast['measurement']
validate_observations(measurement, forecast['observation_schedule'])
assert compare_measurements([measurement, forecast['economics']['baseline']['measurement']])['comparable']
bad = copy.deepcopy(measurement)
bad['basis']['cost_policy_id'] = content_id({'fee_per_contract': '2', 'slippage_ticks': 1})
assert not compare_measurements([measurement, bad])['comparable']
assert not compare_measurements([measurement, None])['comparable']
report['checks']['forecast_and_measurement'] = {'passed': True, 'actual_cash': str(expected_cash),
    'oracle': '1000 + 2 * (101.29 - 100.21) * 10 - 4; two modeled fills',
    'changed_cost_rejected': True, 'missing_measurement_rejected': True}

examples = repos['quant-portfolio'] / 'examples/continuous'
plan = freeze_plan(json.loads((examples / 'plan.json').read_bytes()))
markets = [json.loads((examples / name).read_bytes()) for name in ('market-old.json', 'market-new.json')]
studies = [run_study(plan, market) for market in markets]
for name, study, target in zip(('old', 'new'), studies, (Decimal(34), Decimal(26))):
    assert Decimal(study['net_pnl']) == target
    validate_observations(study['measurement'], study['observation_timestamps'])
    for key in ('cost', 'valuation'):
        assert content_id(study['measurement_configs'][key + '_policy']) == study['measurement']['basis'][key + '_policy_id']
    save('continuous-' + name + '.json', study)
assert not compare_measurements([study['measurement'] for study in studies])['comparable']
store = ArtifactStore(out / 'revision-store')
refs = [store.put_bytes(canonical_json(m), owner='coordinator') for m in markets]
pair = paired_study(store, plan, *refs, owner='coordinator')
assert Decimal(pair['economic_changes']['net_pnl'][0]['delta']) == -8
assert store.read_bytes(refs[0]) == canonical_json(markets[0])
save('revision-pair.json', pair)
report['checks']['continuous_revision_and_measurement'] = {'passed': True,
    'ordinary_comparison_rejected_changed_input': True, 'paired_delta': '-8',
    'old_input_preserved': True, 'oracle': '5*(110-101)-5-6=34; 4*(110-101)-4-6=26'}

registry = RevisionRegistry(store)
old, new = (store.put_bytes(value, owner='diamond') for value in (b'old', b'new'))
for trial in range(8):
    outputs = {name: store.put_bytes(json.dumps({'name': name, 'trial': trial}).encode(), owner='diamond')
               for name in ('left', 'mid', 'right', 'join')}
    for name, inputs in (('left', {'raw': old}), ('mid', {'raw': old}),
                         ('right', {'mid': outputs['mid']}),
                         ('join', {'left': outputs['left'], 'right': outputs['right']})):
        registry.register(output=outputs[name], inputs=inputs, stage=f'{trial}:{name}',
                          code_identity={'producer': 'b' * 40}, controls={}, owner='diamond')
    result = registry.impact(old, new)
    join = next(row for row in result['affected_objects'] if row['stage'] == f'{trial}:join')
    assert set(join['affected_dependencies']) == {outputs['left'].sha256, outputs['right'].sha256}
report['checks']['diamond_dependency_closure'] = {'passed': True, 'distinct_hash_orders': 8}

diagnostics = load_example('diagnostic_fixture', repos['quant-risk-monitor'] / 'examples/model_diagnostics_demo.py')
payload = diagnostics.fixture(changed=True)
full = diagnose_models(payload)
assert full['windows'][0]['findings']['forecast_error']['status'] == 'alert'
# Remove one unfavorable outcome, retain all other planned observations and timestamps.
payload['rows'][-1]['target'] = None
partial = diagnose_models(payload)
finding = partial['windows'][0]['findings']['forecast_error']
assert finding['status'] == 'partial_observation'
assert 'interval' not in finding and 'interval' not in finding['current']
save('partial-diagnostic.json', partial)
report['checks']['selective_missing_outcome'] = {'passed': True, 'before': 'alert',
    'after': finding['status'], 'no_full_window_confidence': True}

after = snapshot()
report['source_unchanged'] = before == after
report['passed'] = report['source_unchanged'] and all(c['passed'] for c in report['checks'].values())
save('report.json', report)
print(json.dumps({k: v for k, v in report.items() if k != 'source_hashes'}, indent=2))
raise SystemExit(0 if report['passed'] else 1)
