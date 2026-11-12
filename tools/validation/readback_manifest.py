#!/usr/bin/env python3
"""Offline readback manifest verifier.

Given a directory of partition images and a JSON manifest, verify size and
SHA-256 for every entry. Fail-closed: a missing file, a size mismatch, a hash
mismatch, or a duplicate name is an error. No device is opened.

Manifest format:

    {
      "partitions": [
        {"name": "xbl", "file": "xbl.img", "size": 4096,
         "sha256": "..."}
      ]
    }

Usage:
    python3 readback_manifest.py --dir dumps --manifest manifest.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

_HEX64 = re.compile(r"^[0-9a-fA-F]{64}$")


class ManifestError(ValueError):
    """The manifest or the directory is inconsistent."""


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def load_manifest(path: Path) -> list[dict]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ManifestError(f"cannot read manifest: {exc}") from exc
    partitions = raw.get("partitions") if isinstance(raw, dict) else None
    if not isinstance(partitions, list) or not partitions:
        raise ManifestError("manifest must contain a non-empty 'partitions' list")
    out = []
    for i, entry in enumerate(partitions):
        if not isinstance(entry, dict):
            raise ManifestError(f"partition {i} is not an object")
        name = entry.get("name")
        filename = entry.get("file")
        size = entry.get("size")
        digest = entry.get("sha256")
        if not isinstance(name, str) or not name:
            raise ManifestError(f"partition {i}: missing name")
        if not isinstance(filename, str) or not filename:
            raise ManifestError(f"{name}: missing file")
        if not isinstance(size, int) or size < 0:
            raise ManifestError(f"{name}: size must be a non-negative integer")
        if not isinstance(digest, str) or not _HEX64.match(digest):
            raise ManifestError(f"{name}: sha256 must be 64 hex characters")
        out.append(
            {"name": name, "file": filename, "size": size, "sha256": digest.lower()}
        )
    return out


def verify(root: Path, entries: list[dict], strict_extra: bool = False) -> list[str]:
    problems: list[str] = []
    seen_names: set[str] = set()
    seen_files: set[str] = set()
    expected_files: set[str] = set()

    if not root.is_dir():
        return [f"not a directory: {root}"]

    for entry in entries:
        name, filename = entry["name"], entry["file"]
        if name in seen_names:
            problems.append(f"duplicate partition name: {name}")
        seen_names.add(name)
        if filename in seen_files:
            problems.append(f"duplicate file reference: {filename}")
        seen_files.add(filename)
        expected_files.add(filename)

        path = root / filename
        if not path.is_file():
            problems.append(f"{name}: missing file {filename}")
            continue
        size = path.stat().st_size
        if size != entry["size"]:
            problems.append(
                f"{name}: size {size} != manifest {entry['size']}"
            )
            continue
        digest = sha256_file(path)
        if digest != entry["sha256"]:
            problems.append(
                f"{name}: sha256 {digest} != manifest {entry['sha256']}"
            )

    if strict_extra:
        for path in sorted(root.iterdir()):
            if path.is_file() and path.name not in expected_files:
                problems.append(f"unexpected file: {path.name}")

    return problems


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--dir", required=True, type=Path)
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--strict-extra", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    try:
        entries = load_manifest(args.manifest)
    except ManifestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    problems = verify(args.dir, entries, strict_extra=args.strict_extra)
    if args.json:
        print(
            json.dumps(
                {
                    "entries": len(entries),
                    "problems": problems,
                    "ok": not problems,
                },
                indent=2,
            )
        )
    else:
        for problem in problems:
            print(f"FAIL {problem}")
        if problems:
            print(f"\n{len(problems)} problem(s)", file=sys.stderr)
        else:
            print(f"OK {len(entries)} partition(s) verified")

    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
