"""Exercise the actual disclosure importer against one reviewed official report."""
import hashlib
import json
from pathlib import Path

import pandas as pd
from quant_data_kit.research_coverage import asof_history
from a_share_multifactor.disclosures import import_disclosures, load_research_history

root = Path(__file__).resolve().parent
official = root / "scratch" / "official"
receipts = json.loads((root / "official-source-receipts.json").read_text())
source = next(row for row in receipts if row["name"] == "sse-600519-2025H1")
text = (official / "sse.txt").read_text(encoding="utf-8")
facts = {"revenue": "89389354416.84", "net_profit": "45402962298.10", "total_assets": "292257789095.51"}
for value in facts.values():
    assert format(float(value), ",.2f") in text
config = {"schema": "a-share.disclosures/v1", "provider": "SSE reviewed annual-disclosure PDF",
    "license_note": "Public official disclosure inspected for local software acceptance; no raw redistribution",
    "documents": [{"document_id": "sse-report", "source_uri": source["url"],
        "file": "sse-600519-2025H1.pdf", "sha256": source["sha256"], "captured_at": source["captured_at"],
        "publication": {"precision": "unknown", "value": None, "evidence_document_id": None}}],
    "records": [{"record_id": field + "-v1", "symbol": "600519", "field": field,
        "value": value, "unit": "CNY", "effective_at": "2025-06-30T00:00:00+08:00",
        "document_id": "sse-report", "supersedes": None,
        "locator": "2025H1 report, major accounting data table, PDF page 5"} for field, value in facts.items()]}
path = official / "reviewed-input.json"
path.write_text(json.dumps(config, indent=2), encoding="utf-8")
output = root / "scratch" / "disclosure-snapshot"
manifest = import_disclosures(path, output)
_, frame = load_research_history(output)
at = pd.Timestamp(source["captured_at"])
for field in facts:
    assert asof_history(frame, as_of=at - pd.Timedelta(nanoseconds=1), domain="fundamentals", field=field).empty
    assert len(asof_history(frame, as_of=at, domain="fundamentals", field=field)) == 1
try:
    import_disclosures(path, root / "scratch" / "forbidden-historical", policy="source-declared")
except ValueError as exc:
    assert "publication evidence" in str(exc)
else:
    raise AssertionError("Unknown publication admitted historically")
material = output / "disclosure" / "sse-600519-2025H1.pdf"
original = material.read_bytes()
try:
    material.write_bytes(original + b"\nsynthetic corruption")
    try:
        load_research_history(output)
    except ValueError as exc:
        assert "hash mismatch" in str(exc)
    else:
        raise AssertionError("Corrupt original material accepted")
finally:
    material.write_bytes(original)
result = {"source_url": source["url"], "source_sha256": source["sha256"],
    "captured_at": source["captured_at"], "reviewed_fact_rows": len(frame),
    "default_capture_only": True, "one_nanosecond_before_capture_rejected": True,
    "at_capture_admitted": True, "unknown_historical_publication_rejected": True,
    "material_corruption_rejected": True, "full_historical_PIT_certified": False,
    "snapshot_manifest_sha256": hashlib.sha256((output / "manifest.json").read_bytes()).hexdigest()}
(root / "disclosure-source-acceptance.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result))
