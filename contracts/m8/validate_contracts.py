"""Machine-semantic validation for the PureSaber M8 contract package."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
import struct
from datetime import date
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

INT64_MIN = -(2**63)
INT64_MAX = 2**63 - 1
INTEGER_RANGES = {
    "i8": (-(2**7), 2**7 - 1),
    "i16": (-(2**15), 2**15 - 1),
    "i32": (-(2**31), 2**31 - 1),
    "i64": (INT64_MIN, INT64_MAX),
    "u8": (0, 2**8 - 1),
    "u16": (0, 2**16 - 1),
    "u32": (0, 2**32 - 1),
    "u64": (0, 2**64 - 1),
}
IDENTITY_COLUMNS = (
    "instrument_id",
    "event_time",
    "sequence",
    "event_id",
    "source_available_at",
)


class ContractViolation(ValueError):
    """A stable contract invariant was violated."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractViolation(f"JSON_DUPLICATE_KEY:{key}")
        result[key] = value
    return result


def load_contract_json(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=_reject_duplicate_keys
    )


def _schema_context(root: Path) -> tuple[dict[str, dict[str, Any]], Registry]:
    schemas: dict[str, dict[str, Any]] = {}
    registry = Registry()
    for path in sorted(root.glob("*.schema.json")):
        schema = load_contract_json(path)
        Draft202012Validator.check_schema(schema)
        schemas[path.name] = schema
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    return schemas, registry


def _validate_schema(
    root: Path,
    schema_name: str,
    value: Any,
    *,
    context: tuple[dict[str, dict[str, Any]], Registry] | None = None,
) -> None:
    schemas, registry = context or _schema_context(root)
    Draft202012Validator(
        schemas[schema_name],
        registry=registry,
        format_checker=FormatChecker(),
    ).validate(value)


def _require_unique(items: list[Any], key, code: str) -> None:
    seen: set[Any] = set()
    for item in items:
        identity = key(item)
        if identity in seen:
            raise ContractViolation(f"{code}:{identity}")
        seen.add(identity)


def _parse_bounded_integer(value: str, minimum: int, maximum: int, code: str) -> int:
    parsed = int(value)
    if not minimum <= parsed <= maximum:
        raise ContractViolation(code)
    return parsed


def _require_sorted(items: list[Any], key, code: str) -> None:
    identities = [key(item) for item in items]
    if identities != sorted(identities):
        raise ContractViolation(code)


def _event_schema_key(item: dict[str, Any]) -> tuple[str, str]:
    return item["schema_id"], item["schema_version"]


def _validate_frequency(value: dict[str, Any]) -> None:
    if value["kind"] == "fixed_time_bar":
        _parse_bounded_integer(
            value["interval_ns"], 1, INT64_MAX, "FREQUENCY_INTERVAL_OUT_OF_RANGE"
        )
    if value["kind"] == "event_bar":
        _parse_bounded_integer(
            value["event_bar_threshold"]["units"],
            1,
            INT64_MAX,
            "FREQUENCY_THRESHOLD_OUT_OF_RANGE",
        )
    if value["market_event_types"] is not None and value[
        "market_event_types"
    ] != sorted(value["market_event_types"]):
        raise ContractViolation("FREQUENCY_EVENT_TYPES_NOT_SORTED")


