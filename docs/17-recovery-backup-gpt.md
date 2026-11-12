# 17 — Backup, GPT identity and recovery

**Result:** the C.01 boot chain was backed up as a verified 24-image set,
the six live GPTs were read and hashed, and the recovery procedures were
tested. The identity/NV backups exist but are **not** published. The restore
XML is geometry-verified but not end-to-end tested.

| Item | Value |
|---|---|
| Boot-chain set | 24 zero-padded, partition-sized images |
| Offline verifier | 96 checks, PASS |
| GPTs | 6 LUNs, hashed and matched |
| Identity/NV backup | Private; hashes only |
| Cold-power-cycle recovery | Validated |
| Restore XML | Draft, untested end-to-end |

---

## 1. What was backed up

### C.01 boot-chain set

A set of 24 zero-padded, partition-sized images extracted from the
decrypted C.01 OTA, plus:

- an inventory manifest with live state, layout evidence, and hashes;
- `SHA256SUMS.txt` for the images;
- an offline verifier (`verify_set.py`, 96 checks, PASS);
- draft Firehose restore XMLs for 18 boot-chain partitions and 18 + 6
  firmware images;
- live identity/NV/secure-partition notes;
- a live GPT verification note;
- a read-only dump checklist for gaps.

The live `abl`, `xbl`, and `vbmeta` dumps equal the decrypted OTA bytes plus
zero padding; the prefixes are identical. These are the images the phone is
running, not reconstructions.

### Identity / NV / secure dumps

A separate private set contains the partitions that must never be published:

```text
cdt, devinfo, frp, fsc, fsg, keystore, misc_before/after,
modemst1/2, oppo_sec, oppodycnvbk, opporeserve1/2/3,
oppostanvbk, persist_before/after, recovery, ...
```

Plus `carrier, ddr, dip, dpo, hypbak, limits, sec, spunvm, ssd, sti,
toolsfv, ...`.

The `*.sha256` files are the integrity reference. `misc_before ==
misc_after` and `persist_before == persist_after` by SHA-256; the token
experiments did not change those partitions.

### A.20 / A.05 reference sets

An A.20 62-partition backup (9.06 GB) and A.05 extracted images are kept as
reference. They are **not** interchangeable with C.01: the A.20 backup is a
newer ABL build than the live C.01 ABL, so it is not a downgrade target, and
the device-specific partitions (`devinfo`, `frp`, `persist`, `modemst*`,
`fsg`, `fsc`, `opporeserve*`, boot chain) must not be crossed between
builds.

## 2. Verified GPTs

The six live GPTs were read with the runtime-root shell and are
byte-identical to the pre-C.01 capture used by the restore XML:

| LUN | SHA-256 |
|---:|---|
| 0 | `5edfc06bf86c935664dcd0b0215b5df1faf1679b6b5c3b2d57d8efcbddf2fbc3` |
| 1 | `f3d4a6f83f1d1e734178c9c2940d8276a5582c7c8aa0ac02452c7177d37b4e07` |
| 2 | `9806a84e1831157aad8937f21527225d393592206588e4d7a3ac45b350fdf3d3` |
| 3 | `3717b0ef49a4046ba4265513c30eef17dafcb0c9600dd7fde8fedb2fba7ff34c` |
| 4 | `fc4610ceacf78158e458f5299b3973fd0e08ed350693081590a6de6a7757fc78` |
| 5 | `a54132455825116f21837266591a53c90e009965f6fe87b663d7870ecb97ffad` |

These are integrity references, not backups. Do not re-GPT, re-layout, or
erase LUNs as a recovery shortcut. The LUN 0 erase during the VIP probe
([11](11-firehose-vip-audit.md)) is the cautionary example.

## 3. Recovery procedures

### Android is up

```bash
adb devices
adb reboot edl
```

Wait for 9008:

```bash
qdl list
# 05c6:9008
```

### EDL, PBL is healthy

Run the signed-programmer control from the companion repository:

