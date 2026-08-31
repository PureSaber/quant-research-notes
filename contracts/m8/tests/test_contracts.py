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
        "rows": "1",
        "arrow_schema_sha256": ZERO,
        "aggregation": {
            "calendar_id": "crypto-24x7-v1",
            "session_policy_version": "v1",
            "kind": "fixed_time_bar",
            "recipe_version": "r1",
            "interval_ns": "60000000000",
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

    def assert_golden_failure(
        self, code: str, *, golden_mutator=None, manifest_mutator=None
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            copied = Path(temporary) / "m8"
            shutil.copytree(ROOT, copied)
            golden_path = copied / "golden" / "factor-frame-hash-v1.json"
            manifest_path = copied / "golden" / "factor-frame-manifest-v1.json"
            golden = contracts.load_contract_json(golden_path)
            manifest = contracts.load_contract_json(manifest_path)
            if golden_mutator is not None:
                golden_mutator(golden)
            if manifest_mutator is not None:
                manifest_mutator(manifest)
            golden_path.write_text(json.dumps(golden), encoding="utf-8")
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(contracts.ContractViolation, code):
                contracts.validate_golden_bundle(copied, golden_path)

    def test_positive_suite_and_verified_input(self) -> None:
        contracts.validate_contract_suite(ROOT)
        contracts.validate_verified_factor_input(ROOT, verified_curated_input())
        normalized = verified_curated_input()
        normalized.update(
            {
                "layer": "normalized",
                "event_schemas": [
                    {
                        "schema_id": "puresaber.trade-event",
                        "schema_version": "2.0.0",
                    }
                ],
                "aggregation": None,
            }
        )
        contracts.validate_verified_factor_input(ROOT, normalized)

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

    def test_frequency_profiles_and_source_order_fail_closed(self) -> None:
        event_bar_manifest = self.manifest()
        event_bar_manifest["frequency"].update(
            {
                "kind": "event_bar",
                "interval_ns": None,
                "event_bar_basis": "trade_count",
                "event_bar_threshold": {"units": "100", "scale": 0},
            }
        )
        contracts.validate_factor_frame_manifest(ROOT, event_bar_manifest)

        event_manifest = self.manifest()
        event_manifest["frequency"].update(
            {
                "kind": "market_event",
                "interval_ns": None,
                "market_event_types": ["puresaber.trade-event"],
            }
        )
        event_manifest["input_event_schemas"] = [
            {"schema_id": "puresaber.trade-event", "schema_version": "2.0.0"}
        ]
        event_manifest["factor_specs"][0]["input_profile"] = "market_event"
        contracts.validate_factor_frame_manifest(ROOT, event_manifest)

        bar_factor = copy.deepcopy(event_manifest)
        bar_factor["factor_specs"][0]["input_profile"] = "bar"
        with self.assertRaisesRegex(
            contracts.ContractViolation, "MARKET_EVENT_REQUIRES_EVENT_FACTORS"
        ):
            contracts.validate_factor_frame_manifest(ROOT, bar_factor)

        unsorted_frequency = copy.deepcopy(event_manifest)
        unsorted_frequency["frequency"]["market_event_types"] = [
            "puresaber.trade-event",
            "puresaber.quote-event",
        ]
        with self.assertRaisesRegex(
            contracts.ContractViolation, "FREQUENCY_EVENT_TYPES_NOT_SORTED"
        ):
            contracts.validate_factor_frame_manifest(ROOT, unsorted_frequency)

        unsorted_schemas = copy.deepcopy(event_manifest)
        unsorted_schemas["frequency"]["market_event_types"] = [
            "puresaber.quote-event",
            "puresaber.trade-event",
        ]
        unsorted_schemas["input_event_schemas"] = [
            {"schema_id": "puresaber.trade-event", "schema_version": "2.0.0"},
            {"schema_id": "puresaber.quote-event", "schema_version": "2.0.0"},
        ]
        with self.assertRaisesRegex(
            contracts.ContractViolation, "INPUT_EVENT_SCHEMAS_NOT_SORTED"
        ):
            contracts.validate_factor_frame_manifest(ROOT, unsorted_schemas)

        unsorted_lineage = self.manifest()
        unsorted_lineage["source_lineage"].append(
            {
                "role": "auxiliary",
                "snapshot_id": f"sha256-{ONE}",
                "logical_sha256": ONE,
                "selection_sha256": ONE,
            }
        )
        with self.assertRaisesRegex(
            contracts.ContractViolation, "SOURCE_LINEAGE_NOT_SORTED"
        ):
            contracts.validate_factor_frame_manifest(ROOT, unsorted_lineage)

        wrong_bar_profile = self.manifest()
        wrong_bar_profile["factor_specs"][0]["input_profile"] = "market_event"
        with self.assertRaisesRegex(
            contracts.ContractViolation, "BAR_FREQUENCY_REQUIRES_BAR_FACTORS"
        ):
            contracts.validate_factor_frame_manifest(ROOT, wrong_bar_profile)

        wrong_bar_schema = self.manifest()
        wrong_bar_schema["input_event_schemas"] = [
            {"schema_id": "puresaber.trade-event", "schema_version": "2.0.0"}
        ]
        with self.assertRaisesRegex(
            contracts.ContractViolation, "BAR_INPUT_SCHEMA_MISMATCH"
        ):
            contracts.validate_factor_frame_manifest(ROOT, wrong_bar_schema)

        missing_dependency_lineage = self.manifest()
        missing_dependency_lineage["factor_specs"][0]["dependencies"][0]["role"] = (
            "missing"
        )
        with self.assertRaisesRegex(
            contracts.ContractViolation, "FACTOR_DEPENDENCY_LINEAGE_MISSING"
        ):
            contracts.validate_factor_frame_manifest(ROOT, missing_dependency_lineage)

    def test_event_bar_partition_evidence_fail_closed(self) -> None:
        value = verified_curated_input()
        value["aggregation"].update(
            {
                "kind": "event_bar",
                "interval_ns": None,
                "event_bar_basis": "trade_count",
                "event_bar_threshold": {"units": "3", "scale": 0},
                "partition_evidence": [
                    {
                        "relative_path": "part-000.parquet",
                        "source": "binance",
                        "instrument_id": "BTC-USDT",
                        "session_id": "binance-24x7-BTC-USDT-SPOT",
                        "first_sequence": "10",
                        "last_sequence": "12",
                        "first_event_id": "event-10",
                        "last_event_id": "event-12",
                        "event_count": "3",
                        "source_selection_sha256": ZERO,
                    }
                ],
            }
        )
        contracts.validate_verified_factor_input(ROOT, value)

        duplicate = copy.deepcopy(value)
        duplicate["aggregation"]["partition_evidence"].append(
            copy.deepcopy(duplicate["aggregation"]["partition_evidence"][0])
        )
        with self.assertRaisesRegex(
            contracts.ContractViolation, "EVENT_BAR_DUPLICATE_PARTITION"
        ):
            contracts.validate_verified_factor_input(ROOT, duplicate)

        duplicate_selection = copy.deepcopy(value)
        duplicate_selection["aggregation"]["partition_evidence"].append(
            copy.deepcopy(duplicate_selection["aggregation"]["partition_evidence"][0])
        )
        duplicate_selection["aggregation"]["partition_evidence"][1]["relative_path"] = (
            "part-001.parquet"
        )
        with self.assertRaisesRegex(
            contracts.ContractViolation, "EVENT_BAR_DUPLICATE_SELECTION"
        ):
            contracts.validate_verified_factor_input(ROOT, duplicate_selection)

        reversed_range = copy.deepcopy(value)
        reversed_range["aggregation"]["partition_evidence"][0].update(
            {"first_sequence": "12", "last_sequence": "10", "event_count": "1"}
        )
        with self.assertRaisesRegex(
            contracts.ContractViolation, "EVENT_BAR_REVERSED_SEQUENCE_RANGE"
        ):
            contracts.validate_verified_factor_input(ROOT, reversed_range)

        excessive_count = copy.deepcopy(value)
        excessive_count["aggregation"]["partition_evidence"][0]["event_count"] = "4"
        with self.assertRaisesRegex(
            contracts.ContractViolation, "EVENT_BAR_COUNT_EXCEEDS_SEQUENCE_RANGE"
        ):
            contracts.validate_verified_factor_input(ROOT, excessive_count)

        overlapping = copy.deepcopy(value)
        second = copy.deepcopy(overlapping["aggregation"]["partition_evidence"][0])
        second.update(
            {
                "relative_path": "part-001.parquet",
                "first_sequence": "12",
                "last_sequence": "14",
                "first_event_id": "event-12",
                "last_event_id": "event-14",
                "source_selection_sha256": ONE,
            }
        )
        overlapping["aggregation"]["partition_evidence"].append(second)
        with self.assertRaisesRegex(
            contracts.ContractViolation, "EVENT_BAR_OVERLAPPING_SEQUENCE_RANGE"
        ):
            contracts.validate_verified_factor_input(ROOT, overlapping)

        adjacent = copy.deepcopy(overlapping)
        adjacent["aggregation"]["partition_evidence"][1].update(
            {
                "first_sequence": "13",
                "first_event_id": "event-13",
                "event_count": "2",
            }
        )
        contracts.validate_verified_factor_input(ROOT, adjacent)

    def test_auxiliary_sources_require_lineage_and_factor_binding(self) -> None:
        manifest = self.manifest()
        manifest["source_lineage"].insert(
            0,
            {
                "role": "fundamentals",
                "snapshot_id": f"sha256-{ONE}",
                "logical_sha256": ONE,
                "selection_sha256": ONE,
            },
        )
        manifest["auxiliary_sources"] = [
            {
                "role": "fundamentals",
                "schema_id": "puresaber.fundamental-event",
                "schema_version": "1.0.0",
                "snapshot_id": f"sha256-{ONE}",
                "physical_sha256": ONE,
                "logical_sha256": ONE,
                "business_key_columns": ["instrument_id"],
                "observation_time_column": "observation_time",
                "effective_from_column": "effective_from",
                "effective_to_column": "effective_to",
                "available_at_column": "available_at",
                "superseded_at_column": "superseded_at",
                "revision_column": "revision",
                "value_availability": {"pe_ratio": "pe_available_at"},
                "join_recipe": "pit-effective-revision-v1",
            }
        ]
        manifest["factor_specs"][0]["dependencies"].insert(
            0,
            {
                "role": "fundamentals",
                "value_column": "pe_ratio",
                "availability_column": "pe_available_at",
            },
        )
        contracts.validate_factor_frame_manifest(ROOT, manifest)

        missing_lineage = copy.deepcopy(manifest)
        missing_lineage["source_lineage"].pop(0)
        with self.assertRaisesRegex(
            contracts.ContractViolation, "AUXILIARY_LINEAGE_MISSING"
        ):
            contracts.validate_factor_frame_manifest(ROOT, missing_lineage)

        missing_dependency = copy.deepcopy(manifest)
        missing_dependency["factor_specs"][0]["dependencies"].pop(0)
        with self.assertRaisesRegex(
            contracts.ContractViolation, "AUXILIARY_FACTOR_DEPENDENCY_MISSING"
        ):
            contracts.validate_factor_frame_manifest(ROOT, missing_dependency)

        wrong_mapping = copy.deepcopy(manifest)
        wrong_mapping["factor_specs"][0]["dependencies"][0]["availability_column"] = (
            "wrong_available_at"
        )
        with self.assertRaisesRegex(
            contracts.ContractViolation, "FACTOR_AUXILIARY_MAPPING_MISMATCH"
        ):
            contracts.validate_factor_frame_manifest(ROOT, wrong_mapping)

        unicode_column = copy.deepcopy(manifest)
        unicode_column["auxiliary_sources"][0]["value_availability"] = {
            "估值": "pe_available_at"
        }
        with self.assertRaises(ValidationError):
            contracts.validate_factor_frame_manifest(ROOT, unicode_column)

    def test_output_schema_and_record_semantics_are_frozen(self) -> None:
        wrong_identity = self.manifest()
        wrong_identity["output_schema"][2]["arrow_type"] = "utf8"
        with self.assertRaisesRegex(
            contracts.ContractViolation, "OUTPUT_IDENTITY_SCHEMA_MISMATCH"
        ):
            contracts.validate_factor_frame_manifest(ROOT, wrong_identity)

        wrong_factor = self.manifest()
        wrong_factor["output_schema"][5]["arrow_type"] = "int64"
        with self.assertRaisesRegex(
            contracts.ContractViolation, "OUTPUT_FACTOR_SCHEMA_MISMATCH"
        ):
            contracts.validate_factor_frame_manifest(ROOT, wrong_factor)

        wrong_factor_availability = self.manifest()
        wrong_factor_availability["output_schema"][6]["nullable"] = False
        with self.assertRaisesRegex(
            contracts.ContractViolation,
            "OUTPUT_FACTOR_AVAILABILITY_SCHEMA_MISMATCH",
        ):
            contracts.validate_factor_frame_manifest(ROOT, wrong_factor_availability)

        manifest = self.manifest()
        envelope = contracts.load_contract_json(
            ROOT / "golden" / "factor-frame-hash-v1.json"
        )["canonical_input"]
        missing_availability = copy.deepcopy(envelope)
        missing_availability["records"][0][6] = {"t": "null"}
        with self.assertRaisesRegex(
            contracts.ContractViolation, "GOLDEN_FACTOR_AVAILABILITY_MISSING"
        ):
            contracts._validate_record_types(missing_availability, manifest)

        early_availability = copy.deepcopy(envelope)
        early_availability["records"][0][6]["v"] = "1788141600123456788"
        with self.assertRaisesRegex(
            contracts.ContractViolation, "GOLDEN_FACTOR_AVAILABLE_BEFORE_SOURCE"
        ):
            contracts._validate_record_types(early_availability, manifest)

        future_factor = copy.deepcopy(envelope)
        future_factor["records"][0][6]["v"] = "1788141600123456790"
        with self.assertRaisesRegex(
            contracts.ContractViolation, "GOLDEN_NON_NULL_FACTOR_AFTER_AS_OF"
        ):
            contracts._validate_record_types(future_factor, manifest)

        fixed_as_of = copy.deepcopy(manifest)
        fixed_as_of["as_of"] = {
            "mode": "fixed",
            "fixed_at_ns": "1788141600123456788",
        }
        with self.assertRaisesRegex(
            contracts.ContractViolation, "GOLDEN_NON_NULL_FACTOR_AFTER_AS_OF"
        ):
            contracts._validate_record_types(envelope, fixed_as_of)

        source_before_event = copy.deepcopy(envelope)
        source_before_event["records"][0][4]["v"] = "1788141600123456788"
        with self.assertRaisesRegex(
            contracts.ContractViolation, "GOLDEN_SOURCE_AVAILABLE_BEFORE_EVENT"
        ):
            contracts._validate_record_types(source_before_event, manifest)

        wrong_row_count = copy.deepcopy(envelope)
        wrong_row_count["records"] = []
        with self.assertRaisesRegex(
            contracts.ContractViolation, "GOLDEN_OUTPUT_ROW_COUNT_MISMATCH"
        ):
            contracts._validate_record_types(wrong_row_count, manifest)

        wrong_column_count = copy.deepcopy(envelope)
        wrong_column_count["records"][0].pop()
        with self.assertRaisesRegex(
            contracts.ContractViolation, "GOLDEN_OUTPUT_COLUMN_COUNT_MISMATCH"
        ):
            contracts._validate_record_types(wrong_column_count, manifest)

        null_identity = copy.deepcopy(envelope)
        null_identity["records"][0][0] = {"t": "null"}
        with self.assertRaisesRegex(
            contracts.ContractViolation, "GOLDEN_NULL_IN_REQUIRED_COLUMN"
        ):
            contracts._validate_record_types(null_identity, manifest)

        wrong_cell_type = copy.deepcopy(envelope)
        wrong_cell_type["records"][0][0] = {"t": "ts_ns", "v": "1"}
        with self.assertRaisesRegex(
            contracts.ContractViolation, "GOLDEN_OUTPUT_TYPE_MISMATCH"
        ):
            contracts._validate_record_types(wrong_cell_type, manifest)

        duplicate = copy.deepcopy(envelope)
        duplicate["records"].append(copy.deepcopy(duplicate["records"][0]))
        two_rows = copy.deepcopy(manifest)
        two_rows["output_rows"] = "2"
        with self.assertRaisesRegex(
            contracts.ContractViolation, "GOLDEN_DUPLICATE_RECORD_IDENTITY"
        ):
            contracts._validate_record_types(duplicate, two_rows)

        unsorted = copy.deepcopy(duplicate)
        unsorted["records"][0][3]["v"] = "event-0008"
        with self.assertRaisesRegex(
            contracts.ContractViolation, "GOLDEN_RECORDS_NOT_SORTED"
        ):
            contracts._validate_record_types(unsorted, two_rows)

    def test_typed_projection_preserves_full_int64_domain(self) -> None:
        maximum = self.manifest()
        maximum["frequency"]["interval_ns"] = str(2**63 - 1)
        contracts.validate_factor_frame_manifest(ROOT, maximum)
        maximum_hash = contracts.hashlib.sha256(
            contracts._jcs_bytes(
                contracts._typed_cell(contracts._manifest_projection(maximum))
            )
        ).hexdigest()

        preceding = copy.deepcopy(maximum)
        preceding["frequency"]["interval_ns"] = str(2**63 - 2)
        preceding_hash = contracts.hashlib.sha256(
            contracts._jcs_bytes(
                contracts._typed_cell(contracts._manifest_projection(preceding))
            )
        ).hexdigest()
        self.assertNotEqual(maximum_hash, preceding_hash)

        out_of_range = copy.deepcopy(maximum)
        out_of_range["frequency"]["interval_ns"] = str(2**63)
        with self.assertRaisesRegex(
            contracts.ContractViolation, "FREQUENCY_INTERVAL_OUT_OF_RANGE"
        ):
            contracts.validate_factor_frame_manifest(ROOT, out_of_range)

    def test_all_typed_cell_forms_and_errors(self) -> None:
        valid = [
            {"t": "bool", "v": True},
            {"t": "fixed", "u": "123", "s": "2"},
            {"t": "date", "v": "2026-08-31"},
            {"t": "binary", "v": "AQ"},
            {"t": "utf8", "v": "PureSaber"},
            {"t": "list", "v": [{"t": "null"}]},
            {"t": "struct", "v": [["x", {"t": "bool", "v": False}]]},
        ]
        for cell in valid:
            contracts.validate_typed_cell(cell)

        invalid = [
            ({"t": "binary", "v": "!!"}, "CELL_INVALID_BASE64URL"),
            ({"t": "binary", "v": "AQ=="}, "CELL_NON_CANONICAL_BASE64URL"),
            ({"t": "i64", "v": "-0"}, "NON_CANONICAL_NEGATIVE_ZERO"),
            ({"t": "fixed", "u": "-0", "s": "0"}, "NON_CANONICAL_NEGATIVE_ZERO"),
            ({"t": "ts_ns", "v": "-0"}, "NON_CANONICAL_NEGATIVE_ZERO"),
            ({"t": "unknown"}, "CELL_UNKNOWN_TAG"),
        ]
        for cell, code in invalid:
            with self.assertRaisesRegex(contracts.ContractViolation, code):
                contracts.validate_typed_cell(cell)

        with self.assertRaisesRegex(
            contracts.ContractViolation, "MANIFEST_INTEGER_OUT_OF_RANGE"
        ):
            contracts._typed_cell(2**63)
        with self.assertRaisesRegex(
            contracts.ContractViolation, "MANIFEST_UNSUPPORTED_TYPE"
        ):
            contracts._typed_cell(1.5)

        utf16_order = contracts._typed_cell({"\ue000": 1, "😀": 2})["v"]
        self.assertEqual([item[0] for item in utf16_order], ["😀", "\ue000"])

        negative_zero_as_of = self.manifest()
        negative_zero_as_of["as_of"] = {"mode": "fixed", "fixed_at_ns": "-0"}
        negative_zero_as_of["certification_scope"] = "research-restated"
        with self.assertRaises(ValidationError):
            contracts.validate_factor_frame_manifest(ROOT, negative_zero_as_of)

        negative_zero_envelope = contracts.load_contract_json(
            ROOT / "golden" / "factor-frame-hash-v1.json"
        )["canonical_input"]
        negative_zero_envelope["records"][0][2]["v"] = "-0"
        with self.assertRaises(ValidationError):
            contracts._validate_schema(
                ROOT, "canonical-envelope.schema.json", negative_zero_envelope
            )

    def test_golden_wrapper_and_cross_bindings_fail_closed(self) -> None:
        self.assert_golden_failure(
            "GOLDEN_WRAPPER_SCHEMA_MISMATCH",
            golden_mutator=lambda value: value.update({"unexpected": True}),
        )
        self.assert_golden_failure(
            "GOLDEN_UNSAFE_MANIFEST_REFERENCE",
            golden_mutator=lambda value: value.update(
                {"manifest_file": "../factor-frame-manifest-v1.json"}
            ),
        )
        self.assert_golden_failure(
            "GOLDEN_MANIFEST_PROJECTION_HASH_MISMATCH",
            golden_mutator=lambda value: value.update(
                {"manifest_projection_sha256": ZERO}
            ),
        )
        self.assert_golden_failure(
            "GOLDEN_METADATA_BINDING_MISMATCH",
            golden_mutator=lambda value: value["canonical_input"]["metadata"]["v"][0][
                1
            ].update({"v": ZERO}),
        )
        self.assert_golden_failure(
            "GOLDEN_OUTPUT_SCHEMA_BINDING_MISMATCH",
            golden_mutator=lambda value: value["canonical_input"]["output_schema"]["v"][
                0
            ]["v"][1][1].update({"v": "binary"}),
        )
        self.assert_golden_failure(
            "GOLDEN_CANONICAL_BYTES_MISMATCH",
            golden_mutator=lambda value: value.update({"canonical_utf8_hex": "00"}),
        )
        self.assert_golden_failure(
            "GOLDEN_HASH_MISMATCH",
            golden_mutator=lambda value: value.update({"sha256": ZERO}),
        )
        self.assert_golden_failure(
            "GOLDEN_MANIFEST_HASH_MISMATCH",
            manifest_mutator=lambda value: value.update(
                {"logical_content_sha256": ZERO}
            ),
        )

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
                "OUTPUT_SCHEMA_ORDER_MISMATCH|PROJECTION_HASH_MISMATCH",
            ):
                contracts.validate_golden_bundle(
                    copied, copied / "golden" / "factor-frame-hash-v1.json"
                )


if __name__ == "__main__":
    unittest.main()
