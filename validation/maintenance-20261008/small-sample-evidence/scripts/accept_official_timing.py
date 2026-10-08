"""Admit real documents only at actual capture; do not infer historical publication."""

import json
from pathlib import Path

from quant_data_kit.financial import SourceMaterialReferenceV2, build_evidence_timing_v2

root = Path(__file__).resolve().parent
receipts = json.loads(
    (root / "official-source-receipts.json").read_text(encoding="utf-8")
)
results = []
for record in receipts:
    if record["status"] != "downloaded":
        continue
    material = SourceMaterialReferenceV2(
        material_id=record["name"],
        kind="official_document",
        archive_version="temporary-acceptance-20261008-delete-after-verification",
        sha256=record["sha256"],
        locator=record["url"],
        review_citation="Retrieved original PDF; historical publication instant not authenticated",
        acquired_at=record["captured_at"],
    )
    built = build_evidence_timing_v2(
        effective_at=record["captured_at"],
        captured_at=record["captured_at"],
        raw_text="Historical publication instant unverified; URL date is not clock evidence",
        precision="unknown",
        revision_id=record["name"],
        source_materials=(material,),
    )
    timing = built.timing
    assert timing.availability.mode == "captured_only"
    for mode, trust in [
        ("natural_forward", "capture_receipt_only"),
        ("retrospective", "trust_source_declared_time"),
    ]:
        assert not timing.is_admitted(
            "2026-10-07T00:00:00Z", study_mode=mode, trust_model=trust
        )
        assert timing.is_admitted(
            record["captured_at"], study_mode=mode, trust_model=trust
        )
    results.append(
        {
            "name": record["name"],
            "mode": timing.availability.mode,
            "past_rejected": True,
            "capture_admitted": True,
            "timing": timing.to_dict(),
        }
    )
assert len(results) == 2
(root / "official-timing-acceptance.json").write_text(
    json.dumps(results, indent=2), encoding="utf-8"
)
print("2 official documents: historical admission rejected; actual capture admitted")
