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
IDENTITY_COLUMNS = ("instrument_id", "event_time", "sequence", "event_id")


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


def validate_verified_factor_input(root: Path, value: dict[str, Any]) -> None:
    _validate_schema(root, "verified-factor-input.schema.json", value)
    _require_unique(
        value["event_schemas"],
        lambda item: (item["schema_id"], item["schema_version"]),
        "INPUT_DUPLICATE_EVENT_SCHEMA",
    )
    _require_unique(
        value["lineage"],
        lambda item: (item["role"], item["snapshot_id"]),
        "INPUT_DUPLICATE_LINEAGE",
    )
    if value["layer"] == "curated":
        aggregation = value["aggregation"]
        pairs = (
            ("calendar_id", "INPUT_CALENDAR_MISMATCH"),
            ("session_policy_version", "INPUT_SESSION_POLICY_MISMATCH"),
            ("market_context_snapshot_id", "INPUT_CONTEXT_ID_MISMATCH"),
            ("market_context_logical_sha256", "INPUT_CONTEXT_HASH_MISMATCH"),
        )
        for field, code in pairs:
            if value[field] != aggregation[field]:
                raise ContractViolation(code)
    elif any(
        item["schema_id"] == "puresaber.bar-event" for item in value["event_schemas"]
    ):
        raise ContractViolation("INPUT_NORMALIZED_BAR_FORBIDDEN")


def _validate_auxiliary_source(root: Path, value: dict[str, Any]) -> None:
    _validate_schema(root, "auxiliary-source.schema.json", value)
    _require_unique(
        value["business_key_columns"], lambda item: item, "AUX_DUPLICATE_BUSINESS_KEY"
    )


def validate_factor_frame_manifest(root: Path, value: dict[str, Any]) -> None:
    _validate_schema(root, "factor-frame-manifest.schema.json", value)
    as_of = value["as_of"]
    if as_of["mode"] == "fixed":
        _parse_bounded_integer(
            as_of["fixed_at_ns"], INT64_MIN, INT64_MAX, "AS_OF_OUT_OF_RANGE"
        )
    _require_unique(
        value["factor_specs"], lambda item: item["factor_id"], "DUPLICATE_FACTOR"
    )
    _require_unique(
        value["source_lineage"],
        lambda item: (item["role"], item["snapshot_id"]),
        "DUPLICATE_SOURCE_LINEAGE",
    )
    _require_unique(
        value["output_schema"], lambda item: item["name"], "DUPLICATE_OUTPUT_COLUMN"
    )
    _require_unique(
        value["auxiliary_sources"],
        lambda item: (item["role"], item["snapshot_id"]),
        "DUPLICATE_AUXILIARY_SOURCE",
    )
    for auxiliary in value["auxiliary_sources"]:
        _validate_auxiliary_source(root, auxiliary)
    for factor in value["factor_specs"]:
        _require_unique(
            factor["dependencies"],
            lambda item: (item["role"], item["value_column"]),
            "DUPLICATE_FACTOR_DEPENDENCY",
        )
    names = tuple(item["name"] for item in value["output_schema"])
    if names[: len(IDENTITY_COLUMNS)] != IDENTITY_COLUMNS:
        raise ContractViolation("OUTPUT_IDENTITY_PREFIX_MISMATCH")
    for factor in value["factor_specs"]:
        if factor["factor_id"] not in names:
            raise ContractViolation(f"OUTPUT_FACTOR_MISSING:{factor['factor_id']}")
        availability = f"{factor['factor_id']}__available_at"
        if availability not in names:
            raise ContractViolation(
                f"OUTPUT_FACTOR_AVAILABILITY_MISSING:{factor['factor_id']}"
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
    if len(envelope["records"]) != manifest["output_rows"]:
        raise ContractViolation("GOLDEN_OUTPUT_ROW_COUNT_MISMATCH")
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
        _jcs_bytes(_manifest_projection(manifest))
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
