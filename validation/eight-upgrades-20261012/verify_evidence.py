"""Verify retained evidence bytes; no runtime, market, or release certification."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
manifest = json.loads((root / 'evidence-manifest.json').read_text(encoding='utf-8'))
assert manifest['schema'] == 'quant.delivery-evidence/v1'
for name, expected in manifest['files'].items():
    file = (root / name).resolve()
    if not file.is_relative_to(root) or hashlib.sha256(file.read_bytes()).hexdigest() != expected:
        raise SystemExit('Evidence verification failed: ' + name)
print(f"Verified {len(manifest['files'])} retained evidence files; no economic certification implied.")
