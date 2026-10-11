"""Hand-calculated maintenance margin and partial funding review."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--sources', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
sys.dont_write_bytecode = True
root = args.sources.resolve()
sys.path[:0] = [str(root / p / 'src') for p in ('quant-execution', 'quant-data-kit')]
from quant_data_kit import AssetClass, FixedPoint, InstrumentSpec, MarginMode
from quant_execution.continuous import SharedCapitalAccount

path = root / 'quant-execution/src/quant_execution/continuous.py'
source_hash = hashlib.sha256(path.read_bytes()).hexdigest()
contract = InstrumentSpec(
    instrument_id='REVIEW:F', asset_class=AssetClass.FUTURE, product_type='future',
    venue='TEST', native_symbol='F', base_currency=None, quote_currency='USD',
    settlement_currency='USD', price_tick=FixedPoint(1, 0),
    quantity_step=FixedPoint(1, 0), contract_multiplier=FixedPoint(1, 0),
    calendar_id='fixture', margin_mode=MarginMode.CROSS,
    effective_from=datetime(2025, 1, 1, tzinfo=timezone.utc),
    available_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
    metadata={'initial_margin_rate': '0.2', 'maintenance_margin_rate': '0.1'},
)
account = SharedCapitalAccount(
    specs=[contract], owners={contract.instrument_id: 'trend'},
    allocations={'trend': {'USD': '250'}, 'reserve': {'USD': '100'}},
    base_currency='USD', opened_at='2026-01-01T00:00:00Z',
)

def event(identity, sequence, kind, **fields):
    at = '2026-01-02T00:00:00Z'
    return {'event_id': identity, 'sequence': sequence, 'kind': kind,
            'at': at, 'available_at': at, **fields}

account.apply(event('open', 0, 'fill', sleeve='trend', instrument_id=contract.instrument_id,
                    quantity='10', price='100', fee='0', settles_at='2026-01-02T00:00:00Z'))
account.apply(event('mark90', 1, 'mark', instrument_id=contract.instrument_id, price='90'))
mid = account.report()
account.apply(event('mark82', 2, 'mark', instrument_id=contract.instrument_id, price='82'))
low = account.report()
transfer_error = None
try:
    account.apply(event('partial-cure', 3, 'transfer', source='reserve', target='trend',
                        currency='USD', amount='5'))
except (ValueError, TypeError) as exc:
    transfer_error = str(exc)
expected_mid_pnl = Decimal('10') * (Decimal('90') - Decimal('100'))
expected_low_pnl = Decimal('10') * (Decimal('82') - Decimal('100'))
result = {
    'schema': 'quant.independent-margin-review/v1', 'evidence_kind': 'synthetic',
    'source_sha256': source_hash,
    'source_unchanged': source_hash == hashlib.sha256(path.read_bytes()).hexdigest(),
    'mid_expected_pnl': str(expected_mid_pnl), 'mid_actual_pnl': mid['net_pnl'],
    'mid_actual_margin_call': mid['history'][-1]['margin_call'],
    'mid_expected_initial_free': str(Decimal('250') + expected_mid_pnl - Decimal('900') * Decimal('.2')),
    'mid_expected_maintenance_free': str(Decimal('250') + expected_mid_pnl - Decimal('900') * Decimal('.1')),
    'low_expected_pnl': str(expected_low_pnl), 'low_actual_pnl': low['net_pnl'],
    'low_actual_margin_call': low['history'][-1]['margin_call'],
    'partial_transfer_accepted': transfer_error is None, 'partial_transfer_error': transfer_error,
    'partial_transfer_changes_no_total_pnl': account.report()['net_pnl'] == low['net_pnl'],
}
result['passed'] = (result['source_unchanged']
    and Decimal(mid['net_pnl']) == expected_mid_pnl
    and Decimal(low['net_pnl']) == expected_low_pnl
    and not result['mid_actual_margin_call'] and result['low_actual_margin_call']
    and result['partial_transfer_accepted'] and result['partial_transfer_changes_no_total_pnl'])
args.output.parent.mkdir(parents=True, exist_ok=True)
with args.output.open('x', encoding='utf-8') as stream:
    json.dump(result, stream, indent=2)
print(json.dumps(result, indent=2))
sys.exit(0 if result['passed'] else 1)