def _validate_aggregation(value: dict[str, Any]) -> None:
    if value["kind"] == "fixed_time_bar":
        _parse_bounded_integer(
            value["interval_ns"], 1, INT64_MAX, "AGGREGATION_INTERVAL_OUT_OF_RANGE"
        )
    _require_unique(
        value["source_event_schemas"],
        _event_schema_key,
        "AGGREGATION_DUPLICATE_SOURCE_SCHEMA",
    )
    _require_sorted(
        value["source_event_schemas"],
        _event_schema_key,
        "AGGREGATION_SOURCE_SCHEMAS_NOT_SORTED",
    )
    if value["kind"] != "event_bar":
        return
    _parse_bounded_integer(
        value["event_bar_threshold"]["units"],
        1,
        INT64_MAX,
        "AGGREGATION_THRESHOLD_OUT_OF_RANGE",
    )
    evidence = value["partition_evidence"]
    _require_unique(
        evidence, lambda item: item["relative_path"], "EVENT_BAR_DUPLICATE_PARTITION"
    )
    _require_sorted(
        evidence, lambda item: item["relative_path"], "EVENT_BAR_PARTITIONS_NOT_SORTED"
    )
    for item in evidence:
        first = _parse_bounded_integer(
            item["first_sequence"], 0, INT64_MAX, "EVENT_BAR_SEQUENCE_OUT_OF_RANGE"
        )
        last = _parse_bounded_integer(
            item["last_sequence"], 0, INT64_MAX, "EVENT_BAR_SEQUENCE_OUT_OF_RANGE"
        )
        count = _parse_bounded_integer(
            item["event_count"], 1, INT64_MAX, "EVENT_BAR_COUNT_OUT_OF_RANGE"
        )
        if first > last:
            raise ContractViolation("EVENT_BAR_REVERSED_SEQUENCE_RANGE")
        if count > last - first + 1:
            raise ContractViolation("EVENT_BAR_COUNT_EXCEEDS_SEQUENCE_RANGE")


def validate_verified_factor_input(root: Path, value: dict[str, Any]) -> None:
    _validate_schema(root, "verified-factor-input.schema.json", value)
    _parse_bounded_integer(value["rows"], 1, INT64_MAX, "INPUT_ROWS_OUT_OF_RANGE")
    _require_unique(
        value["event_schemas"],
        _event_schema_key,
        "INPUT_DUPLICATE_EVENT_SCHEMA",
    )
    _require_sorted(
        value["event_schemas"], _event_schema_key, "INPUT_EVENT_SCHEMAS_NOT_SORTED"
    )
    _require_unique(
        value["lineage"],
        lambda item: (item["role"], item["snapshot_id"]),
        "INPUT_DUPLICATE_LINEAGE",
    )
    _require_sorted(
        value["lineage"],
        lambda item: (item["role"], item["snapshot_id"]),
        "INPUT_LINEAGE_NOT_SORTED",
    )
    if value["layer"] == "curated":
        aggregation = value["aggregation"]
        _validate_aggregation(aggregation)
        pairs = (
            ("calendar_id", "INPUT_CALENDAR_MISMATCH"),
            ("session_policy_version", "INPUT_SESSION_POLICY_MISMATCH"),
            ("market_context_snapshot_id", "INPUT_CONTEXT_ID_MISMATCH"),
            ("market_context_logical_sha256", "INPUT_CONTEXT_HASH_MISMATCH"),
        )
        for field, code in pairs:
            if value[field] != aggregation[field]:
                raise ContractViolation(code)


def _validate_auxiliary_source(root: Path, value: dict[str, Any]) -> None:
    _validate_schema(root, "auxiliary-source.schema.json", value)
    _require_unique(
        value["business_key_columns"], lambda item: item, "AUX_DUPLICATE_BUSINESS_KEY"
    )


