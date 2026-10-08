"""Bounded retrieval of two public primary-source documents for evidence inspection."""
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import requests

root = Path(__file__).resolve().parent
target = root / "scratch" / "official"
target.mkdir(exist_ok=False)
sources = {
    "sse-600519-2025H1": "https://big5.sse.com.cn/site/cht/www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2025-08-13/600519_20250813_TU6Y.pdf",
    "fullgoal-000191-202606": "https://www.fullgoal.com.cn/wbs-file/fund_report/20260608/CN_50100000_000191_FA010030_20260001.pdf",
}
receipts = []
for name, url in sources.items():
    receipt = {"name": name, "url": url, "historical_availability_authenticated": False}
    try:
        data = bytearray()
        with requests.get(url, timeout=(10, 20), stream=True) as response:
            response.raise_for_status()
            for chunk in response.iter_content(65536):
                data.extend(chunk)
                if len(data) > 20_000_000:
                    raise ValueError("Document exceeds 20 MB acceptance limit")
        assert data.startswith(b"%PDF-"), "Source did not return PDF"
        (target / f"{name}.pdf").write_bytes(data)
        receipt.update(status="downloaded", bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    except Exception as exc:
        receipt.update(status="unavailable", error=str(exc))
    receipt["captured_at"] = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    receipts.append(receipt)
    print(json.dumps(receipt), flush=True)
(root / "official-source-receipts.json").write_text(json.dumps(receipts, indent=2), encoding="utf-8")
