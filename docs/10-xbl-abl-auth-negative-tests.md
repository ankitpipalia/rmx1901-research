# 10 — XBL/ABL authentication and the negative boot tests

**Result:** two modified XBL images were written to the device and both
failed to boot, falling to EDL. The stock XBL and ABL were restored. The
static analysis shows that SBL1 authenticates ABL through SMC `0x82000210`,
that `VerifiedBootDxe` is the Android boot/vbmeta verifier rather than the
ABL gate, and that the Fastboot unlock writer is dead behind a stub. The
exact gate that rejected the modified XBL is **not localized**.

| Test | Image | Write | Boot | Recovery |
|---|---|---|---|---|
| A | two-site patched XBL `6982bba2…` | `OK xbl in ~195.6 s` | EDL | stock restored |
| B0 | benign re-hashed XBL `f541fbfc…` | `OK xbl in ~195.7 s` | EDL | stock restored |

---

## 1. The trust chain

```text
PBL
 -> XBL          (authenticated by PBL)
    -> SBL1
       -> ABL    (authenticated by SBL1, SMC 0x82000210)
          -> boot / vbmeta (VerifiedBootDxe)
```

There are two different verifiers in this chain, and conflating them caused
several wrong turns:

- **SBL1 `SecBootAuthLib`** authenticates the ABL image. The call chain is
  `FUN_14856f5c → FUN_14859598 → FUN_14859d3c`, SMC **`0x82000210`**
  ("Auth Metadata"). The ABL descriptor comes from the `xbl_config`
  partition; the ABL entry is `sec_type 28`, `auth:1`, RSA/ASN.1/X.509.
- **`VerifiedBootDxe`** verifies the Android boot image and vbmeta. It is
  not the ABL gate.

The earlier hypothesis that `VerifiedBootDxe::VerifyImage` authenticated
ABL was wrong. The correction matters because patching the Android verifier
would not make a modified ABL boot.

## 2. ABL unlock state

The ABL unlock writer is `FUN_00025d50(type, value)`:

- type 0 = unlock (`devinfo[0x0d]`);
- type 1 = critical unlock (`devinfo[0x0e]`);
- it sets the byte and calls
  `FUN_0001bae0(1, 0x68678, 0x998)`, which is
  `QCOM_VERIFIEDBOOT_PROTOCOL->VBRwDeviceState(WRITE_CONFIG, devinfo, 0x998)`;
- the write persists through **RPMB** (`VB: RWDeviceState: Succeed using rpmb!`);
- it then writes `recovery\n--format_data\n` at offset `0x40` of a `0x440`
  `bootloader_message` into `misc`, which wipes userdata.

The `devinfo` blob is `0x998` bytes. The ABL never reads the `devinfo`
**partition**, so editing or flashing that partition is inert. This is why
the “write two bytes to devinfo” route does not work on C.01.

The Fastboot `flashing unlock` handler `FUN_000374c8` reaches
`FUN_00025d50(0,1)` only if `FUN_000057c0()` returns 3. On C.01,
`0x57c0` is exactly:

```text
mov w0, #2
ret
```

So the headless unlock branch is dead, and the display Unlock/Lock menu
(`FUN_00028f88`) is the only path — it needs an enabled display and
physical key presses.

## 3. Fastboot gate

`FUN_00030cf4` (Fastboot app) calls `FUN_000311b4` (the vendor token gate)
**before** USB init:

```c
lVar5 = FUN_000311b4();
if (lVar5 != 0) {
    ... "fastboot_unlock_verify error and reboot."
    FUN_00011078('>');       // EFI_RUNTIME_SERVICES->ResetSystem
}
...
FUN_0001e5f8(0);
... USB init ...
"Fastboot: Processing commands"
```

`FUN_000311b4`:

- reads the board serial, pads it to 8 characters;
- selects LBA `0x45A` or `0x2206` for `opporeserve1`;
- compares the stored serial;
- calls `VBVerifyFastbootUnlockVerify` with a `0x20C`-byte buffer;
- returns `0x100` on every failure path, `0` on success.

`FUN_00011078` sets `x0=0` (`EfiResetCold`), `x1=0` or
`0x8000000000000002`, `x2=0x19`, `x3=buffer`, and calls
`[DAT_00059f90 + 0x68]`, the EDK2 `EFI_RUNTIME_SERVICES->ResetSystem` slot.

**Consequence:** a failed token check performs a cold reset before USB
initialization. The Fastboot command parser (and CVE-2021-1931) is not
reachable on stock C.01 without a valid token or a modified ABL that skips
the gate.

## 4. Test A — two-site patched XBL

Test A replaced two `bl 0x146ae000` instructions with `mov w0,#0`:

| Site | Address | Purpose |
|---|---:|---|
| 1 | `0x22dec` | XBL per-image auth call (`0x82000210`) |
| 2 | `0x22e80` | second auth wrapper (`0x82000211`) |

Each patch is four bytes: `00 00 80 52`. No `ret` was added.

