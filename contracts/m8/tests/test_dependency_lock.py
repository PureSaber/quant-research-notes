"""Keep the hashed CI environment aligned with its direct requirements."""

import re
import unittest
from pathlib import Path


class DependencyLockTests(unittest.TestCase):
    def test_direct_versions_match_hashed_lock(self):
        root = Path(__file__).resolve().parents[1]
        pattern = r"^([A-Za-z0-9_.-]+)==([^ ;\\\n]+)"
        declared = dict(
            re.findall(pattern, (root / "requirements.in").read_text(), re.MULTILINE)
        )
        locked = dict(
            re.findall(pattern, (root / "requirements.lock").read_text(), re.MULTILINE)
        )
        self.assertTrue(declared)
        for package, version in declared.items():
            with self.subTest(package=package):
                self.assertEqual(locked.get(package), version)
