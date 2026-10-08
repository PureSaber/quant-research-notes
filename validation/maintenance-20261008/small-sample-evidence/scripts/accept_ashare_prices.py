"""Separate, explicitly selected Tencent source after Eastmoney sample failure."""

import hashlib
import json
from pathlib import Path

import numpy as np
from quant_data_kit.providers.prices import fetch_daily_prices

root = Path(__file__).resolve().parent
result = {
    "provider": "akshare_tencent",
    "adjustment": "none",
    "automatic_fallback": False,
}
try:
    frame = fetch_daily_prices(
        ["000001", "600519"],
        "2026-09-01",
        "2026-09-30",
        provider="akshare_tencent",
        adjust="",
        max_retries=1,
        max_workers=1,
    )
    assert len(frame) and set(frame.symbol) == {"000001", "600519"}
    assert frame.provider.eq("akshare_tencent").all()
    assert not frame.duplicated(["symbol", "date"]).any()
    assert np.isfinite(frame[["open", "high", "low", "close", "volume"]]).all().all()
    path = root / "scratch" / "a-share" / "prices-tencent.csv"
    assert not path.exists()
    frame.to_csv(path, index=False)
    result.update(
        status="passed",
        rows=len(frame),
        counts=frame.groupby("symbol").size().to_dict(),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    )
except Exception as exc:
    result.update(status="failed", error=str(exc))
(root / "ashare-price-acceptance.json").write_text(
    json.dumps(result, indent=2), encoding="utf-8"
)
print(json.dumps(result))
