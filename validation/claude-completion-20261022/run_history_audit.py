import hashlib
import json
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pandas as pd
from quant_data_kit.etf_events import normalize_etf_splits, adjust_etf_prices
from quant_data_kit.etf_history import audit_etf_history
from quant_data_kit.research_dataset import _validate_adjustments, _validate_actions
from a_share_multifactor.config import AppConfig
from a_share_multifactor.corporate_actions import action_events, split_share_rules
from a_share_multifactor.decision_workflow import write_watchlist_catalog
from a_share_multifactor.run_contract import _replay

ROOT=Path(__file__).parent
OLD=Path(r'F:\qbiz1022\etf-history')
symbols=['510300','510500','159915','588000']
raw=pd.concat([pd.read_parquet(OLD/'akshare_sina_etf'/s/'bars.parquet') for s in symbols],ignore_index=True)
other=pd.concat([pd.read_parquet((OLD/'akshare_eastmoney_etf' if s=='588000' else ROOT/'prices'/'akshare_tencent')/s/'bars.parquet') for s in symbols],ignore_index=True)
receipt=json.loads((ROOT/'history-evidence'/'split-plan'/'receipt.json').read_text())
declaration={'event_id':'510500-split-20220826-exact','symbol':'510500','announced_date':'2022-08-23',
             'record_date':'2022-08-26','ex_date':'2022-08-29','credit_at':'2022-08-26T16:00:00+08:00',
             'known_at':'2022-08-24T00:00:00+08:00','sellable_date':'2022-08-29','ratio':'1.14539',
             'fractional_rule':'ceil','source':receipt['url'],'file':'split-plan/source.pdf','sha256':receipt['sha256']}
split=normalize_etf_splits([declaration],evidence_root=ROOT/'history-evidence',captured_at=receipt['captured_at'])
cash=pd.concat([pd.read_parquet(ROOT/'cash-actions'/(s+'.parquet')) for s in symbols],ignore_index=True)
actions=pd.concat([cash,split],ignore_index=True).sort_values(['symbol','ex_date'])
actions.to_parquet(ROOT/'reviewed-actions.parquet',index=False)
adjusted=adjust_etf_prices(raw,actions)
adjusted.to_parquet(ROOT/'adjusted-reviewed.parquet',index=False)
calendar=pd.to_datetime(pd.read_csv(OLD/'validation'/'calendar.csv').iloc[:,0])
report=audit_etf_history(raw,other,calendar,actions,symbols=symbols,start='2020-11-16',end='2026-10-21',master_root=ROOT/'master-bundle-later')
report['native_action_validation']=_validate_actions(actions,raw)
report['native_adjustment_validation']=_validate_adjustments(raw,adjusted,actions)
report['cash_crossvendor']=[]
for s, group in cash.groupby('symbol'):
    sina=pd.read_csv(OLD/'validation'/(s+'-sina-dividends.csv'))
    sina['date']=pd.to_datetime(sina.iloc[:,0]); sina['cash']=sina.iloc[:,1].diff().fillna(sina.iloc[:,1])
    for row in group.itertuples():
        matched=sina[sina.date==row.ex_date]
        observed=float(matched.cash.iloc[0]) if len(matched)==1 else None
        passed=observed is not None and abs(observed-float(row.cash_per_share))<1e-8
        report['cash_crossvendor'].append({'symbol':s,'ex_date':str(row.ex_date.date()),
                  'native_cash_per_share':row.cash_per_share,'sina_increment':observed,'passed':passed})
        if not passed:
            report['blocking_issues'].append({'kind':'cash_crossvendor_conflict','symbol':s,'date':str(row.ex_date.date())})
report['split_declaration']=declaration
report['credit_time_basis']='issuer states end of record date; 16:00 China is a daily-replay convention, not an observed registry timestamp'
report['source_identities']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'reviewed-actions.parquet',ROOT/'adjusted-reviewed.parquet',OLD/'validation'/'calendar.csv']}
report['additional_blockers']=[
    '2021-02-08 issuer suspension is located, but the direct downloaded attachment is an HTML challenge; not admissible as a hash-verified PDF.',
    '2020-12-31 SZSE rule publication time is date-only; separate validated masters cover through 2020-12-30 and from 2021-01-04. The trading-day boundary remains uncovered.',
    'Current rule evidence is retained only through its original 2026-10-14 capture. 2026-10-14 through 2026-10-21 needs a complete current directory/attachment refresh.',
    'Calendar is a Sina redistribution; it has not been independently reconciled against every official annual holiday notice.',
]
report['admitted']=not report['blocking_issues'] and not report['additional_blockers']
report['new_retrospective_study']='not_started_data_admission_failed'
out=ROOT/'native-split-audit'; out.mkdir(exist_ok=True)
report['native_unit_replays']=[]
for quantity in [100,100000]:
    panel=raw[(raw.symbol=='510500') & raw.date.between('2022-08-24','2022-08-30')].copy()
    panel['composite_score']=1.
    cfg=AppConfig(); cfg=replace(cfg,quantiles=1,costs=replace(cfg.costs,initial_capital=10000000,retail_mode=False,
                     commission=0,min_commission=0,stamp_tax=0,slippage=0,max_position_weight=1,cash_buffer=0,max_holdings=1))
    case=out/str(quantity); case.mkdir(exist_ok=True)
    catalog=write_watchlist_catalog(case,{'watchlist':[{'symbol':'510500','venue':'SSE','asset_class':'etf'}]},'2022-08-01','2022-09-01')
    events=action_events(split,raw[raw.symbol=='510500'],adjusted[adjusted.symbol=='510500'],pd.Timestamp('2022-08-24'),pd.Timestamp('2022-08-30'))
    args=dict(catalog_path=catalog,corporate_actions=events,share_rules=split_share_rules(split,raw),
              target_schedule={pd.Timestamp('2022-08-24').date():{'510500':quantity}})
    result=_replay(panel,cfg,'split-source-audit-'+str(quantity),**args)
    final=result.ledger.snapshot()
    expected=int((Decimal(quantity)*Decimal('1.14539')).to_integral_value(rounding='ROUND_CEILING'))
    actual=int(final.positions['510500'].to_decimal())
    balanced=all(sum(p.amount.to_decimal() for p in t.postings)==0 for t in result.ledger.transactions)
    repeated=_replay(panel,cfg,'split-source-audit-'+str(quantity),**args).ledger.snapshot()==final
    assert actual==expected and balanced and repeated
    report['native_unit_replays'].append({'record_quantity':quantity,'post_split_quantity':actual,'expected_quantity':expected,
          'cash':str(final.cash_balances['CNY'].to_decimal()),'nav':str(final.nav.to_decimal()),'balanced':balanced,'repeatable':repeated})
(ROOT/'history-admission.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
print(json.dumps({'admitted':report['admitted'],'sessions':report['sessions'],'cash_events':len(cash),'cash_reconciled':all(r['passed'] for r in report['cash_crossvendor']),
                  'blocking_issues':len(report['blocking_issues']),'native_unit_replays':report['native_unit_replays']},ensure_ascii=False))
