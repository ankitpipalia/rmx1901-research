#!/usr/bin/env python3
"""Sahara packet framing helper.

Sahara uses an 8-byte header: a 32-bit command and a 32-bit length. The
length includes the 8-byte header. This tool encodes, decodes, and splits
that framing. It does not know command semantics and does not touch a
device; command names are intentionally not guessed.

Usage:
    python3 sahara_frames.py frame --command 0x02 --payload-hex 00...
    python3 sahara_frames.py parse --hex 0200000030000000...
    python3 sahara_frames.py stream --hex ...
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from dataclasses import dataclass, asdict

HEADER = struct.Struct("<II")
HEADER_SIZE = HEADER.size


class SaharaError(ValueError):
    """Malformed or incomplete Sahara framing."""


@dataclass(frozen=True)
class Frame:
    command: int
    payload: bytes
    consumed: int

    @property
    def length(self) -> int:
        return HEADER_SIZE + len(self.payload)

    def to_dict(self) -> dict:
        return {
            "command": self.command,
            "command_hex": f"0x{self.command:08x}",
            "length": self.length,
            "payload_length": len(self.payload),
            "payload_hex": self.payload.hex(),
            "consumed": self.consumed,
        }


def encode(command: int, payload: bytes = b"") -> bytes:
    if not 0 <= command <= 0xFFFFFFFF:
        raise SaharaError("command must fit in 32 bits")
    if len(payload) + HEADER_SIZE > 0xFFFFFFFF:
        raise SaharaError("payload is too large")
    return HEADER.pack(command, HEADER_SIZE + len(payload)) + payload


def decode(data: bytes) -> Frame:
    if len(data) < HEADER_SIZE:
        raise SaharaError(f"need at least {HEADER_SIZE} bytes, got {len(data)}")
    command, length = HEADER.unpack_from(data, 0)
    if length < HEADER_SIZE:
        raise SaharaError(f"length {length} is smaller than the header")
    if length > len(data):
        raise SaharaError(
            f"frame claims {length} bytes but only {len(data)} are available"
        )
    payload = data[HEADER_SIZE:length]
    return Frame(command=command, payload=payload, consumed=length)


def split_stream(data: bytes) -> tuple[list[Frame], bytes]:
    """Decode as many complete frames as possible; return frames, remainder."""
    frames: list[Frame] = []
    pos = 0
    while pos < len(data):
        remaining = data[pos:]
        if len(remaining) < HEADER_SIZE:
            break
        _command, length = HEADER.unpack_from(remaining, 0)
        if length < HEADER_SIZE:
            raise SaharaError(
                f"invalid length {length} at stream offset 0x{pos:x}"
            )
        if len(remaining) < length:
            break
        frames.append(decode(remaining))
        pos += length
    return frames, data[pos:]


def _parse_hex(text: str) -> bytes:
    cleaned = "".join(text.split()).replace("0x", "").replace("0X", "")
    if len(cleaned) % 2:
        raise SaharaError("hex input has an odd number of digits")
    try:
        return bytes.fromhex(cleaned)
    except ValueError as exc:
        raise SaharaError(f"invalid hex: {exc}") from exc


def cmd_frame(args) -> int:
    payload = _parse_hex(args.payload_hex) if args.payload_hex else b""
    frame = encode(args.command, payload)
    if args.json:
        print(json.dumps({"hex": frame.hex(), "length": len(frame)}, indent=2))
    else:
        print(frame.hex())
    return 0


def cmd_parse(args) -> int:
    data = _parse_hex(args.hex)
    frame = decode(data)
    extra = len(data) - frame.consumed
    out = frame.to_dict()
    out["trailing_bytes"] = extra
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"command: 0x{frame.command:08x}")
        print(f"length:  {frame.length}")
        print(f"payload: {len(frame.payload)} bytes")
        print(f"hex:     {frame.payload.hex()}")
        print(f"trailing:{extra} bytes")
    return 0


def cmd_stream(args) -> int:
    data = _parse_hex(args.hex)
    frames, remainder = split_stream(data)
    if args.json:
        print(
            json.dumps(
                {
                    "frames": [f.to_dict() for f in frames],
                    "remainder_hex": remainder.hex(),
                    "remainder_length": len(remainder),
                },
                indent=2,
            )
        )
    else:
        for i, frame in enumerate(frames):
            print(
                f"[{i}] command=0x{frame.command:08x} "
                f"payload={len(frame.payload)} consumed={frame.consumed}"
            )
        print(f"remainder: {len(remainder)} bytes")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("frame", help="encode one frame")
    f.add_argument("--command", type=lambda s: int(s, 0), required=True)
    f.add_argument("--payload-hex", default="")
    f.add_argument("--json", action="store_true")
    f.set_defaults(func=cmd_frame)

    d = sub.add_parser("parse", help="decode one frame")
    d.add_argument("--hex", required=True)
    d.add_argument("--json", action="store_true")
    d.set_defaults(func=cmd_parse)

    s = sub.add_parser("stream", help="decode a byte stream")
    s.add_argument("--hex", required=True)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_stream)

    args = p.parse_args(argv)
    try:
        return args.func(args)
    except SaharaError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
