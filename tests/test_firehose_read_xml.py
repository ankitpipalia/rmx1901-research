import contextlib
import io
import unittest

from tools.analysis import firehose_read_xml as fx


class FirehoseReadXmlTests(unittest.TestCase):
    def test_build_contains_no_filename(self):
        xml = fx.build_read_xml(1, 0, 2048)
        self.assertNotIn("filename", xml.lower())
        self.assertIn('physical_partition_number="1"', xml)
        self.assertIn('num_partition_sectors="2048"', xml)

    def test_validate(self):
        xml = fx.build_read_xml(4, 16, 32)
        info = fx.validate_read_xml(xml)
        self.assertEqual(info["lun"], 4)
        self.assertEqual(info["start_sector"], 16)
        self.assertEqual(info["byte_length"], 32 * 4096)

    def test_reject_filename(self):
        xml = fx.build_read_xml(1, 0, 1).replace(
            "/>", 'filename="x.bin" />'
        )
        with self.assertRaises(fx.FirehoseError):
            fx.validate_read_xml(xml)

    def test_reject_wrong_sector_size(self):
        with self.assertRaises(fx.FirehoseError):
            fx.build_read_xml(1, 0, 1, sector_size=512)

    def test_reject_zero_sectors(self):
        with self.assertRaises(fx.FirehoseError):
            fx.build_read_xml(1, 0, 0)

    def test_parse_responses(self):
        text = (
            '<response value="ACK" rawmode="true" />\n'
            '<log value="Read 4096 bytes" />\n'
            '<response value="ACK" />\n'
        )
        responses = fx.parse_responses(text)
        self.assertEqual(len(responses), 3)
        self.assertEqual(responses[0].tag, "response")
        self.assertEqual(responses[0].attrs["rawmode"], "true")
        self.assertEqual(responses[1].tag, "log")

    def test_cli_build(self):
        with contextlib.redirect_stdout(io.StringIO()):
            rc = fx.main(["build", "--lun", "1", "--start-sector", "0", "--sectors", "8"])
        self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
