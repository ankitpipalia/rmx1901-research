#!/usr/bin/env python3
"""Offline Firehose `<program>` geometry preflight.

Parses a Firehose XML, checks every `<program>` entry for:

  - required attributes and non-negative integers;
  - a file whose size is exactly sectors * 4096;
  - no overlap with another entry on the same LUN;
  - optional exact geometry match against a JSON manifest.

It does not write, erase, or open a device. It is a dry-run checker for a
restore XML you already have.

Usage:
    python3 preflight_geometry.py --xml restore.xml --dir images
    python3 preflight_geometry.py --xml restore.xml --dir images \
        --manifest c01.json --json
"""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, asdict
from pathlib import Path

SECTOR_SIZE = 4096


class PreflightError(ValueError):
    """The XML or manifest is malformed."""


@dataclass(frozen=True)
class ProgramEntry:
    label: str
    filename: str
    lun: int
    start: int
    sectors: int


def parse_programs(xml_path: Path) -> list[ProgramEntry]:
    try:
        tree = ET.parse(xml_path)
    except (OSError, ET.ParseError) as exc:
        raise PreflightError(f"cannot parse XML: {exc}") from exc

    entries: list[ProgramEntry] = []
    for elem in tree.getroot().iter("program"):
        required = [
            "label",
            "filename",
            "physical_partition_number",
            "start_sector",
            "num_partition_sectors",
        ]
        missing = [key for key in required if key not in elem.attrib]
        if missing:
            raise PreflightError(
                f"<program> missing attributes: {', '.join(missing)}"
            )
        try:
            lun = int(elem.attrib["physical_partition_number"], 0)
            start = int(elem.attrib["start_sector"], 0)
            sectors = int(elem.attrib["num_partition_sectors"], 0)
        except ValueError as exc:
            raise PreflightError(f"non-integer attribute: {exc}") from exc
        if lun < 0 or start < 0 or sectors <= 0:
            raise PreflightError(
                f"{elem.attrib['label']}: lun/start must be non-negative "
                "and sectors positive"
            )
        entries.append(
            ProgramEntry(
                label=elem.attrib["label"],
                filename=elem.attrib["filename"],
                lun=lun,
                start=start,
                sectors=sectors,
            )
        )
    if not entries:
        raise PreflightError("no <program> entries found")
    return entries


def load_manifest(path: Path) -> dict[str, dict]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PreflightError(f"cannot read manifest: {exc}") from exc
    partitions = raw.get("partitions") if isinstance(raw, dict) else None
    if not isinstance(partitions, list) or not partitions:
        raise PreflightError("manifest must contain a non-empty 'partitions' list")
    out: dict[str, dict] = {}
    for entry in partitions:
        if not isinstance(entry, dict):
            raise PreflightError("manifest partition is not an object")
        name = entry.get("name")
        if not isinstance(name, str) or not name:
            raise PreflightError("manifest partition missing name")
        if name in out:
            raise PreflightError(f"manifest duplicate name: {name}")
        out[name] = entry
    return out


def check(entries: list[ProgramEntry], base: Path,
          manifest: dict[str, dict] | None = None) -> list[str]:
    problems: list[str] = []
    by_lun: dict[int, list[ProgramEntry]] = {}

    for entry in entries:
        by_lun.setdefault(entry.lun, []).append(entry)
        path = base / entry.filename
        if not path.is_file():
            problems.append(f"{entry.label}: missing file {entry.filename}")
        else:
            expected = entry.sectors * SECTOR_SIZE
            actual = path.stat().st_size
            if actual != expected:
                problems.append(
                    f"{entry.label}: size {actual} != {entry.sectors} * "
                    f"{SECTOR_SIZE} = {expected}"
                )

        if manifest is not None:
            ref = manifest.get(entry.label)
            if ref is None:
                problems.append(f"{entry.label}: not in manifest")
            else:
                try:
                    want = (
                        int(ref["physical_partition_number"]),
                        int(ref["start_sector"]),
                        int(ref["num_partition_sectors"]),
                    )
                except (KeyError, TypeError, ValueError) as exc:
                    problems.append(f"{entry.label}: bad manifest entry: {exc}")
                else:
                    have = (entry.lun, entry.start, entry.sectors)
                    if have != want:
                        problems.append(
                            f"{entry.label}: geometry {have} != manifest {want}"
                        )

    for lun, group in sorted(by_lun.items()):
        ordered = sorted(group, key=lambda e: e.start)
        for prev, cur in zip(ordered, ordered[1:]):
            if cur.start < prev.start + prev.sectors:
                problems.append(
                    f"LUN{lun}: {cur.label} [0x{cur.start:x}+0x{cur.sectors:x}] "
                    f"overlaps {prev.label} [0x{prev.start:x}+0x{prev.sectors:x}]"
                )

    return problems


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--xml", required=True, type=Path)
    p.add_argument("--dir", required=True, type=Path,
                   help="directory containing the program files")
    p.add_argument("--manifest", type=Path,
                   help="optional JSON manifest with exact geometry")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)

    try:
        entries = parse_programs(args.xml)
        manifest = load_manifest(args.manifest) if args.manifest else None
    except PreflightError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    problems = check(entries, args.dir, manifest)
    if args.json:
        print(
            json.dumps(
                {
                    "entries": [asdict(e) for e in entries],
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
            print(f"OK {len(entries)} program entries, no overlap, sizes match")

    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
