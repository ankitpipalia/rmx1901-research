#!/usr/bin/env python3
"""Offline ELF64 segment hash-table reporter and verifier.

This tool models the programmer hash table used in the PBL work:

    entry[0]      SHA-256 of the ELF header (e_ehsize bytes)
    entry[1]      zero (the hash segment itself is skipped)
    entry[2 + i]  SHA-256 of program header i's file segment

It never opens a device and never writes a file. It is a verification helper
for an image you already have.

Usage:
    python3 elf_hash_table.py report --elf image.elf
    python3 elf_hash_table.py verify --elf image.elf --table-offset 0x1028
    python3 elf_hash_table.py dump   --elf image.elf --table-offset 0x1028 --entries 22
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from dataclasses import dataclass
from pathlib import Path

ELF_MAGIC = b"\x7fELF"
ELFCLASS64 = 2
ELFDATA2LSB = 1
ZERO_DIGEST = b"\x00" * 32


class ElfError(ValueError):
    """The input is not a supported ELF64 little-endian image."""


@dataclass(frozen=True)
class Segment:
    index: int
    p_type: int
    p_flags: int
    p_offset: int
    p_vaddr: int
    p_paddr: int
    p_filesz: int
    p_memsz: int
    p_align: int
    sha256: str


@dataclass(frozen=True)
class ElfInfo:
    path: Path
    size: int
    e_ehsize: int
    e_phoff: int
    e_phentsize: int
    e_phnum: int
    header_sha256: str
    segments: tuple[Segment, ...]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_elf64(data: bytes, path: Path | None = None) -> ElfInfo:
    if len(data) < 64:
        raise ElfError("file is shorter than an ELF64 header")
    if data[:4] != ELF_MAGIC:
        raise ElfError("bad ELF magic")
    if data[4] != ELFCLASS64:
        raise ElfError(f"unsupported ELF class {data[4]} (need ELFCLASS64)")
    if data[5] != ELFDATA2LSB:
        raise ElfError(f"unsupported ELF data encoding {data[5]} (need little-endian)")

    e_ehsize = struct.unpack_from("<H", data, 0x34)[0]
    e_phoff = struct.unpack_from("<Q", data, 0x20)[0]
    e_phentsize = struct.unpack_from("<H", data, 0x36)[0]
    e_phnum = struct.unpack_from("<H", data, 0x38)[0]

    if e_ehsize < 64 or e_ehsize > len(data):
        raise ElfError(f"invalid e_ehsize {e_ehsize}")
    if e_phentsize < 56:
        raise ElfError(f"invalid e_phentsize {e_phentsize}")
    if e_phnum == 0:
        raise ElfError("ELF has no program headers")
    end = e_phoff + e_phnum * e_phentsize
    if e_phoff < e_ehsize or end > len(data):
        raise ElfError("program header table is outside the file")

    segments = []
    for i in range(e_phnum):
        off = e_phoff + i * e_phentsize
        (
            p_type,
            p_flags,
            p_offset,
            p_vaddr,
            p_paddr,
            p_filesz,
            p_memsz,
            p_align,
        ) = struct.unpack_from("<IIQQQQQQ", data, off)
        if p_offset + p_filesz > len(data):
            raise ElfError(
                f"segment {i} file range 0x{p_offset:x}+0x{p_filesz:x} "
                "exceeds the file"
            )
        segments.append(
            Segment(
                index=i,
                p_type=p_type,
                p_flags=p_flags,
                p_offset=p_offset,
                p_vaddr=p_vaddr,
                p_paddr=p_paddr,
                p_filesz=p_filesz,
                p_memsz=p_memsz,
                p_align=p_align,
                sha256=_sha256(data[p_offset : p_offset + p_filesz]),
            )
        )

    return ElfInfo(
        path=path or Path("<memory>"),
        size=len(data),
        e_ehsize=e_ehsize,
        e_phoff=e_phoff,
        e_phentsize=e_phentsize,
        e_phnum=e_phnum,
        header_sha256=_sha256(data[:e_ehsize]),
        segments=tuple(segments),
    )


def expected_table(info: ElfInfo) -> list[bytes]:
    """Return the expected 2 + N table: header, zero, then segment digests."""
    table = [bytes.fromhex(info.header_sha256), ZERO_DIGEST]
    table.extend(bytes.fromhex(seg.sha256) for seg in info.segments)
    return table


def read_table(data: bytes, offset: int, entries: int) -> list[bytes]:
    if entries <= 0:
        raise ElfError("entries must be positive")
    end = offset + entries * 32
    if offset < 0 or end > len(data):
        raise ElfError(
            f"hash table 0x{offset:x}+{entries * 32} exceeds the file"
        )
    return [data[offset + i * 32 : offset + (i + 1) * 32] for i in range(entries)]


def verify(data: bytes, info: ElfInfo, table_offset: int) -> list[dict]:
    expected = expected_table(info)
    actual = read_table(data, table_offset, len(expected))
    results = []
    for i, (want, got) in enumerate(zip(expected, actual)):
        results.append(
            {
                "index": i,
                "expected": want.hex(),
                "actual": got.hex(),
                "ok": want == got,
            }
        )
    return results


def _fmt_segment(seg: Segment) -> str:
    return (
        f"[{seg.index:2d}] type=0x{seg.p_type:x} flags=0x{seg.p_flags:x} "
        f"off=0x{seg.p_offset:08x} filesz=0x{seg.p_filesz:08x} "
        f"vaddr=0x{seg.p_vaddr:016x} sha256={seg.sha256}"
    )


def cmd_report(args) -> int:
    data = Path(args.elf).read_bytes()
    info = parse_elf64(data, Path(args.elf))
    if args.json:
        print(
            json.dumps(
                {
                    "path": str(info.path),
                    "size": info.size,
                    "e_ehsize": info.e_ehsize,
                    "e_phoff": info.e_phoff,
                    "e_phentsize": info.e_phentsize,
                    "e_phnum": info.e_phnum,
                    "header_sha256": info.header_sha256,
                    "segments": [
                        {
                            "index": s.index,
                            "p_type": s.p_type,
                            "p_flags": s.p_flags,
                            "p_offset": s.p_offset,
                            "p_vaddr": s.p_vaddr,
                            "p_paddr": s.p_paddr,
                            "p_filesz": s.p_filesz,
                            "p_memsz": s.p_memsz,
                            "p_align": s.p_align,
                            "sha256": s.sha256,
                        }
                        for s in info.segments
                    ],
                },
                indent=2,
            )
        )
        return 0
    print(f"file: {info.path}")
    print(f"size: {info.size} (0x{info.size:x})")
    print(f"header: {info.header_sha256}")
    for seg in info.segments:
        print(_fmt_segment(seg))
    return 0


def cmd_dump(args) -> int:
    data = Path(args.elf).read_bytes()
    info = parse_elf64(data, Path(args.elf))
    table = read_table(data, args.table_offset, args.entries)
    print(f"table at 0x{args.table_offset:x}, {args.entries} entries")
    for i, entry in enumerate(table):
        print(f"[{i:2d}] {entry.hex()}")
    print(f"segments in ELF: {info.e_phnum}; expected entries: {2 + info.e_phnum}")
    return 0


def cmd_verify(args) -> int:
    data = Path(args.elf).read_bytes()
    info = parse_elf64(data, Path(args.elf))
    results = verify(data, info, args.table_offset)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for row in results:
            mark = "OK  " if row["ok"] else "FAIL"
            print(f"{mark} [{row['index']:2d}] {row['actual']}")
            if not row["ok"]:
                print(f"         expected {row['expected']}")
    bad = [r for r in results if not r["ok"]]
    if bad:
        print(f"\n{len(bad)} mismatch(es)", file=sys.stderr)
        return 1
    print(f"\nall {len(results)} entries match")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("report", help="print header and per-segment SHA-256")
    r.add_argument("--elf", required=True)
    r.add_argument("--json", action="store_true")
    r.set_defaults(func=cmd_report)

    d = sub.add_parser("dump", help="dump a hash table")
    d.add_argument("--elf", required=True)
    d.add_argument("--table-offset", type=lambda s: int(s, 0), required=True)
    d.add_argument("--entries", type=int, required=True)
    d.set_defaults(func=cmd_dump)

    v = sub.add_parser("verify", help="verify a table against the ELF")
    v.add_argument("--elf", required=True)
    v.add_argument("--table-offset", type=lambda s: int(s, 0), required=True)
    v.add_argument("--json", action="store_true")
    v.set_defaults(func=cmd_verify)

    args = p.parse_args(argv)
    try:
        return args.func(args)
    except (OSError, ElfError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