def validate_factor_frame_manifest(root: Path, value: dict[str, Any]) -> None:
    _validate_schema(root, "factor-frame-manifest.schema.json", value)
    _validate_frequency(value["frequency"])
    _parse_bounded_integer(value["input_rows"], 0, INT64_MAX, "INPUT_ROWS_OUT_OF_RANGE")
    _parse_bounded_integer(
        value["output_rows"], 0, INT64_MAX, "OUTPUT_ROWS_OUT_OF_RANGE"
    )
    as_of = value["as_of"]
    if as_of["mode"] == "fixed":
        _parse_bounded_integer(
            as_of["fixed_at_ns"], INT64_MIN, INT64_MAX, "AS_OF_OUT_OF_RANGE"
        )
    _require_unique(
        value["factor_specs"], lambda item: item["factor_id"], "DUPLICATE_FACTOR"
    )
    _require_sorted(
        value["factor_specs"], lambda item: item["factor_id"], "FACTOR_SPECS_NOT_SORTED"
    )
    _require_unique(
        value["input_event_schemas"], _event_schema_key, "DUPLICATE_INPUT_EVENT_SCHEMA"
    )
    _require_sorted(
        value["input_event_schemas"],
        _event_schema_key,
        "INPUT_EVENT_SCHEMAS_NOT_SORTED",
    )
    _require_unique(
        value["source_lineage"],
        lambda item: (item["role"], item["snapshot_id"]),
        "DUPLICATE_SOURCE_LINEAGE",
    )
    _require_sorted(
        value["source_lineage"],
        lambda item: (item["role"], item["snapshot_id"]),
        "SOURCE_LINEAGE_NOT_SORTED",
    )
    _require_unique(
        value["output_schema"], lambda item: item["name"], "DUPLICATE_OUTPUT_COLUMN"
    )
    _require_unique(
        value["auxiliary_sources"],
        lambda item: (item["role"], item["snapshot_id"]),
        "DUPLICATE_AUXILIARY_SOURCE",
    )
    _require_sorted(
        value["auxiliary_sources"],
        lambda item: (item["role"], item["snapshot_id"]),
        "AUXILIARY_SOURCES_NOT_SORTED",
    )
    for auxiliary in value["auxiliary_sources"]:
        _validate_auxiliary_source(root, auxiliary)
    for factor in value["factor_specs"]:
        _require_unique(
            factor["dependencies"],
            lambda item: (item["role"], item["value_column"]),
            "DUPLICATE_FACTOR_DEPENDENCY",
        )
        _require_sorted(
            factor["dependencies"],
            lambda item: (item["role"], item["value_column"]),
            "FACTOR_DEPENDENCIES_NOT_SORTED",
        )
    frequency = value["frequency"]
    input_schemas = value["input_event_schemas"]
    if frequency["kind"] == "market_event":
        if any(
            factor["input_profile"] != "market_event"
            for factor in value["factor_specs"]
        ):
            raise ContractViolation("MARKET_EVENT_REQUIRES_EVENT_FACTORS")
        if [item["schema_id"] for item in input_schemas] != frequency[
            "market_event_types"
        ]:
            raise ContractViolation("MARKET_EVENT_SCHEMA_SET_MISMATCH")
    else:
        if any(factor["input_profile"] != "bar" for factor in value["factor_specs"]):
            raise ContractViolation("BAR_FREQUENCY_REQUIRES_BAR_FACTORS")
        if input_schemas != [
            {"schema_id": "puresaber.bar-event", "schema_version": "2.0.0"}
        ]:
            raise ContractViolation("BAR_INPUT_SCHEMA_MISMATCH")
    lineage_keys = {
        (item["role"], item["snapshot_id"], item["logical_sha256"])
        for item in value["source_lineage"]
    }
    lineage_roles = {item["role"] for item in value["source_lineage"]}
    auxiliary_by_role: dict[str, list[dict[str, Any]]] = {}
    for auxiliary in value["auxiliary_sources"]:
        auxiliary_by_role.setdefault(auxiliary["role"], []).append(auxiliary)
    for auxiliary in value["auxiliary_sources"]:
        expected = (
            auxiliary["role"],
            auxiliary["snapshot_id"],
            auxiliary["logical_sha256"],
        )
        if expected not in lineage_keys:
            raise ContractViolation("AUXILIARY_LINEAGE_MISSING")
    referenced_auxiliary_roles: set[str] = set()
    for factor in value["factor_specs"]:
        for dependency in factor["dependencies"]:
            role = dependency["role"]
            if role not in lineage_roles:
                raise ContractViolation(f"FACTOR_DEPENDENCY_LINEAGE_MISSING:{role}")
            if role in auxiliary_by_role:
                referenced_auxiliary_roles.add(role)
                if any(
                    item["value_availability"].get(dependency["value_column"])
                    != dependency["availability_column"]
                    for item in auxiliary_by_role[role]
                ):
                    raise ContractViolation(f"FACTOR_AUXILIARY_MAPPING_MISMATCH:{role}")
    unused_auxiliary_roles = set(auxiliary_by_role) - referenced_auxiliary_roles
    if unused_auxiliary_roles:
        raise ContractViolation(
            f"AUXILIARY_FACTOR_DEPENDENCY_MISSING:{min(unused_auxiliary_roles)}"
        )
    names = tuple(item["name"] for item in value["output_schema"])
    expected_names = IDENTITY_COLUMNS + tuple(
        name
        for factor in value["factor_specs"]
        for name in (factor["factor_id"], f"{factor['factor_id']}__available_at")
    )
    if names != expected_names:
        raise ContractViolation("OUTPUT_SCHEMA_ORDER_MISMATCH")
    expected_identity_schema = (
        ("instrument_id", "utf8", False),
        ("event_time", "timestamp[ns,UTC]", False),
        ("sequence", "int64", False),
        ("event_id", "utf8", False),
        ("source_available_at", "timestamp[ns,UTC]", False),
    )
    actual_identity_schema = tuple(
        (item["name"], item["arrow_type"], item["nullable"])
        for item in value["output_schema"][: len(IDENTITY_COLUMNS)]
    )
    if actual_identity_schema != expected_identity_schema:
        raise ContractViolation("OUTPUT_IDENTITY_SCHEMA_MISMATCH")
    schema_by_name = {item["name"]: item for item in value["output_schema"]}
    for factor in value["factor_specs"]:
        factor_field = schema_by_name[factor["factor_id"]]
        available_field = schema_by_name[f"{factor['factor_id']}__available_at"]
        if factor_field != {
            "name": factor["factor_id"],
            "arrow_type": "float64",
            "nullable": True,
        }:
            raise ContractViolation(
                f"OUTPUT_FACTOR_SCHEMA_MISMATCH:{factor['factor_id']}"
            )
        if available_field != {
            "name": f"{factor['factor_id']}__available_at",
            "arrow_type": "timestamp[ns,UTC]",
            "nullable": True,
        }:
            raise ContractViolation(
                f"OUTPUT_FACTOR_AVAILABILITY_SCHEMA_MISMATCH:{factor['factor_id']}"
            )


