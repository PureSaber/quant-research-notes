"""Independent numerical transfer and semantic rejection controls."""
import argparse
import copy
import hashlib
import json
import sys
from decimal import Decimal
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--repo', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
repo = args.repo.resolve()
sys.dont_write_bytecode = True
sys.path.insert(0, str(repo / 'src'))
from quant_agent.assistant_assessment import load, public_packet, score
from quant_agent.assessment_baseline import respond

files = [repo / 'src/quant_agent' / name for name in
         ('assistant_assessment.py', 'assessment_baseline.py')]
before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
cases = load(repo / 'benchmarks/assistant-v1/public/cases.json')
labels = load(repo / 'benchmarks/assistant-v1/evaluator/labels.json')
public = public_packet(cases)
baseline = respond(public)
valid = score(public, labels, baseline)
assert valid['passed'] and not valid['online_model_called']

# Alter evidence and case identifier together; no corresponding evaluator label exists.
numeric = copy.deepcopy(public)
case = next(c for c in numeric['cases'] if c['case_id'] == 'net-return')
numeric['cases'] = [case]
case['case_id'] = 'reviewer-unseen-numbers'
ledger = next(e for e in case['evidence'] if e['type'] == 'ledger')['content']
ledger.update(starting_equity='200', gross_pnl='20', fees='25')
response = respond(numeric)['responses'][0]
values = {c['key']: c['value'] for c in response['claims']}
assert Decimal(values['net_pnl']) == -5
assert Decimal(values['net_return']) == Decimal('-0.025')

controls = {}
wrong = copy.deepcopy(baseline)
row = next(r for r in wrong['responses'] if r['case_id'] == 'net-return')
claim = next(c for c in row['claims'] if c['key'] == 'net_return')
claim['value'] = '12345'  # Keep the exact valid citations; arithmetic is false.
failed = score(public, labels, wrong)
assert not failed['passed']
controls['correct_citation_wrong_financial_claim_rejected'] = True
wrong = copy.deepcopy(baseline)
row = next(r for r in wrong['responses'] if r['case_id'] == 'failed-attempt-omission')
row['acknowledged_failures'] = []
assert not score(public, labels, wrong)['passed']
controls['omitted_failed_attempts_rejected'] = True
wrong = copy.deepcopy(baseline)
row = next(r for r in wrong['responses'] if r['case_id'] == 'conflicting-sources')
row['decision'] = 'report_only'
assert not score(public, labels, wrong)['passed']
controls['unresolved_conflict_without_abstention_rejected'] = True
assert all('claims' not in c and 'rationale' not in c for c in public['cases'])
result = {'schema': 'quant.independent-assessment-review/v1',
          'evidence_kind': 'synthetic', 'baseline_cases': valid['summary'],
          'new_numeric_case': {'case_id': case['case_id'], 'net_pnl': '-5', 'net_return': '-0.025'},
          'controls': controls, 'sources': before,
          'source_unchanged': before == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
          'online_model_quality': 'not_measured'}
result['passed'] = result['source_unchanged'] and all(controls.values())
args.output.parent.mkdir(parents=True, exist_ok=True)
with args.output.open('x', encoding='utf-8') as stream:
    json.dump(result, stream, indent=2)
print(json.dumps(result, indent=2))
raise SystemExit(0 if result['passed'] else 1)