```bash
python3 pblexp_macos.py all --transport usb \
  --resources <resources-dir> \
  --image <signed-programmer> \
  --xml none --serve-settle 0 --serve-drain 0.5 --total-timeout 60
```

Expected:

```text
181 READ_DATA64 requests
END_IMAGE_TX status=0
DONE_RESP status=1
```

### Running signed programmer → EDL

```bash
python3 firehose_power.py reset_to_edl
```

`reset_to_edl` returns ACK and re-enumerates 9008 while a programmer is
running. `reset` boots the normal system; `off` powers down and needs a
physical power-on.

### PBL is hung / no HELLO

A PBL stuck in `END_IMAGE_TX status 1` (or in an oracle loop) refuses a
Sahara reset:

```text
qdl reset -> SAHARA: device rejected the reset request: end-of-image status 0x1
```

Recovery is a **full cold power cycle**: hold Power ~10 s to force off, then
power on. USB replug/PnP is not sufficient. There is no host-side reset for
a wedged bare PBL.

### Cold boot and re-enter EDL

```bash
adb devices
adb reboot edl
qdl list
```

## 4. Restore path

Draft restore XMLs exist for the C.01 boot chain. Before any real restore:

1. verify the set offline (`verify_set.py`; 96 checks, PASS);
2. confirm the signed programmer loads and the Firehose transport works;
3. confirm the target partition names and geometry against the live GPT;
4. have a cold-power-cycle recovery available;
5. do not restore A.20/A.05 device-specific partitions onto C.01.

The XML is geometry-verified but **not** tested end-to-end. A failed
XBL/ABL write can bootloop the phone; the signed programmer path is
independent of the boot chain, so EDL recovery should remain available, but
that claim must be verified before the first boot-partition write.

## 5. Known gaps

- `system`, `vendor`, `odm`, `cache`, `userdata`, `vm-*`, `logdump`,
  `logfs`, `rawdump`: firmware/user/log data, covered by the OTA/userdata
  restore, not a full image backup.
- Live `modem` (144 MiB): the matching C.01 OTA `modem.img` is the firmware;
  live NV/calibration is in `modemst1/2`, `fsg`, `fsc`.
- `ALIGN_TO_128K_1/2`: alignment gaps, intentionally not captured.
- No OPPO/Realme signing key and no vendor unlock token.

## 6. Recovery checklist

- [ ] Phone is owned; C.01 backup intact.
- [ ] Signed programmer control passes (181 READ_DATA, DONE 1).
- [ ] Firehose `reset_to_edl` ACK and 9008 re-enumeration.
- [ ] Cold-power-cycle procedure known.
- [ ] No boot-chain/GPT/RPMB write until a restore has been tested.
- [ ] After any failed auth test: cold boot, confirm HELLO, then continue.

No partition/GPT/RPMB write was made for the runtime-root or Nightzuku work.
Boot-chain writes were limited to the documented Test A/B0 experiments and
the K3 cross-flash; stock C.01 was restored.

## 7. What is published vs withheld

| Item | Status |
|---|---|
| GPT hashes | Published (integrity reference) |
| Recovery procedures | Published |
| Backup inventory | Published at category level |
| Identity/NV dumps | Withheld |
| Boot-chain images | Withheld |
| Restore XML | Withheld |
| Signing keys / tokens | Not available |

## 8. Limits

- The restore XML is not end-to-end tested.
- The identity/NV backup is only as good as the readback that produced it;
  the readback gate was verified for three partitions, not the whole device.
- GPT hashes identify the layout, not the contents.
- Recovery depends on a healthy PBL and a working programmer; neither is
  guaranteed after a bad boot-chain write.

## 9. References

- EDL readback and restore: [16](16-edl-readback-and-restore.md)
- Firehose/VIP: [11](11-firehose-vip-audit.md)
- OTA extraction: [15](15-ota-ozip-extraction.md)
- Companion tooling: <https://github.com/ankitpipalia/pblexp-macos>
