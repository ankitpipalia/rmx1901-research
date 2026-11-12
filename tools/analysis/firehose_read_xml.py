#!/usr/bin/env python3
"""Build and parse the Firehose `<read>` request used for raw readback.

The safe raw-read form has **no** `filename` attribute. With a filename the
programmer may write the data to a device-side file instead of streaming it
to the host. This tool builds the request, validates it, and parses
`<response>`/`<log>` lines. It is offline only.

Usage:
    python3 firehose_read_xml.py build --lun 1 --start-sector 0 --sectors 2048
    python3 firehose_read_xml.py validate --xml-file read.xml
    python3 firehose_read_xml.py parse --text-file responses.txt
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from dataclasses import dataclass

SECTOR_SIZE = 4096
_TAG_RE = re.compile(r"<(response|log)\b([^>]*?)/?>", re.IGNORECASE)
_ATTR_RE = re.compile(r'([A-Za-z_][\w.-]*)\s*=\s*"([^"]*)"')


class FirehoseError(ValueError):
    """Invalid Firehose read request or response text."""


@dataclass(frozen=True)
class Response:
    tag: str
    attrs: dict

    def to_dict(self) -> dict:
        return {"tag": self.tag, "attrs": self.attrs}


def build_read_xml(lun: int, start_sector: int, sectors: int,
                   sector_size: int = SECTOR_SIZE) -> str:
    if sector_size != SECTOR_SIZE:
        raise FirehoseError(f"sector size must be {SECTOR_SIZE} for this device")
    for name, value in (("lun", lun), ("start_sector", start_sector),
                        ("sectors", sectors)):
        if not isinstance(value, int) or value < 0:
            raise FirehoseError(f"{name} must be a non-negative integer")
    if sectors == 0:
        raise FirehoseError("sectors must be positive")
    return (
        '<read SECTOR_SIZE_IN_BYTES="%d" '
        'physical_partition_number="%d" '
        'start_sector="%d" '
        'num_partition_sectors="%d" />'
        % (sector_size, lun, start_sector, sectors)
    )


def validate_read_xml(text: str) -> dict:
    if not text.strip():
        raise FirehoseError("empty XML")
    if "<read" not in text:
        raise FirehoseError("no <read> element")
    if "filename" in text.lower():
        raise FirehoseError("read request must not carry a filename attribute")

    match = re.search(r"<read\b([^>]*?)/?>", text, re.IGNORECASE | re.DOTALL)
    if not match:
        raise FirehoseError("malformed <read> element")
    attrs = {k: v for k, v in _ATTR_RE.findall(match.group(1))}
    required = {
        "SECTOR_SIZE_IN_BYTES",
        "physical_partition_number",
        "start_sector",
        "num_partition_sectors",
    }
    missing = required - set(attrs)
    if missing:
        raise FirehoseError(f"missing attributes: {sorted(missing)}")
    try:
        sector_size = int(attrs["SECTOR_SIZE_IN_BYTES"])
        lun = int(attrs["physical_partition_number"])
        start = int(attrs["start_sector"])
        count = int(attrs["num_partition_sectors"])
    except ValueError as exc:
        raise FirehoseError(f"non-integer attribute: {exc}") from exc
    if sector_size != SECTOR_SIZE:
        raise FirehoseError(f"SECTOR_SIZE_IN_BYTES must be {SECTOR_SIZE}")
    if lun < 0 or start < 0 or count <= 0:
        raise FirehoseError("lun/start must be non-negative and count positive")
    return {
        "sector_size": sector_size,
        "lun": lun,
        "start_sector": start,
        "num_partition_sectors": count,
        "byte_length": count * sector_size,
    }


def parse_responses(text: str) -> list[Response]:
    out: list[Response] = []
    for match in _TAG_RE.finditer(text):
        tag = match.group(1).lower()
        attrs = {
            k: html.unescape(v) for k, v in _ATTR_RE.findall(match.group(2))
        }
        out.append(Response(tag=tag, attrs=attrs))
    return out


def cmd_build(args) -> int:
    xml = build_read_xml(args.lun, args.start_sector, args.sectors)
    if args.json:
        print(json.dumps({"xml": xml, **validate_read_xml(xml)}, indent=2))
    else:
        print(xml)
    return 0


def cmd_validate(args) -> int:
    text = (
        open(args.xml_file, encoding="utf-8").read()
        if args.xml_file
        else args.xml
    )
    info = validate_read_xml(text)
    if args.json:
        print(json.dumps(info, indent=2))
    else:
        print("valid read request")
        for key, value in info.items():
            print(f"  {key}: {value}")
    return 0


def cmd_parse(args) -> int:
    text = (
        open(args.text_file, encoding="utf-8").read()
        if args.text_file
        else args.text
    )
    responses = parse_responses(text)
    if args.json:
        print(json.dumps([r.to_dict() for r in responses], indent=2))
    else:
        for i, response in enumerate(responses):
            print(f"[{i}] <{response.tag}> {response.attrs}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="build a safe raw-read request")
    b.add_argument("--lun", type=int, required=True)
    b.add_argument("--start-sector", type=int, required=True)
    b.add_argument("--sectors", type=int, required=True)
    b.add_argument("--json", action="store_true")
    b.set_defaults(func=cmd_build)

    v = sub.add_parser("validate", help="validate a read request")
    v.add_argument("--xml-file")
    v.add_argument("--xml")
    v.add_argument("--json", action="store_true")
    v.set_defaults(func=cmd_validate)

    d = sub.add_parser("parse", help="parse response/log text")
    d.add_argument("--text-file")
    d.add_argument("--text")
    d.add_argument("--json", action="store_true")
    d.set_defaults(func=cmd_parse)

    args = p.parse_args(argv)
    if args.cmd == "validate" and not (args.xml_file or args.xml):
        print("error: provide --xml-file or --xml", file=sys.stderr)
        return 2
    if args.cmd == "parse" and not (args.text_file or args.text):
        print("error: provide --text-file or --text", file=sys.stderr)
        return 2
    try:
        return args.func(args)
    except (OSError, FirehoseError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
