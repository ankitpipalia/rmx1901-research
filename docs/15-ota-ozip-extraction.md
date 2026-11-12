# 15 — OPPO OTA / `.ozip` extraction

**Result:** C.01 and K3 `.ozip` OTA packages were decrypted, converted to
raw partition images, and verified against the live device. The extracted
images were used for analysis and recovery. **No firmware, OTA package, or
extracted image is published.**

| Item | Value |
|---|---|
| Inputs | Realme X C.01 OTA, OPPO K3 C.13 OTA |
| Tools | `oppo_ozip_decrypt`, `sdat2img`, AOSP `avbtool` |
| Outputs | system/vendor/boot and a C.01 boot-chain set |
| Verification | GPT geometry, SHA-256, AVB, live-partition comparison |
| Published | Method and credits only |

---

## 1. Why extract OTA images

OTA extraction supplied three things the work needed:

1. **Reference images** for static analysis (ABL, XBL, vbmeta, keymaster,
   TZ, modem).
2. **A recovery set** for the C.01 boot chain, so a failed experiment could
   be restored without a full firmware download.
3. **A comparison basis** for the live partitions, to confirm that a
   readback matched the shipped image.

The OTA packages are vendor firmware. They are not redistributable, and
they contain proprietary code and device-specific data.

## 2. The `.ozip` format, at a high level

An OPPO `.ozip` is an encrypted archive. The public `oppo_ozip_decrypt`
tool implements the container handling and key selection. The output is a
zip-like payload containing:

- `system.new.dat`, `system.transfer.list` (and vendor/product variants);
- `boot.img`, `dtbo.img`, `vbmeta.img`;
- firmware images for the boot chain and modem.

The exact key material and container details are part of the upstream tool,
not this repository. No key or OTA is published here.

## 3. Conversion pipeline

```text
.ozip
  -> oppo_ozip_decrypt
     -> zip payload
        -> sdat2img (system/vendor/product)
        -> raw boot/dtbo/vbmeta/firmware images
           -> avbtool verify_image (where applicable)
           -> SHA-256 + GPT geometry check
```

`sdat2img` converts the Android sparse `.new.dat` + `.transfer.list` pair
into a raw image. `avbtool` verifies the AVB footer and descriptor on images
that carry one.

For the C.01 boot-chain set, each image was zero-padded to its partition
size so the Firehose restore XML could use exact sector counts. The set
covers 24 partitions; the restore XML drafts cover 18 boot-chain partitions
and 18 + 6 firmware images.

## 4. Verification

The extracted set was checked in four ways:

1. **Geometry.** Each image's size and sector count were compared with the
   live GPT.
2. **Hashes.** `SHA256SUMS.txt` covers the extracted images; the offline
   verifier runs 96 checks and passes.
3. **AVB.** `avbtool` verified the vbmeta/boot images that carry AVB
   metadata.
4. **Live comparison.** The live `abl`, `xbl`, and `vbmeta` dumps equal the
   decrypted OTA bytes plus zero padding; the prefixes are identical. These
   are the images the phone is running, not reconstructions.

The live comparison is the strongest check: it ties the extracted image to
the bytes on the device.

## 5. What was produced

| Artifact | Purpose | Published? |
|---|---|---|
| C.01 boot-chain image set | Recovery and analysis | No |
| C.01 restore XML drafts | Firehose restore | No (procedure described in [16](16-edl-readback-and-restore.md)) |
| K3 C.13 system/vendor/boot | Compatibility experiment | No |
| Extracted ABL/XBL/keymaster/TZ | Static analysis | No |
| Hash manifest | Integrity reference | Hashes only, in [evidence/hashes.md](../evidence/hashes.md) |

## 6. Licensing and attribution

| Tool | License | Use |
|---|---|---|
| `oppo_ozip_decrypt` / `oppo_decrypt` | Custom attribution (“share/modify, refer original author”) | Decryption; not vendored |
| `sdat2img` | MIT | Sparse image conversion; not vendored |
| AOSP `avbtool` | Apache-2.0 | AVB verification; not vendored |

The tools are linked and credited, not copied into this MIT/CC-BY
repository. See [THIRD-PARTY-LICENSES](../references/THIRD-PARTY-LICENSES.md).

## 7. Why no firmware is published

- Vendor firmware is not licensed for redistribution.
- It is large and device-specific.
- It contains proprietary code and, in some partitions, identity/NV data.
- Publishing it would create a flashing resource that could be used on
  third-party devices.

The research value is in the **method and the verification**, not in the
bytes.

## 8. Limits

- The extraction pipeline is build-specific; a different OTA may use a
  different container version.
- `oppo_ozip_decrypt` is a third-party tool; its correctness and licensing
  are its authors' responsibility.
- AVB verification does not prove the image is the one the device will
  accept; the bootloader has its own trust chain.
- The C.01 restore XML is geometry-verified but not end-to-end tested
  ([16](16-edl-readback-and-restore.md)).

## 9. References

- `oppo_ozip_decrypt` / `oppo_decrypt` (upstream; attribution license).
- `sdat2img` (MIT).
- AOSP `avbtool` (Apache-2.0).
- Recovery and restore: [16](16-edl-readback-and-restore.md),
  [17](17-recovery-backup-gpt.md).
- Upstream credits: [UPSTREAM-CREDITS](../references/UPSTREAM-CREDITS.md).