def _validate_binary64(hex_value: str) -> None:
    bits = int(hex_value, 16)
    if bits == 0x8000000000000000:
        raise ContractViolation("CELL_NEGATIVE_ZERO")
    value = struct.unpack(">d", bits.to_bytes(8, "big"))[0]
    if not math.isfinite(value):
        raise ContractViolation("CELL_NON_FINITE_FLOAT")


def validate_typed_cell(cell: dict[str, Any]) -> None:
    tag = cell["t"]
    if tag == "null":
        return
    if tag == "bool":
        return
    if tag in INTEGER_RANGES:
        minimum, maximum = INTEGER_RANGES[tag]
        _parse_bounded_integer(
            cell["v"], minimum, maximum, f"CELL_{tag.upper()}_OUT_OF_RANGE"
        )
        return
    if tag == "f64":
        _validate_binary64(cell["v"])
        return
    if tag == "fixed":
        _parse_bounded_integer(
            cell["u"], INT64_MIN, INT64_MAX, "CELL_FIXED_OUT_OF_RANGE"
        )
        return
    if tag == "ts_ns":
        _parse_bounded_integer(
            cell["v"], INT64_MIN, INT64_MAX, "CELL_TIMESTAMP_OUT_OF_RANGE"
        )
        return
    if tag == "date":
        try:
            parsed = date.fromisoformat(cell["v"])
        except ValueError as exc:
            raise ContractViolation("CELL_INVALID_DATE") from exc
        if parsed.isoformat() != cell["v"]:
            raise ContractViolation("CELL_NON_CANONICAL_DATE")
        return
    if tag == "binary":
        encoded = cell["v"]
        if len(encoded) % 4 == 1:
            raise ContractViolation("CELL_INVALID_BASE64URL")
        try:
            decoded = base64.b64decode(
                encoded + "=" * ((4 - len(encoded) % 4) % 4),
                altchars=b"-_",
                validate=True,
            )
        except ValueError as exc:
            raise ContractViolation("CELL_INVALID_BASE64URL") from exc
        if base64.urlsafe_b64encode(decoded).decode("ascii").rstrip("=") != encoded:
            raise ContractViolation("CELL_NON_CANONICAL_BASE64URL")
        return
    if tag == "utf8":
        return
    if tag == "list":
        for item in cell["v"]:
            validate_typed_cell(item)
        return
    if tag == "struct":
        _require_unique(cell["v"], lambda item: item[0], "CELL_DUPLICATE_STRUCT_FIELD")
        for _, item in cell["v"]:
            validate_typed_cell(item)
        return
    raise ContractViolation(f"CELL_UNKNOWN_TAG:{tag}")


