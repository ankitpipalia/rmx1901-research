# 16 — EDL readback and restore

**Result:** a fail-closed, three-phase Firehose readback gate was built and
verified on hardware. It read `xbl`, `abl`, and `xbl_config` and produced
hashes byte-identical to the runtime-root dump. A restore XML set was
generated and geometry-verified, but **not** run end-to-end. The gate caught
real framing bugs that had produced a wrong hash earlier.

| Item | Value |
|---|---|
| Transport | Qualcomm 9008 `05c6:9008` |
| Protocol | Sahara handoff, then Firehose |
| Readback | three-phase, fail-closed |
| Verified partitions | `xbl`, `abl`, `xbl_config` |
| Restore XML | 18 boot-chain + 6 firmware images, untested |
| Destructive runners | Not published |

---

## 1. The 9008 transport

The device enumerates as Qualcomm HS-USB QDLoader 9008 (`05c6:9008`). On
macOS there is no `/dev/cu.*` tty for this interface; the host uses
PyUSB/libusb and claims interface 0. On Windows the same device appears as a
COM port, but the port is lost after the segment3 handoff.

The Sahara handoff and the signed-programmer serve path are implemented in
the companion repository
(<https://github.com/ankitpipalia/pblexp-macos>). The key transport rules:

- do not call `set_configuration()`;
- do not reset the device on open;
- claim interface 0 and clear halts;
- drain one pending HELLO before the first `Hello710`;
- drain one pending HELLO after the loader re-enumerates, before
  `LOADER_HELLO`.

Without the second drain, the host writes `LOADER_HELLO`, gets no
`READ_DATA`, and reports a timeout.

## 2. The readback gate

The gate is deliberately **read-only and fail-closed**. It verifies three
things:

1. **The device is the expected target.** The port must be a Qualcomm 9008
   device; the programmer must be the expected image; the control run must
   complete with `END_IMAGE_TX 0` and `DONE 1`.
2. **The read is framed correctly.** Firehose is a byte stream, not a
   packet stream. XML messages can be split across reads, several messages
   can arrive in one read, and the first raw-data bytes can arrive in the
   same read as the ACK. The gate buffers and frames all of that.
3. **The bytes match the expected hash.** A read that is short, long, or
   desynchronized is a failure, not a partial success.

### The `<read>` command must not carry a filename

The safe raw-read form is:

```xml
<read SECTOR_SIZE_IN_BYTES="4096"
      physical_partition_number="<lun>"
      start_sector="<start>"
      num_partition_sectors="<count>" />
```

With a `filename` attribute, the programmer may write the data to a
device-side file instead of streaming it to the host. The gate omits it.

### Three bugs that produced a wrong hash

An earlier readback reported `xbl = 4b5f64a1…`, which did not match the
runtime-root dump. The cause was host framing, not a bad partition:

1. a `filename` attribute, which changed the programmer's behavior;
2. an unconsumed final ACK, which shifted the next read;
3. no XML buffering, so a split `<response>` was parsed as raw data.

After the fix, the gate read `xbl`, `abl`, and `xbl_config` and got:

```text
xbl         fadc6410…   (matches root dump)
abl         9a57f700…   (matches root dump)
xbl_config  5a551955…   (matches root dump)
```

That is the hardware verification of the readback path. The old
`4b5f64a1…` was a host artifact and is withdrawn.

## 3. `power reset_to_edl`

While a programmer is running, Firehose `<power>` can reset the device:

```xml
<power value="reset_to_edl" />
```

It returns ACK and re-enumerates 9008. This is useful for returning to EDL
without a physical key sequence. It does **not** recover a PBL stuck in
`END_IMAGE_TX status 1`; a wedged bare PBL needs a full cold power cycle
(hold Power ~10 s, then power on). USB replug is not sufficient.

## 4. Preflight for writes

Before any write, a separate preflight gate checks:

- the port is a Qualcomm 9008 device;
- the required files exist and their SHA-256 values match;
- every `<program>` entry's file size equals
  `num_partition_sectors × 4096`;
- the geometry (LUN, start, sectors) matches the C.01 manifest;
- no two entries on the same LUN overlap;
- no stale `stop.flag` or `state.json` is present.

The preflight does not write. It exits non-zero on any failure.

The published tool in `tools/validation/` is an **offline** version of this
logic: it validates a directory of images and a geometry manifest without a
device. The device-side runner is not published, because a misconfigured
Firehose write can brick a device.

## 5. Restore set

The C.01 restore set covers 18 boot-chain partitions, with an extended set
of 18 + 6 firmware images:

```text
abl, xbl, xbl_config, boot, dtbo, vbmeta, vbmeta_system, vbmeta_vendor,
recovery, modem, dsp, hyp, tz, aop, aop_config, devcfg, featenabler,
qupfw, ...
```

The XML geometry is verified against the live GPT. The set is **not**
end-to-end tested: a failed XBL/ABL write can bootloop the phone, and the
signed-programmer path, while independent of the boot chain, must be
re-verified before the first boot-partition write.

The restore XML itself is not published. The procedure and the preflight
requirements are.

## 6. Recovery from the LUN 0 erase

The VIP probe erased LUN 0 (see [11](11-firehose-vip-audit.md)). Recovery
used:

- the C.01 OTA images for the affected partitions;
- the device's own C.01 state dumps for identity/NV partitions;
- a userdata format.

The GPTs were verified before and after. The device booted C.01. This was
the most serious operational incident in the work, and it is recorded as a
lesson: establish VIP state before sending any destructive command, and
never send an `erase` as a “probe”.

## 7. What is published vs withheld

| Item | Status |
|---|---|
| Readback framing logic and failure modes | Published (description + offline tool) |
| Signed-programmer control procedure | Published (companion repo) |
| Restore procedure and preflight checks | Published |
| Restore XML with exact partition list | Withheld |
| Device-side write runner | Withheld |
| Firmware images | Withheld |
| Signed/modified programmers | Withheld (hashes only) |

## 8. Limits

- The readback gate is verified for three partitions; a full-device readback
  was not performed.
- The restore XML is geometry-verified but not executed end-to-end.
- Firehose behavior can differ between programmer versions.
- A wedged PBL has no host-side reset; cold power cycle is the only
  recovery.

## 9. References

- Companion repository: <https://github.com/ankitpipalia/pblexp-macos>
- Firehose/VIP: [11](11-firehose-vip-audit.md)
- Backup/GPT: [17](17-recovery-backup-gpt.md)
- Offline validation tool: [tools/validation](../tools/README.md)
