import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from tools.validation import preflight_geometry as pg
from tools.validation import readback_manifest as rm


def write_manifest(path: Path, entries: list[dict]) -> None:
    path.write_text(json.dumps({"partitions": entries}), encoding="utf-8")


class ReadbackManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "xbl.img").write_bytes(b"A" * 4096)
        (self.root / "abl.img").write_bytes(b"B" * 4096)
        self.entries = [
            {
                "name": "xbl",
                "file": "xbl.img",
                "size": 4096,
                "sha256": hashlib.sha256(b"A" * 4096).hexdigest(),
            },
            {
                "name": "abl",
                "file": "abl.img",
                "size": 4096,
                "sha256": hashlib.sha256(b"B" * 4096).hexdigest(),
            },
        ]
        self.manifest = self.root / "manifest.json"
        write_manifest(self.manifest, self.entries)

    def tearDown(self):
        self.tmp.cleanup()

    def test_pass(self):
        entries = rm.load_manifest(self.manifest)
        self.assertEqual(rm.verify(self.root, entries), [])

    def test_hash_mismatch(self):
        (self.root / "xbl.img").write_bytes(b"C" * 4096)
        entries = rm.load_manifest(self.manifest)
        problems = rm.verify(self.root, entries)
        self.assertTrue(any("sha256" in p for p in problems))

    def test_size_mismatch(self):
        (self.root / "abl.img").write_bytes(b"B" * 4095)
        entries = rm.load_manifest(self.manifest)
        problems = rm.verify(self.root, entries)
        self.assertTrue(any("size" in p for p in problems))

    def test_missing(self):
        (self.root / "xbl.img").unlink()
        entries = rm.load_manifest(self.manifest)
        problems = rm.verify(self.root, entries)
        self.assertTrue(any("missing" in p for p in problems))

    def test_duplicate(self):
        entries = rm.load_manifest(self.manifest)
        entries.append(dict(entries[0]))
        problems = rm.verify(self.root, entries)
        self.assertTrue(any("duplicate" in p for p in problems))

    def test_strict_extra(self):
        (self.root / "notes.txt").write_text("extra")
        entries = rm.load_manifest(self.manifest)
        problems = rm.verify(self.root, entries, strict_extra=True)
        self.assertTrue(any("unexpected" in p for p in problems))

    def test_cli_pass(self):
        with contextlib.redirect_stdout(io.StringIO()):
            rc = rm.main(["--dir", str(self.root), "--manifest", str(self.manifest)])
        self.assertEqual(rc, 0)


class PreflightGeometryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "xbl.img").write_bytes(b"X" * 4096)
        (self.root / "abl.img").write_bytes(b"A" * 4096)
        self.xml = self.root / "restore.xml"
        self.xml.write_text(
            "<data>"
            '<program label="xbl" filename="xbl.img" '
            'physical_partition_number="1" start_sector="0" '
            'num_partition_sectors="1" />'
            '<program label="abl" filename="abl.img" '
            'physical_partition_number="4" start_sector="0" '
            'num_partition_sectors="1" />'
            "</data>",
            encoding="utf-8",
        )
        self.manifest = self.root / "manifest.json"
        write_manifest(
            self.manifest,
            [
                {
                    "name": "xbl",
                    "physical_partition_number": 1,
                    "start_sector": 0,
                    "num_partition_sectors": 1,
                },
                {
                    "name": "abl",
                    "physical_partition_number": 4,
                    "start_sector": 0,
                    "num_partition_sectors": 1,
                },
            ],
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_pass(self):
        entries = pg.parse_programs(self.xml)
        manifest = pg.load_manifest(self.manifest)
        self.assertEqual(pg.check(entries, self.root, manifest), [])

    def test_overlap(self):
        self.xml.write_text(
            "<data>"
            '<program label="a" filename="xbl.img" '
            'physical_partition_number="1" start_sector="0" '
            'num_partition_sectors="1" />'
            '<program label="b" filename="abl.img" '
            'physical_partition_number="1" start_sector="0" '
            'num_partition_sectors="1" />'
            "</data>",
            encoding="utf-8",
        )
        entries = pg.parse_programs(self.xml)
        problems = pg.check(entries, self.root)
        self.assertTrue(any("overlaps" in p for p in problems))

    def test_size_mismatch(self):
        (self.root / "xbl.img").write_bytes(b"X" * 4095)
        entries = pg.parse_programs(self.xml)
        problems = pg.check(entries, self.root)
        self.assertTrue(any("size" in p for p in problems))

    def test_manifest_mismatch(self):
        manifest = pg.load_manifest(self.manifest)
        manifest["xbl"]["start_sector"] = 99
        entries = pg.parse_programs(self.xml)
        problems = pg.check(entries, self.root, manifest)
        self.assertTrue(any("geometry" in p for p in problems))

    def test_cli_pass(self):
        with contextlib.redirect_stdout(io.StringIO()):
            rc = pg.main(
                [
                    "--xml",
                    str(self.xml),
                    "--dir",
                    str(self.root),
                    "--manifest",
                    str(self.manifest),
                ]
            )
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
