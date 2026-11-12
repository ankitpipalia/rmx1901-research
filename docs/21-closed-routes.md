# 21 — Closed routes

This page records the routes that were investigated and **closed** for this
device/build, with the reason. A closed route here means “not applicable or
not reachable in this work”, not “impossible for all time”.

| Route | Verdict | Reason |
|---|---|---|
| `devinfo` two-byte unlock | Closed | ABL does not read the `devinfo` partition; unlock state is RPMB-backed |
| Keymaster `0x202/0x203` | Measured closed | Milestone SW fuse is blown; TA returns `-0xF` |
| Direct RPMB write | Closed | RPMB is TEE-owned; the HLOS path goes through the refused Keymaster state |
| NO_AVB / vbmeta rename | Not applicable | C.01 is VB2 compile-time; no `vbmeta`/`vbmeta_a` strings; no TWRP |
| GBL / `efisp` | Not applicable | Android 10 C.01 has no GBL or `efisp`; the technique targets newer ABL |
| ABL token via `opporeserve1` | Closed | 256-byte vendor signature checked by XBL/TEE; not mintable |
| Fastboot unlock writer | Closed | `0x57c0` returns 2; only the display menu reaches the writer |
| e=3 certificate attack | Not applicable | C.01 chain uses `e=65537` |
| MSM Download Tool / QFIL | Not used | Proprietary vendor tools; not needed and not redistributable |
| Engineering ABL | Unavailable | No signed engineering ABL was obtained |

---

## 1. `devinfo` is inert

The iQOO-style route writes two bytes in a 4 KiB `devinfo` partition and
expects the ABL to read it. On C.01:

- the ABL logs `VB: RWDeviceState: Succeed using rpmb!`;
- the unlock state is a `0x998`-byte blob written through
  `QCOM_VERIFIEDBOOT_PROTOCOL->VBRwDeviceState`, which persists in RPMB;
- the ABL PE has **no `devinfo` partition xref**.

A `dd` to `devinfo` is therefore a no-op. This was checked statically and
against the live log. It is device-specific: other ABLs do read `devinfo`,
which is why the public iQOO technique works there.

## 2. Keymaster / RPMB is measured closed

The read-only probe sent `READ_KM_DEVICE_STATE` (`0x202`) to `keymaster64`
from runtime root. It returned:

```text
rc=0
raw response at rsp+8: 0xfffffff1   (-0xF)
ION data buffer: all zero, no "ANDROID-BOOT!"
```

`-0xF` means the milestone SW fuse is blown. The TA refuses `0x202` (and
would refuse `0x203`) before touching the RPMB-backed device state.

The probe itself had three bugs that were fixed before the result was
trusted:

1. wrong ION heap — C.01 uses `ION_QSECOM_HEAP_ID = 27`, not a bit in
   0..15;
2. request/response outside the QSEECom shared buffer — they must lie
   inside `handle->sb_virt` with `sb_len` at `+8`;
3. 32-bit command wrapper for a 64-bit TA — `keymaster64` needs
   `QSEECom_send_modified_cmd_64`; the 32-bit wrapper is rejected with
   “QSEE app arch 0 is not supported”.

No `0x203` write was sent. The route is closed on this unit, not merely
assumed closed.

## 3. NO_AVB does not apply

The public NO_AVB technique renames or removes `vbmeta` so the ABL takes a
“no AVB” path, then uses the Keymaster TA to write device state. It requires:

- a runtime GPT `Is_VERIFIED_BOOT_2()` lookup;
- a bootable unsigned image (usually TWRP);
- a Keymaster TA that accepts `0x202/0x203` because the milestone was
  skipped.

C.01 fails all three:

- the ABL prints `AVB version 2` with an immediate `w2 = 2` at `0x5a08`, a
  compile-time `AVB_2`, not a runtime GPT check;
- there are no `vbmeta`/`vbmeta_a` strings in the C.01 ABL path;
- no TWRP exists for this device;
- the milestone fuse is already blown, so the TA refuses the state commands.

The GPT-rename trick is not universal. On C.01 it does nothing useful.

## 4. GBL / `efisp` does not apply

The 2026-era GBL/efisp technique targets newer ABL builds that load an
unsigned GBL UEFI application. C.01 is Android 10 and has no GBL or `efisp`
partition. The technique is not applicable to this build.

## 5. The ABL token cannot be minted

The Deep Testing route is described in [13](13-deeptest-token-flow.md). The
short version:

- the server rejects RMX1901 with `-1002`;
- the 316-byte blob has a 256-byte vendor signature;
- root can write the slot but cannot produce the signature;
- a serial-only block passes the ABL serial check and is rejected by
  XBL/TEE with `VBVerifyFastbootUnlockVerify : verify fail` / `0x50`.

This is a cryptographic gate, not a missing byte.

## 6. The Fastboot unlock writer is dead

`FUN_000057c0` is:

```text
mov w0, #2
ret
```

The writer `FUN_00025d50(0,1)` is reached only when this returns 3. It
returns 2. The `flashing unlock` handler therefore falls into the display
Unlock/Lock menu, which needs an enabled display and physical key presses.
This is not a headless route.

## 7. e=3 is not present

The C.01 certificate chain uses `e=65537` throughout. The short-exponent
RSA attack does not apply. This was checked on the certificates in the
programmer and the XBL chain.

## 8. RPMB is not directly writable from HLOS

RPMB is owned by the TEE. The HLOS path is the Keymaster state command,
which is refused (`-0xF`). A direct RPMB write from Android root is not a
supported path and was not attempted.

## 9. What remains open

The closed routes do not exhaust the space. The open items are:

- the exact PBL enforcement point for the signed XBL hash segment;
- host-loaded XBL acceptance;
- the storage API/entry a PBL payload could use;
- the `0x13` finish payload port;
- a controlled receiver for the CVE-2020-0423 race.

See [OPEN-QUESTIONS](OPEN-QUESTIONS.md).

## 10. References

- Deep Testing: [13](13-deeptest-token-flow.md)
- XBL/ABL authentication: [10](10-xbl-abl-auth-negative-tests.md)
- Firehose/VIP: [11](11-firehose-vip-audit.md)
- Public research: [18](18-public-research-cve-triage.md)
- Recovery: [17](17-recovery-backup-gpt.md)
