"""Inject native typed faults through the real trial registry and findings reader."""
import json
from pathlib import Path

from quant_data_kit.failure_policy import HARD_STOPS, EvidenceFault
from quant_lab.research import execute_study
from quant_lab.findings import research_findings

root=Path(__file__).parent/'fault-propagation'
root.mkdir(exist_ok=True)
cases=[]
for kind in sorted(HARD_STOPS | {'held_suspended_price','held_price_unknown','entitlement_unresolved',
                               'candidate_price_missing','optimizer_search_failed','optimizer_infeasible_reported',
                               'optimizer_proven_infeasible','rules_unknown','rule_changed','unparsed','template_changed'}):
    recipe={'schema_version':'quant.research-recipe/v1','study_id':'injection-'+kind,'hypothesis':'software fault injection only',
            'mode':'exploratory','backend':'equity','inputs':{'bundle':'synthetic-unused'},
            'interval':{'start':'2024-01-01','end':'2024-06-01'},'factors':{'momentum_20d':1},
            'strategy':{'family':'rank','frequency':'weekly','top_n':1,'max_weight':.5,'cash_buffer':.5,'trend_window':60},
            'costs':{'initial_capital':100000,'commission':.0003,'min_commission':5,'stamp_tax':0,'slippage':.001,'participation_rate':.01},
            'diagnostics':{},'variants':[]}
    def fail(*args):
        raise EvidenceFault(kind,'synthetic fault injected at native executor boundary')
    destination=root/kind
    result=execute_study(recipe,destination,identity={'code':'synthetic-fault-injection'},data_identity={'fixture':kind},executor=fail)
    finding=research_findings(destination/'experiments.db')
    assessment=result['results'][0]['failure_assessment']
    persisted=finding['studies'][0]['attempts'][0]['payload']['failure_assessment']
    assert assessment==persisted and result['completed']==0
    assert not any(assessment[k] for k in ['publish_target','gate_a_credit','gate_b_credit','gate_c_credit'])
    cases.append({'kind':kind,'tier':assessment['tier'],'evidence_status':assessment['evidence_status'],
                  'registry_and_findings_preserved':True,'completed_attempts':0,'gate_credit':False})
(root/'receipt.json').write_text(json.dumps(cases,indent=2),encoding='utf-8')
print(json.dumps(cases))