The candidate XBL `6982bba2…` was written successfully:

```text
OK xbl in 195.6s
```

The ABL was left stock. On the next boot the device fell to **EDL** instead
of Android. Test B was not attempted. Stock XBL was restored, and the device
booted C.01 green/locked.

### What the static trace said

- All 614 PBL functions were decompiled. No writer of `ctx+0x24` or
  `ctx+0x120` was found; the auth config `0x1480fbb0+0x70` is only read by
  `b198`, which writes zero. The setter is outside the PBL image.
- `FUN_0031c990` / `FUN_0031c6e4` are gated on `ctx+0x120` / `ctx+0x24`.
- `FUN_0031ce8c` is `return 0`.
- The `"ISMQ"` gate reads `0xffffffff`.
- The post-hash RSA path is dead in the PBL.

Static default: the PBL auth is **hash-only** on this path. The XBL hash
segment is signed (see below), but whether the PBL enforces that signature
on the storage path is **not runtime-proven**.

### P0c correction

Both patches replace `bl 0x146ae000`, the SMC trampoline. The wrappers
consume only `ret`. The patched path sets the return to 0, so the
“uninitialized output buffer” failure mode is not supported. The second
site is `0x22e80`, not `0x22e60`.

The older explanation that “three unpatched auth stages caused EDL” was
**retracted**. The Stage-2 cause is unresolved.

## 5. Test B0 — benign re-hashed XBL

B0 changed one string byte and `table[2]` in the XBL hash segment, then
re-hashed it so the table was self-consistent. The image `f541fbfc…` was
written successfully (`OK xbl in 195.7s`) and the device again fell to EDL.

This is important because it isolates **hash consistency** from **code
changes**: even a benign image with a self-consistent table was rejected.
The leading hypothesis is the signed hash segment: the XBL carries a
16-entry table at `0x1028`, a 256-byte signature at `0x1228`, and a
certificate chain at `0x1328`. Updating `table[2]` invalidates the
signature. If the PBL verifies that signature on the storage path, a
re-hashed image cannot boot.

That hypothesis is consistent with both tests but is not localized. The
rejecting gate could also be the SBL1 ABL auth path or another check.

## 6. Why Path A1 was not completed

Path A1 was the designed chain:

1. host-load a patched XBL (patch SBL1 XBL auth, the SBL1 ABL-auth call, and
   Fastboot);
2. flash only the modified ABL (`0x311b4` → `mov w0,#0; ret`,
   `0x57c0` → `mov w0,#3; ret`);
3. run `fastboot flashing unlock` → `FUN_00025d50(0,1)`;
4. restore the stock ABL.

It was not completed because:

- host-loaded XBL acceptance is unproven (the boot-context probes showed the
  stock payload is the programmer path, and the storage path hangs in UFS);
- the exact PBL enforcement point is not localized;
- a modified ABL will not boot if XBL authenticates it;
- the risk of another boot-chain write without a localized gate was not
  justified.

## 7. What is measured vs inferred

| Claim | Status |
|---|---|
| Test A XBL was written and did not boot | **Measured** |
| Test B0 re-hashed XBL was written and did not boot | **Measured** |
| Stock XBL/ABL restored and device booted | **Measured** |
| SBL1 authenticates ABL via SMC `0x82000210` | **Derived** from static analysis |
| `VerifiedBootDxe` is not the ABL gate | **Derived** |
| `devinfo` partition is inert; state is in RPMB | **Derived + runtime log** |
| `0x57c0` is a stub returning 2 | **Measured statically** |
| XBL hash segment is signed | **Measured statically** |
| PBL enforces the XBL signature on the storage path | **Unproven** |
| A modified ABL would boot | **No** |

## 8. Evidence

- Test A failure notes:
  [evidence/logs-sanitized/testA-failure-2026-11-12.md](../evidence/logs-sanitized/testA-failure-2026-11-12.md)
- B0 rejection:
  [evidence/logs-sanitized/b0-rejection-2026-11-12.md](../evidence/logs-sanitized/b0-rejection-2026-11-12.md)
- Hashes of the XBL candidates and stock images:
  [evidence/hashes.md](../evidence/hashes.md)
- Raw images and full logs are private.

## 9. Limits

- Two negative boot tests do not identify the rejecting gate.
- The static trace covers the PBL image; the setter may be outside it.
- The ABL auth chain is derived from decompiled code; the SMC call is not
  instrumented at runtime.
- No modified ABL was flashed in these tests.
- The device was recovered; a failed XBL write can still brick a device
  without a tested programmer path.

## 10. References

- PBL programmer auth: [07](07-pbl-programmer-auth.md)
- PBL oracle: [08](08-pbl-execution-oracle.md)
- Boot-context probes: [09](09-pbl-boot-context-probes.md)
- Firehose/VIP: [11](11-firehose-vip-audit.md)
- Closed routes: [21](21-closed-routes.md)
- Companion tooling: <https://github.com/ankitpipalia/pblexp-macos>