def _typed_cell(value: Any) -> dict[str, Any]:
    if value is None:
        return {"t": "null"}
    if isinstance(value, bool):
        return {"t": "bool", "v": value}
    if isinstance(value, int):
        if not INT64_MIN <= value <= INT64_MAX:
            raise ContractViolation("MANIFEST_INTEGER_OUT_OF_RANGE")
        return {"t": "i64", "v": str(value)}
    if isinstance(value, str):
        return {"t": "utf8", "v": value}
    if isinstance(value, list):
        return {"t": "list", "v": [_typed_cell(item) for item in value]}
    if isinstance(value, dict):
        return {
            "t": "struct",
            "v": [[key, _typed_cell(value[key])] for key in sorted(value)],
        }
    raise ContractViolation(f"MANIFEST_UNSUPPORTED_TYPE:{type(value).__name__}")


def _jcs_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _manifest_projection(manifest: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in manifest.items()
        if key not in {"logical_content_sha256", "physical_sha256"}
    }


def _output_schema_cell(fields: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "t": "list",
        "v": [
            {
                "t": "struct",
                "v": [
                    ["name", _typed_cell(field["name"])],
                    ["arrow_type", _typed_cell(field["arrow_type"])],
                    ["nullable", _typed_cell(field["nullable"])],
                ],
            }
            for field in fields
        ],
    }


def _validate_record_types(envelope: dict[str, Any], manifest: dict[str, Any]) -> None:
    expected_tags = {
        "utf8": "utf8",
        "timestamp[ns,UTC]": "ts_ns",
        "int64": "i64",
        "float64": "f64",
    }
    output_schema = manifest["output_schema"]
    if len(envelope["records"]) != int(manifest["output_rows"]):
        raise ContractViolation("GOLDEN_OUTPUT_ROW_COUNT_MISMATCH")
    schema_index = {field["name"]: index for index, field in enumerate(output_schema)}
    factor_pairs = [
        (
            schema_index[factor["factor_id"]],
            schema_index[f"{factor['factor_id']}__available_at"],
        )
        for factor in manifest["factor_specs"]
    ]
    identities: list[tuple[str, int, int, str]] = []
    for row in envelope["records"]:
        if len(row) != len(output_schema):
            raise ContractViolation("GOLDEN_OUTPUT_COLUMN_COUNT_MISMATCH")
        for cell, field in zip(row, output_schema, strict=True):
            validate_typed_cell(cell)
            if cell["t"] == "null":
                if not field["nullable"]:
                    raise ContractViolation(
                        f"GOLDEN_NULL_IN_REQUIRED_COLUMN:{field['name']}"
                    )
                continue
            expected = expected_tags.get(field["arrow_type"])
            if expected is None or cell["t"] != expected:
                raise ContractViolation(f"GOLDEN_OUTPUT_TYPE_MISMATCH:{field['name']}")
        event_time = int(row[schema_index["event_time"]]["v"])
        source_available_at = int(row[schema_index["source_available_at"]]["v"])
        if event_time > source_available_at:
            raise ContractViolation("GOLDEN_SOURCE_AVAILABLE_BEFORE_EVENT")
        for factor_index, availability_index in factor_pairs:
            factor_cell = row[factor_index]
            availability_cell = row[availability_index]
            if factor_cell["t"] != "null" and availability_cell["t"] == "null":
                raise ContractViolation("GOLDEN_FACTOR_AVAILABILITY_MISSING")
            if (
                availability_cell["t"] != "null"
                and int(availability_cell["v"]) < source_available_at
            ):
                raise ContractViolation("GOLDEN_FACTOR_AVAILABLE_BEFORE_SOURCE")
        identities.append(
            (
                row[schema_index["instrument_id"]]["v"],
                event_time,
                int(row[schema_index["sequence"]]["v"]),
                row[schema_index["event_id"]]["v"],
            )
        )
    if len(identities) != len(set(identities)):
        raise ContractViolation("GOLDEN_DUPLICATE_RECORD_IDENTITY")
    if identities != sorted(identities):
        raise ContractViolation("GOLDEN_RECORDS_NOT_SORTED")


