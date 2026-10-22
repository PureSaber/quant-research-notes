"""Reproducible partial historical rule imports; never bridge an unknown boundary."""
import copy
import hashlib
import json
import re
import shutil
from pathlib import Path

import pandas as pd
from quant_data_kit.instrument_master import import_instrument_master, resolve_instrument_catalog, load_instrument_master

ROOT = Path(__file__).parent
BASE = Path(r'C:\Users\51076\Documents\ChatGPT\SCRATCH\qetf-evidence\master-source-20261014-v2')
EVIDENCE = ROOT / 'history-evidence'
END = json.loads((BASE/'declaration.json').read_text(encoding='utf-8'))['captured_at']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def claim(value, locator, excerpt, derived=False):
    return dict(value=value, locator=locator, excerpt=excerpt, method='derived' if derived else 'direct')


def section(folder, start, end):
    text = re.sub(r'\s+', '', (EVIDENCE/folder/'text.txt').read_text(encoding='utf-8'))
    return text[text.index(start):text.index(end, text.index(start)+len(start))]


def build(label, begin, cutoff):
    root = ROOT / ('master-source-'+label)
    shutil.copytree(BASE, root)
    d = json.loads((root/'declaration.json').read_text(encoding='utf-8'))
    d['captured_at'] = json.loads((EVIDENCE/'listing-510500-2020-verified'/'receipt.json').read_text())['captured_at']
    for doc in d['documents']:
        if doc['validity_basis'] == 'observed-through-capture-refresh-required':
            doc['validity_basis'] = 'bounded-event'  # Retain the old observed horizon, not today's date.
    docs = {doc['document_id']:doc for doc in d['documents']}
    listing = docs['listing-510500']
    evidence = EVIDENCE/'listing-510500-2020-verified'
    receipt = json.loads((evidence/'receipt.json').read_text())
    shutil.copyfile(evidence/'source.pdf', root/listing['file'])
    listing.update(published_at='2020-10-19T00:00:00Z', available_at='2020-10-20T00:00:00Z',
                   source_uri=receipt['url'], sha256=receipt['sha256'], title='2020-10-19 fund product key information update')
    text = re.sub(r'\s+', '', (evidence/'text.txt').read_text(encoding='utf-8'))
    text = text[text.index('一、产品概况'):text.index('二、基金投资')]
    for field in listing['assertions'][0]['fields'].values():
        field.update(locator='page 1: product overview', excerpt=text)

    def document(folder, docid, venue, published, available, effective, until, symbols, kind='trading_rule'):
        p=EVIDENCE/folder
        receipt=json.loads((p/'receipt.json').read_text())
        source=next(x for x in p.glob('source.*') if x.suffix in {'.pdf','.docx','.html'})
        target=root/'documents'/(docid+source.suffix)
        shutil.copyfile(source,target)
        doc=dict(document_id=docid,kind=kind,publisher=venue,title=docid,source_uri=receipt['url'],
                 published_at=published,available_at=available,effective_from=effective,effective_to=until,
                 validity_basis='bounded-event',availability_basis='publication-date-conservative-next-day',
                 file=str(target.relative_to(root)).replace('\\','/'),sha256=sha(target),assertions=[])
        if kind=='trading_rule':
            lot_clause,tick_clause=('3.4.7','3.4.11') if venue=='SSE' else ('3.3.8','3.3.13')
            lot=section(folder,lot_clause,'3.4.8' if venue=='SSE' else '3.3.9')
            tick=section(folder,tick_clause,'3.4.12' if venue=='SSE' else '3.3.14')
            for symbol in symbols:
                fields={'venue':claim(venue,'document title',docid),
                        'lot_size':claim('100',lot_clause,lot), 'quantity_step':claim('1',lot_clause+' odd-lot sell provision',lot,True),
                        'price_tick':claim('0.001',tick_clause,tick), 'price_scale':claim('3',tick_clause,tick,True)}
                if venue=='SSE' and symbol!='588000':
                    fields['price_limit_rate']=claim('0.10','3.4.13',section(folder,'3.4.13','3.4.14'))
                doc['assertions'].append({'symbol':symbol,'fields':fields})
        else:
            excerpt=section(folder,'一、本所上市','二、本所')
            doc['assertions']=[{'symbol':'588000','fields':{'price_limit_rate':claim('0.20','paragraph 1(1): STAR-index ETFs',excerpt)}}]
        docs[docid]=doc
        return doc

    document('sse-2020','sse-rule-2020','SSE','2020-03-13T00:00:00Z','2020-03-14T00:00:00Z',
             '2020-03-14T00:00:00Z','2023-04-10T00:00:00Z',['510300','510500','588000'])
    document('sse-star-limit','sse-star-limit-2020','SSE','2020-08-21T00:00:00Z','2020-08-22T00:00:00Z',
             '2020-08-22T00:00:00Z','2023-04-10T00:00:00Z',['588000'],'price_limit')
    if label=='early':
        document('szse-2020','szse-rule-2020','SZSE','2020-03-13T00:00:00Z','2020-03-14T00:00:00Z',
                 '2020-03-14T00:00:00Z','2020-12-31T00:00:00Z',['159915'])
        intervals=[(begin,cutoff,'szse-rule-2020')]
    else:
        document('szse-2020-dec','szse-rule-2020-dec','SZSE','2020-12-31T00:00:00Z','2021-01-01T00:00:00Z',
                 '2021-01-01T00:00:00Z','2021-04-06T00:00:00Z',['159915'])
        document('szse-2021','szse-rule-2021','SZSE','2021-03-31T00:00:00Z','2021-04-01T00:00:00Z',
                 '2021-04-06T00:00:00Z','2023-04-10T00:00:00Z',['159915'])
        intervals=[(begin,'2021-04-06T00:00:00Z','szse-rule-2020-dec'),
                   ('2021-04-06T00:00:00Z','2023-04-10T00:00:00Z','szse-rule-2021')]
    old=pd.read_csv(root/'catalog.csv',dtype=str,keep_default_na=False)
    rows=[]
    for symbol in ['510300','510500','159915','588000']:
        template=old[old.symbol==symbol].iloc[0].to_dict()
        for left,right,szse in intervals:
            row=copy.deepcopy(template)
            trading=szse if symbol=='159915' else 'sse-rule-2020'
            limit='szse-limit-159915-2020' if symbol=='159915' else 'sse-star-limit-2020' if symbol=='588000' else trading
            row.update(catalog_source_version='claude-historical-partial-20261022',effective_from=left,effective_to=right,
                       trading_rule_evidence_id=trading,price_limit_evidence_id=limit,
                       available_at=max(docs[k]['available_at'] for k in [trading,limit,row['listing_evidence_id']]))
            rows.append(row)
    if label!='early':
        rows+=old.to_dict(orient='records')
    pd.DataFrame(rows).to_csv(root/'catalog.csv',index=False)
    d.update(documents=list(docs.values()),catalog_sha256=sha(root/'catalog.csv'))
    d['rights_note'] += ' New primary attachments and typed historical clauses added. Conservative partial coverage excludes 2020-12-31: publication time unavailable. Original current validity horizon remains 2026-10-14; no runtime/account changes.'
    d['coverage']['trading_rules']='historical partial coverage; date-only 2020-12-31 boundary remains blocked'
    (root/'declaration.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
    destination=ROOT/('master-bundle-'+label)
    manifest=import_instrument_master(root,destination)
    print(label,manifest['bundle_sha256'])
    _, catalog=load_instrument_master(destination)
    resolved=resolve_instrument_catalog(catalog,symbols=['510300','510500','159915','588000'],
                  start=pd.Timestamp('2020-11-16' if label=='early' else '2021-01-04'),
                  end=pd.Timestamp('2020-12-30' if label=='early' else '2026-10-13'))
    resolved.to_csv(ROOT/('master-verified-'+label+'.csv'),index=False)


if __name__=='__main__':
    build('early','2020-11-16T00:00:00Z','2020-12-31T00:00:00Z')
    build('later','2021-01-01T00:00:00Z',END)
