import contextlib
import io
import unittest

from tools.analysis import sahara_frames as sf


class SaharaFrameTests(unittest.TestCase):
    def test_roundtrip(self):
        frame = sf.encode(0x02, b"\x00" * 40)
        self.assertEqual(len(frame), 48)
        decoded = sf.decode(frame)
        self.assertEqual(decoded.command, 0x02)
        self.assertEqual(decoded.length, 48)
        self.assertEqual(decoded.payload, b"\x00" * 40)

    def test_empty_payload(self):
        frame = sf.encode(0x07)
        self.assertEqual(frame, b"\x07\x00\x00\x00\x08\x00\x00\x00")
        decoded = sf.decode(frame)
        self.assertEqual(decoded.payload, b"")

    def test_split_stream(self):
        stream = sf.encode(1, b"abc") + sf.encode(2, b"de")
        frames, remainder = sf.split_stream(stream)
        self.assertEqual([f.command for f in frames], [1, 2])
        self.assertEqual(remainder, b"")

    def test_incomplete_remainder(self):
        stream = sf.encode(1, b"abc") + b"\x02\x00\x00\x00"
        frames, remainder = sf.split_stream(stream)
        self.assertEqual(len(frames), 1)
        self.assertEqual(remainder, b"\x02\x00\x00\x00")

    def test_bad_length(self):
        with self.assertRaises(sf.SaharaError):
            sf.decode(b"\x01\x00\x00\x00\x04\x00\x00\x00")

    def test_truncated(self):
        with self.assertRaises(sf.SaharaError):
            sf.decode(b"\x01\x00\x00\x00\x10\x00\x00\x00abc")

    def test_cli_frame(self):
        with contextlib.redirect_stdout(io.StringIO()):
            rc = sf.main(["frame", "--command", "2", "--payload-hex", "0011"])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