def validate_golden_bundle(root: Path, golden_path: Path) -> None:
    golden = load_contract_json(golden_path)
    if (
        set(golden)
        != {
            "schema",
            "manifest_file",
            "manifest_projection_sha256",
            "canonical_input",
            "canonical_utf8_hex",
            "sha256",
        }
        or golden["schema"] != "puresaber.factor-frame-hash-golden@1.0.0"
    ):
        raise ContractViolation("GOLDEN_WRAPPER_SCHEMA_MISMATCH")
    manifest_name = golden["manifest_file"]
    if Path(manifest_name).name != manifest_name:
        raise ContractViolation("GOLDEN_UNSAFE_MANIFEST_REFERENCE")
    manifest = load_contract_json(golden_path.parent / manifest_name)
    validate_factor_frame_manifest(root, manifest)
    projection_hash = hashlib.sha256(
        _jcs_bytes(_typed_cell(_manifest_projection(manifest)))
    ).hexdigest()
    if projection_hash != golden["manifest_projection_sha256"]:
        raise ContractViolation("GOLDEN_MANIFEST_PROJECTION_HASH_MISMATCH")
    envelope = golden["canonical_input"]
    _validate_schema(root, "canonical-envelope.schema.json", envelope)
    validate_typed_cell(envelope["metadata"])
    validate_typed_cell(envelope["output_schema"])
    expected_metadata = {
        "t": "struct",
        "v": [
            ["manifest_projection_sha256", {"t": "utf8", "v": projection_hash}],
            ["manifest_schema_id", {"t": "utf8", "v": manifest["schema_id"]}],
        ],
    }
    if envelope["metadata"] != expected_metadata:
        raise ContractViolation("GOLDEN_METADATA_BINDING_MISMATCH")
    if envelope["output_schema"] != _output_schema_cell(manifest["output_schema"]):
        raise ContractViolation("GOLDEN_OUTPUT_SCHEMA_BINDING_MISMATCH")
    _validate_record_types(envelope, manifest)
    canonical = _jcs_bytes(envelope)
    logical_hash = hashlib.sha256(canonical).hexdigest()
    if canonical.hex() != golden["canonical_utf8_hex"]:
        raise ContractViolation("GOLDEN_CANONICAL_BYTES_MISMATCH")
    if logical_hash != golden["sha256"]:
        raise ContractViolation("GOLDEN_HASH_MISMATCH")
    if manifest["logical_content_sha256"] != logical_hash:
        raise ContractViolation("GOLDEN_MANIFEST_HASH_MISMATCH")


def validate_contract_suite(root: Path) -> None:
    _schema_context(root)
    validate_golden_bundle(root, root / "golden" / "factor-frame-hash-v1.json")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    validate_contract_suite(args.root.resolve())
    print("M8 contracts: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
