"""Small real-source A-share PIT gate acceptance; no historical timestamp invention."""

import hashlib
import json
from pathlib import Path

from a_share_multifactor.data_loader import merge_price_fundamentals
from quant_data_kit.providers.fundamentals import fetch_fundamentals
from quant_data_kit.providers.prices import fetch_daily_prices

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "scratch" / "a-share"
DATA.mkdir(exist_ok=False)
result = {
    "symbols": ["000001", "600519"],
    "start": "2026-09-01",
    "end": "2026-09-30",
    "historical_PIT_certified": False,
}
for name, fetch, kwargs in [
    ("fundamentals", fetch_fundamentals, {}),
    ("prices", fetch_daily_prices, {"provider": "akshare_eastmoney", "adjust": ""}),
]:
    try:
        table = fetch(
            result["symbols"],
            result["start"],
            result["end"],
            max_workers=1,
            max_retries=1,
            **kwargs,
        )
        assert len(table), "Empty real sample"
        assert not table.duplicated(["symbol", "date"]).any()
        assert set(table.symbol) == set(result["symbols"])
        path = DATA / f"{name}.csv"
        table.to_csv(path, index=False)
        result[name] = {
            "rows": len(table),
            "counts": table.groupby("symbol").size().to_dict(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        if name == "fundamentals":
            assert table.available_at.isna().all()
            assert table.availability_basis.eq("unknown").all()
            result[name]["unknown_availability_rows"] = int(
                table.available_at.isna().sum()
            )
            # Bare observation keys suffice to exercise the actual consumer PIT gate.
            try:
                merge_price_fundamentals(table[["symbol", "date"]], table)
            except ValueError as exc:
                assert "unknown availability" in str(exc)
                result["pit_gate"] = {
                    "status": "correctly_rejected",
                    "reason": str(exc),
                }
            else:
                raise AssertionError("Unknown publication time accepted as PIT")
    except Exception as exc:
        result[name] = {"status": "failed", "error": str(exc)}
(ROOT / "ashare-acceptance.json").write_text(
    json.dumps(result, indent=2), encoding="utf-8"
)
print(json.dumps(result))
