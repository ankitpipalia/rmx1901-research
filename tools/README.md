# Tools

Offline, read-only analysis and validation helpers. **No destructive runner
is published here.** The device transport and signed-programmer serve path
live in the companion repository
[`pblexp-macos`](https://github.com/ankitpipalia/pblexp-macos).

## Layout

```text
tools/
  analysis/
    elf_hash_table.py       ELF64 segment hashes and programmer-style table verify
    sahara_frames.py        Sahara 8-byte header framing
    firehose_read_xml.py    Safe <read> request build/validate, response parse
  validation/
    readback_manifest.py    Offline image size/hash manifest verifier
    preflight_geometry.py   Firehose <program> geometry/size/overlap preflight
tests/
  test_*.py                 Synthetic-fixture unit tests
```

## Why these are safe

- They read files and text; they do not open USB, serial, or block devices.
- They do not write, erase, flash, or patch anything.
- They fail closed: a malformed input returns a non-zero exit code.
- The Firehose read builder refuses a `filename` attribute, because that can
  change the programmer's behavior from “stream to host” to “write a
  device-side file”.

The destructive Firehose runner, the signed-programmer serve path, and the
boot-chain write scripts are **not** in this repository.

## Usage

### ELF hash table

```bash
python3 tools/analysis/elf_hash_table.py report --elf image.elf
python3 tools/analysis/elf_hash_table.py verify --elf image.elf \
  --table-offset 0x1028
```

The verify mode expects the programmer convention:

```text
entry[0]      SHA-256 of the ELF header
entry[1]      zero
entry[2 + i]  SHA-256 of program header i's file segment
```

It prints `OK`/`FAIL` per entry and exits 1 on any mismatch.

### Sahara framing

```bash
python3 tools/analysis/sahara_frames.py frame --command 0x02 \
  --payload-hex 0000000000000000
python3 tools/analysis/sahara_frames.py parse --hex 0200000030000000...
python3 tools/analysis/sahara_frames.py stream --hex ...
```

The tool does not assign semantics to command numbers. It frames and
deframes; the caller decides what a command means.

### Firehose read request

```bash
python3 tools/analysis/firehose_read_xml.py build --lun 1 \
  --start-sector 0 --sectors 2048
python3 tools/analysis/firehose_read_xml.py validate --xml-file read.xml
python3 tools/analysis/firehose_read_xml.py parse --text-file responses.txt
```

The built request has no `filename` attribute and uses a 4096-byte sector.

### Readback manifest

```bash
python3 tools/validation/readback_manifest.py --dir dumps \
  --manifest manifest.json
```

Manifest format:

```json
{
  "partitions": [
    {"name": "xbl", "file": "xbl.img", "size": 4096, "sha256": "..."}
  ]
}
```

A missing file, size mismatch, hash mismatch, or duplicate name fails the
check. `--strict-extra` also rejects files not listed in the manifest.

### Firehose geometry preflight

```bash
python3 tools/validation/preflight_geometry.py --xml restore.xml \
  --dir images --manifest c01.json
```

Checks required attributes, `size == sectors × 4096`, per-LUN overlap, and
optional exact geometry against a manifest. It does not contact a device.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

The tests use synthetic ELF files, synthetic Sahara frames, synthetic
Firehose XML, and temporary directories. No hardware is required.

## Limits

- The tools model the formats used in this research; they are not universal
  Qualcomm or OPPO parsers.
- `elf_hash_table.py` assumes the programmer table convention above. A
  different table layout needs a different tool.
- `preflight_geometry.py` validates the XML and the files, not the device's
  actual GPT. Pair it with a GPT manifest from the target.
- A successful preflight does not make a write safe. It only removes
  arithmetic and geometry mistakes.

## License

MIT. See [LICENSE](../LICENSE).
