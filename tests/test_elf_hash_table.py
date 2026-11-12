import contextlib
import hashlib
import io
import struct
import tempfile
import unittest
from pathlib import Path

from tools.analysis import elf_hash_table as eht


def build_elf(path: Path) -> bytes:
    header = bytearray(64)
    header[0:4] = b"\x7fELF"
    header[4] = 2  # ELFCLASS64
    header[5] = 1  # little-endian
    header[6] = 1  # EV_CURRENT
    struct.pack_into("<H", header, 0x34, 64)  # e_ehsize
    struct.pack_into("<Q", header, 0x20, 64)  # e_phoff
    struct.pack_into("<H", header, 0x36, 56)  # e_phentsize
    struct.pack_into("<H", header, 0x38, 3)  # e_phnum

    phdrs = bytearray()
    segs = [
        (1, 5, 232, 0x1000, 0x1000, 16, 16, 0x1000),
        (1, 6, 248, 0x2000, 0x2000, 8, 8, 0x1000),
        (1, 4, 256, 0x3000, 0x3000, 0, 0, 0x1000),
    ]
    for seg in segs:
        phdrs += struct.pack("<IIQQQQQQ", *seg)

    body = bytearray()
    body += header
    body += phdrs
    body += b"0123456789abcdef"  # seg0
    body += b"ABCDEFGH"          # seg1
    if len(body) > 300:
        raise AssertionError("fixture layout overflow")
    body += b"\x00" * (300 - len(body))

    table = [
        hashlib.sha256(bytes(header)).digest(),
        b"\x00" * 32,
        hashlib.sha256(b"0123456789abcdef").digest(),
        hashlib.sha256(b"ABCDEFGH").digest(),
        hashlib.sha256(b"").digest(),
    ]
    body += b"".join(table)
    path.write_bytes(bytes(body))
    return bytes(body)


class ElfHashTableTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "fixture.elf"
        self.data = build_elf(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_report(self):
        info = eht.parse_elf64(self.data, self.path)
        self.assertEqual(info.e_phnum, 3)
        self.assertEqual(len(info.segments), 3)
        self.assertEqual(
            info.header_sha256,
            hashlib.sha256(self.data[:64]).hexdigest(),
        )
        self.assertEqual(
            info.segments[0].sha256,
            hashlib.sha256(b"0123456789abcdef").hexdigest(),
        )

    def test_expected_table(self):
        info = eht.parse_elf64(self.data, self.path)
        table = eht.expected_table(info)
        self.assertEqual(len(table), 5)
        self.assertEqual(table[1], b"\x00" * 32)

    def test_verify_pass(self):
        info = eht.parse_elf64(self.data, self.path)
        results = eht.verify(self.data, info, 300)
        self.assertTrue(all(row["ok"] for row in results))

    def test_verify_tamper_fails(self):
        info = eht.parse_elf64(self.data, self.path)
        tampered = bytearray(self.data)
        tampered[300 + 3 * 32] ^= 0xFF
        results = eht.verify(bytes(tampered), info, 300)
        self.assertEqual([row["ok"] for row in results], [True, True, True, False, True])

    def test_bad_magic(self):
        with self.assertRaises(eht.ElfError):
            eht.parse_elf64(b"NOPE" + b"\x00" * 60)

    def test_table_out_of_bounds(self):
        info = eht.parse_elf64(self.data, self.path)
        with self.assertRaises(eht.ElfError):
            eht.verify(self.data, info, len(self.data) - 16)

    def test_cli_verify(self):
        with contextlib.redirect_stdout(io.StringIO()):
            rc = eht.main(["verify", "--elf", str(self.path), "--table-offset", "300"])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
