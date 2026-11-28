"""Restore the image collection from its public sources (Python 3.8+)."""

import hashlib
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "references" / "east-central" / "sources.json"
DESTINATION = ROOT / "tmp" / "reference-images-east-central"


def restore(entry):
    target = DESTINATION / Path(entry["file"]).name
    expected = entry["sha256"]
    if target.exists():
        if hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            raise ValueError(f"existing local file differs: {target.name}")
        return "verified"

    request = Request(
        quote(entry["asset_url"], safe=":/?&=+%#;,()"),
        headers={"User-Agent": "Mozilla/5.0", "Referer": entry["page"]},
    )
    with urlopen(request, timeout=40) as response:
        data = response.read()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError(f"published file differs: {target.name}")

    with NamedTemporaryFile(dir=DESTINATION, delete=False) as staging:
        temporary = Path(staging.name)
    try:
        temporary.write_bytes(data)
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
    return "downloaded"


def main():
    entries = json.loads(MANIFEST.read_text("utf-8"))["images"]
    DESTINATION.mkdir(parents=True, exist_ok=True)
    failures = 0
    for entry in entries:
        try:
            print(entry["id"], restore(entry))
        except (OSError, ValueError) as exc:
            print(entry["id"], str(exc))
            failures += 1
    return bool(failures)


if __name__ == "__main__":
    raise SystemExit(main())
