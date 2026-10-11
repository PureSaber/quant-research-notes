"""Independent replay-identity probe; all inputs are synthetic and local."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--sources', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
sys.dont_write_bytecode = True
sources = args.sources.resolve()
sys.path[:0] = [str(sources / name / 'src') for name in ('quant-execution', 'quant-data-kit')]
from quant_data_kit import AssetClass, FixedPoint, InstrumentSpec, MarginMode
from quant_execution.continuous import SharedCapitalAccount

source = sources / 'quant-execution/src/quant_execution/continuous.py'
before_hash = hashlib.sha256(source.read_bytes()).hexdigest()
spec = InstrumentSpec(
    instrument_id='REVIEW:ETF', asset_class=AssetClass.ETF,
    product_type='cash', venue='TEST', native_symbol='ETF', base_currency=None,
    quote_currency='USD', settlement_currency='USD', price_tick=FixedPoint(1, 2),
    quantity_step=FixedPoint(1, 0), contract_multiplier=FixedPoint(1, 0),
    calendar_id='synthetic', margin_mode=MarginMode.NONE,
    effective_from=datetime(2025, 1, 1, tzinfo=timezone.utc),
    available_at=datetime(2025, 1, 1, tzinfo=timezone.utc), metadata={},
)

def account(capital, contract=spec):
    return SharedCapitalAccount(
        specs=[contract], owners={contract.instrument_id: 'alpha'},
        allocations={'alpha': {'USD': capital}}, base_currency='USD',
        opened_at='2026-01-01T00:00:00Z',
    )

original = account('1000')
original.apply({
    'event_id': 'independent-buy', 'at': '2026-01-02T00:00:00Z', 'sequence': 0,
    'kind': 'fill', 'sleeve': 'alpha', 'instrument_id': spec.instrument_id,
    'quantity': '5', 'price': '10', 'fee': '0',
    'settles_at': '2026-01-02T00:00:00Z', 'available_at': '2026-01-02T00:00:00Z',
})
checkpoint = original.checkpoint()
same = account('1000')
same.restore(checkpoint)
changed = account('2000')
changed_before = changed.report()
error = None
try:
    changed.restore(checkpoint)
except (ValueError, TypeError) as exc:
    error = str(exc)
from dataclasses import replace
changed_spec = account('1000', replace(spec, price_tick=FixedPoint(5, 2)))
spec_before = changed_spec.report()
spec_error = None
try:
    changed_spec.restore(checkpoint)
except (ValueError, TypeError) as exc:
    spec_error = str(exc)
after_hash = hashlib.sha256(source.read_bytes()).hexdigest()
result = {
    'schema': 'quant.independent-checkpoint-review/v1', 'evidence_kind': 'synthetic',
    'source_sha256': before_hash, 'source_unchanged': before_hash == after_hash,
    'same_configuration_replays_identically': original.report() == same.report(),
    'changed_initial_capital_rejected': error is not None,
    'rejection_preserves_account': changed.report() == changed_before,
    'original_initial_nav': original.report()['initial_nav'],
    'changed_initial_nav': changed.report()['initial_nav'], 'error': error,
    'changed_specification_rejected': spec_error is not None,
    'specification_rejection_preserves_account': changed_spec.report() == spec_before,
    'specification_error': spec_error,
}
result['passed'] = all(result[k] for k in (
    'source_unchanged', 'same_configuration_replays_identically',
    'changed_initial_capital_rejected', 'rejection_preserves_account',
    'changed_specification_rejected', 'specification_rejection_preserves_account',
))
args.output.parent.mkdir(parents=True, exist_ok=True)
with args.output.open('x', encoding='utf-8') as output:
    json.dump(result, output, indent=2)
print(json.dumps(result, indent=2))
sys.exit(0 if result['passed'] else 1)
