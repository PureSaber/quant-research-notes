"""Disposable public-data checks; emits only aggregate counts, hashes and outcomes."""

import hashlib
import json
import re
import sqlite3
from decimal import Decimal, localcontext
from pathlib import Path

import numpy as np
import pandas as pd
from quant_fund.data import import_observations, validate_nav

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "scratch" / "public-fund"
results = {
    "classification": "public_snapshot_not_historical_PIT",
    "funds": [],
    "checks": {},
}
database = DATA / "acceptance.sqlite"
assert not database.exists(), "Use a new acceptance database"
for code in ("000191", "003318"):
    path = DATA / f"{code}.csv"
    frame = pd.read_csv(path, dtype={"fund_id": str})
    checked = validate_nav(frame)
    assert frame.known_at.eq("2026-10-08").all()
    assert not frame.duplicated(["fund_id", "nav_date", "known_at"]).any()
    assert np.isfinite(frame[["unit_nav", "total_return_nav"]]).all().all()
    assert (frame[["unit_nav", "total_return_nav"]] > 0).all().all()
    dividends = pd.read_csv(DATA / f"{code}.dividends.raw.csv", dtype=str)
    cash = {}
    for _, row in dividends.iterrows():
        match = re.fullmatch(r"每10份派现金([0-9.]+)元", row["每10份分红"])
        assert match, "Unreviewed dividend syntax"
        cash[row["除息日"]] = (
            cash.get(row["除息日"], Decimal(0)) + Decimal(match[1]) / 10
        )
    # Independent shares-and-wealth calculation, not the provider's recurrence.
    with localcontext() as ctx:
        ctx.prec = 40
        shares = Decimal(1)
        first = Decimal(str(frame.iloc[0].unit_nav))
        errors = []
        for i, row in frame.iterrows():
            price = Decimal(str(row.unit_nav))
            if i:
                shares += shares * cash.get(row.nav_date, Decimal(0)) / price
            wealth = shares * price / first
            errors.append(abs(float(wealth) - row.total_return_nav))
    assert max(errors) < 1e-10
    imported = import_observations(path, database)
    assert imported["inserted"] == len(frame)
    assert import_observations(path, database)["inserted"] == 0
    results["funds"].append(
        {
            "code": code,
            "rows": len(frame),
            "start": frame.nav_date.min(),
            "end": frame.nav_date.max(),
            "known_at": "2026-10-08",
            "dividend_events": len(dividends),
            "max_independent_wealth_error": max(errors),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    )
with sqlite3.connect(database) as connection:
    before = connection.execute(
        "SELECT * FROM nav ORDER BY fund_id, nav_date, known_at"
    ).fetchall()
    exported = pd.read_sql_query(
        "SELECT * FROM nav ORDER BY fund_id, nav_date, known_at", connection
    )
assert len(before) == sum(x["rows"] for x in results["funds"])
# New valid row followed by conflicting old version must roll back the entire import.
new = frame.iloc[[0]].copy()
new["fund_id"] = "SYNTHETIC_FAULT"
conflict = frame.iloc[[0]].copy()
conflict["unit_nav"] += 1
fault = DATA / "synthetic-conflict.csv"
pd.concat([new, conflict]).to_csv(fault, index=False)
try:
    import_observations(fault, database)
except ValueError as exc:
    assert "冲突" in str(exc)
else:
    raise AssertionError("Conflicting version accepted")
with sqlite3.connect(database) as connection:
    after = connection.execute(
        "SELECT * FROM nav ORDER BY fund_id, nav_date, known_at"
    ).fetchall()
assert before == after
rejected = []
for name, column, value in [
    ("nan", "unit_nav", np.nan),
    ("negative", "unit_nav", -1),
    ("infinity", "total_return_nav", np.inf),
    ("empty_source", "source", ""),
    ("known_before_nav", "known_at", "2000-01-01"),
]:
    bad = frame.iloc[[0]].copy()
    bad[column] = value
    try:
        validate_nav(bad)
    except ValueError:
        rejected.append(name)
    else:
        raise AssertionError(f"Invalid snapshot accepted: {name}")
expected = (
    pd.concat(
        [
            pd.read_csv(DATA / f"{c}.csv", dtype={"fund_id": str})
            for c in ("000191", "003318")
        ]
    )
    .sort_values(["fund_id", "nav_date", "known_at"])
    .reset_index(drop=True)
)
pd.testing.assert_frame_equal(expected, exported, check_exact=True)
results["checks"] = {
    "independent_total_return": "passed",
    "idempotent_import": "passed",
    "mixed_import_atomic_rollback": "passed",
    "export_equals_input": "passed",
    "invalid_cases_rejected": rejected,
    "database_rows": len(before),
    "historical_PIT_certified": False,
    "real_transactions_certified": False,
}
results["downloaded_files"] = [
    {
        "name": p.name,
        "bytes": p.stat().st_size,
        "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
    }
    for p in sorted(DATA.glob("*.csv"))
]
(ROOT / "fund-acceptance.json").write_text(
    json.dumps(results, indent=2), encoding="utf-8"
)
print(json.dumps(results["checks"]))
