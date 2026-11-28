"""Restore the image collection from its public sources (Python 3.8+)."""

import argparse
import hashlib
import json
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "references" / "east-central" / "sources.json"
DESTINATION = ROOT / "tmp" / "reference-images-east-central"


def checksum(stream, output=None):
    digest = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(chunk)
        if output is not None:
            output.write(chunk)
    return digest.hexdigest()


def restore(entry):
    target = DESTINATION / Path(entry["file"]).name
    expected = entry["sha256"]
    if target.exists():
        with target.open("rb") as stream:
            if checksum(stream) != expected:
                raise ValueError(f"existing local file differs: {target.name}")
        return "verified"

    request = Request(
        quote(entry["asset_url"], safe=":/?&=+%#;,()"),
        headers={"User-Agent": "Mozilla/5.0", "Referer": entry["page"]},
    )
    with TemporaryDirectory(dir=DESTINATION) as staging:
        temporary = Path(staging) / target.name
        with urlopen(request, timeout=40) as response, temporary.open("wb") as output:
            actual = checksum(response, output)
        if actual != expected:
            raise ValueError(f"published file differs: {target.name}")
        os.replace(temporary, target)
    return "downloaded"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ids", nargs="*", metavar="ID", help="image IDs; default: all")
    requested = set(parser.parse_args().ids)
    entries = json.loads(MANIFEST.read_text("utf-8"))["images"]
    unknown = requested.difference(entry["id"] for entry in entries)
    if unknown:
        parser.error("unknown image IDs: " + ", ".join(sorted(unknown)))
    if requested:
        entries = [entry for entry in entries if entry["id"] in requested]
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
