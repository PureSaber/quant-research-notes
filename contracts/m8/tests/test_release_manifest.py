from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_DIRECTORY = REPOSITORY_ROOT / "validation" / "m8"
EXPECTED_FILE_SHA256 = (
    "f90889a154d1419bfb595a524faa13d809d1bb39078ae1abf729c2e7cafd34af"
)
EXPECTED_MANIFEST_SHA256 = (
    "51b8278226a8c550ff14e2908d1ecaf81435cd0579970acba17f8a483978420a"
)


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


class ReleaseManifestTests(unittest.TestCase):
    def test_release_manifests_are_canonical_and_byte_identical(self) -> None:
        paths = [
            MANIFEST_DIRECTORY / "stack-manifest-v2-release-a.json",
            MANIFEST_DIRECTORY / "stack-manifest-v2-release-b.json",
        ]
        raw_manifests = [path.read_bytes() for path in paths]

        self.assertEqual(raw_manifests[0], raw_manifests[1])
        for raw in raw_manifests:
            self.assertNotIn(b"\r", raw)
            self.assertTrue(raw.endswith(b"\n"))
            document = json.loads(raw)
            self.assertEqual(raw, _canonical_json(document) + b"\n")
            self.assertEqual(hashlib.sha256(raw).hexdigest(), EXPECTED_FILE_SHA256)

            claimed_hash = document.pop("manifest_hash")
            self.assertEqual(claimed_hash, EXPECTED_MANIFEST_SHA256)
            self.assertEqual(
                hashlib.sha256(_canonical_json(document)).hexdigest(),
                claimed_hash,
            )


if __name__ == "__main__":
    unittest.main()
