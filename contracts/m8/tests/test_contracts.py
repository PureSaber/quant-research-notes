from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import ValidationError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import validate_contracts as contracts

ZERO = "0" * 64
ONE = "1" * 64


def verified_curated_input() -> dict:
    return {
        "schema_id": "puresaber.verified-factor-input@1.0.0",
        "layer": "curated",
        "source_snapshot_id": f"sha256-{ZERO}",
        "source_logical_sha256": ZERO,
        "selection_logical_sha256": ZERO,
        "event_schemas": [
            {"schema_id": "puresaber.bar-event", "schema_version": "2.0.0"}
        ],
        "calendar_id": "crypto-24x7-v1",
        "session_policy_version": "v1",
        "market_context_snapshot_id": f"sha256-{ONE}",
        "market_context_logical_sha256": ONE,
        "lineage": [
            {"role": "market", "snapshot_id": f"sha256-{ZERO}", "logical_sha256": ZERO}
        ],
        "rows": 1,
        "arrow_schema_sha256": ZERO,
        "aggregation": {
            "calendar_id": "crypto-24x7-v1",
            "session_policy_version": "v1",
            "kind": "fixed_time_bar",
            "recipe_version": "r1",
            "interval_ns": 60_000_000_000,
            "session_rollup": None,
            "event_bar_basis": None,
            "event_bar_threshold": None,
            "market_context_snapshot_id": f"sha256-{ONE}",
            "market_context_logical_sha256": ONE,
            "source_event_schemas": [
                {"schema_id": "puresaber.trade-event", "schema_version": "2.0.0"}
            ],
            "partition_evidence": None,
        },
    }


class ContractTests(unittest.TestCase):
    def manifest(self) -> dict:
        return contracts.load_contract_json(
            ROOT / "golden" / "factor-frame-manifest-v1.json"
        )

    def test_positive_suite_and_verified_input(self) -> None:
        contracts.validate_contract_suite(ROOT)
        contracts.validate_verified_factor_input(ROOT, verified_curated_input())

    def test_input_layer_schema_and_context_mismatches_fail(self) -> None:
        bad_schema = verified_curated_input()
        bad_schema["event_schemas"] = [
            {"schema_id": "puresaber.trade-event", "schema_version": "2.0.0"}
        ]
        with self.assertRaises(ValidationError):
            contracts.validate_verified_factor_input(ROOT, bad_schema)

        bad_context = verified_curated_input()
        bad_context["aggregation"]["market_context_snapshot_id"] = f"sha256-{ZERO}"
        with self.assertRaisesRegex(
            contracts.ContractViolation, "INPUT_CONTEXT_ID_MISMATCH"
        ):
            contracts.validate_verified_factor_input(ROOT, bad_context)

        normalized_bar = verified_curated_input()
        normalized_bar["layer"] = "normalized"
        normalized_bar["aggregation"] = None
        with self.assertRaises(ValidationError):
            contracts.validate_verified_factor_input(ROOT, normalized_bar)

    def test_pit_scope_range_and_uniqueness_fail(self) -> None:
        fixed_certified = self.manifest()
        fixed_certified["as_of"] = {"mode": "fixed", "fixed_at_ns": "0"}
        with self.assertRaises(ValidationError):
            contracts.validate_factor_frame_manifest(ROOT, fixed_certified)

        out_of_range = self.manifest()
        out_of_range["as_of"] = {"mode": "fixed", "fixed_at_ns": str(2**100)}
        out_of_range["certification_scope"] = "research-restated"
        with self.assertRaisesRegex(contracts.ContractViolation, "AS_OF_OUT_OF_RANGE"):
            contracts.validate_factor_frame_manifest(ROOT, out_of_range)

        duplicate_factor = self.manifest()
        duplicate_factor["factor_specs"].append(
            copy.deepcopy(duplicate_factor["factor_specs"][0])
        )
        with self.assertRaisesRegex(contracts.ContractViolation, "DUPLICATE_FACTOR"):
            contracts.validate_factor_frame_manifest(ROOT, duplicate_factor)

        duplicate_lineage = self.manifest()
        duplicate_lineage["source_lineage"].append(
            copy.deepcopy(duplicate_lineage["source_lineage"][0])
        )
        with self.assertRaisesRegex(
            contracts.ContractViolation, "DUPLICATE_SOURCE_LINEAGE"
        ):
            contracts.validate_factor_frame_manifest(ROOT, duplicate_lineage)

        duplicate_output = self.manifest()
        duplicate_output["output_schema"].append(
            copy.deepcopy(duplicate_output["output_schema"][0])
        )
        with self.assertRaisesRegex(
            contracts.ContractViolation, "DUPLICATE_OUTPUT_COLUMN"
        ):
            contracts.validate_factor_frame_manifest(ROOT, duplicate_output)

    def test_duplicate_json_mapping_key_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "duplicate.json"
            path.write_text(
                '{"pe_ratio":"first","pe_ratio":"second"}', encoding="utf-8"
            )
            with self.assertRaisesRegex(
                contracts.ContractViolation, "JSON_DUPLICATE_KEY"
            ):
                contracts.load_contract_json(path)

    def test_invalid_typed_cells_fail(self) -> None:
        invalid = [
            ({"t": "f64", "v": "7ff0000000000000"}, "CELL_NON_FINITE_FLOAT"),
            ({"t": "f64", "v": "7ff8000000000000"}, "CELL_NON_FINITE_FLOAT"),
            ({"t": "f64", "v": "8000000000000000"}, "CELL_NEGATIVE_ZERO"),
            ({"t": "u8", "v": "-1"}, "CELL_U8_OUT_OF_RANGE"),
            ({"t": "i8", "v": "128"}, "CELL_I8_OUT_OF_RANGE"),
            ({"t": "fixed", "u": str(2**63), "s": "0"}, "CELL_FIXED_OUT_OF_RANGE"),
            ({"t": "ts_ns", "v": str(2**63)}, "CELL_TIMESTAMP_OUT_OF_RANGE"),
            ({"t": "binary", "v": "A"}, "CELL_INVALID_BASE64URL"),
            ({"t": "date", "v": "2026-02-31"}, "CELL_INVALID_DATE"),
            (
                {"t": "struct", "v": [["x", {"t": "null"}], ["x", {"t": "null"}]]},
                "CELL_DUPLICATE_STRUCT_FIELD",
            ),
        ]
        for cell, code in invalid:
            with (
                self.subTest(code=code),
                self.assertRaisesRegex(contracts.ContractViolation, code),
            ):
                contracts.validate_typed_cell(cell)

    def test_golden_manifest_and_hash_are_cross_bound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / "m8"
            shutil.copytree(ROOT, copied)
            manifest_path = copied / "golden" / "factor-frame-manifest-v1.json"
            manifest = contracts.load_contract_json(manifest_path)
            manifest["factor_specs"][0]["factor_id"] = "different_1p"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(
                contracts.ContractViolation,
                "OUTPUT_FACTOR_MISSING|PROJECTION_HASH_MISMATCH",
            ):
                contracts.validate_golden_bundle(
                    copied, copied / "golden" / "factor-frame-hash-v1.json"
                )


if __name__ == "__main__":
    unittest.main()
