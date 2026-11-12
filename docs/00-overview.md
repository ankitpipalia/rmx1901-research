# Overview

## 1. Subject

This is a two-week independent security research effort on a personally
owned **Realme X `RMX1901EX`** (Qualcomm Snapdragon 710, `SDM710`), plus an
OPPO K3 (`PCGM00`) firmware-compatibility experiment on the same hardware.
The work spans Android privilege escalation, Qualcomm EDL/Sahara/Firehose,
PBL/XBL/ABL reverse engineering, the Realme Deep Testing token flow, OTA
extraction, and recovery engineering.

The device was purchased used and is owned by the author. It was already
bootloader-locked with verified boot green. No third-party device, account,
or network was targeted.

## 2. Research questions

1. Can a public Android kernel/binder bug give a usable root shell on the
   C.01 build, and what device-specific changes are required?
2. Can the `system` (uid 1000) shell from CVE-2024-31317 be obtained on the
   older A.05 build, and what does it actually allow?
3. Is the Qualcomm PBL programmer gate a hash check, a PKI check, or both?
4. Can a PBL-stage payload execute code, and what does the boot context look
   like at that point?
5. Can a modified XBL or ABL boot on a locked device?
6. Is the official Realme unlock route usable for this model?
7. Which public unlock routes (devinfo, RPMB/Keymaster, NO_AVB, GBL, e=3,
   Fastboot overflow) actually apply to this build?
8. Can the device be recovered reliably from failed boot-chain experiments?

## 3. Device and builds

| Item | Value |
|---|---|
| Model | Realme X `RMX1901EX` |
| SoC | Qualcomm SDM710 (Snapdragon 710) |
| UFS | Samsung `KM5V7001DM-B621`, 6 physical LUNs, 4096-byte blocks |
| Bootloader | Locked, verified boot green |
| C.01 | `RMX1901_11_C.01`, Android 10, kernel `4.9.186-perf+`, SPL 2020-02-05 |
| A.05 | `RMX1901EX_11_A.05`, Android 9, kernel `4.9.112-perf+`, SPL 2019-06-05 |
| A.20 | `RMX1901EX_11_A.20`, Android 10, kernel `4.9.112-perf+`, SPL 2020-12-05 |
| K3 | `PCGM00_11_C.13`, Android 10, kernel `4.9.186` |

C.01 is the main research target. A.05 was used for the CVE-2024-31317
uid-1000 work and for the downgrade study. A.20 supplied kernel reference
material and backups. The K3 firmware was a compatibility experiment, not a
permanent target.

## 4. Method

The work followed a read-only-first discipline:

1. **Establish ground truth offline.** Parse the images, map symbols, and
   decompile the relevant functions before touching the device.
2. **Build a control.** For every auth test, run the stock/signed case first.
3. **Change one variable.** Patch one site or one table entry at a time.
4. **Verify by readback.** Hash the partition before and after; compare with
   the expected image.
5. **Recover deliberately.** Keep the signed programmer, the GPT set, and a
   cold-power-cycle procedure available before any boot-chain write.
6. **Record the negative result.** A failed test is data; it is documented
   with the same care as a success.

The full method, including the evidence labels `measured`, `derived`, and
`inferred`, is in [METHODOLOGY](METHODOLOGY.md).

## 5. Outcomes at a glance

### Achieved

- **Runtime uid 0 on C.01** through a device-specific CVE-2020-0041 port
  (full capabilities, SELinux Permissive, temporary).
- **uid 1000 `system_app` shell on A.05** through CVE-2024-31317
  (not root; A.05-specific).
- **Nightzuku/Shizuku running as root** on top of the runtime root.
- **PBL programmer hash-table bypass**: the outer 22-entry SHA-256 table is
  the acceptance gate; a hash-fixed programmer is accepted.
- **PBL-stage code execution**: a `segment1` payload at `0x970` runs after
  segment2/3 and sends a USB magic.
- **Boot-context measurement**: the stock payload runs the programmer path
  (type 3, descriptor `0xA`).
- **Firehose/VIP audit**: VIP is off on this unit; the 17-range whitelist
  would exclude the unlock-relevant partitions if it were on.
- **Hardware-verified Firehose readback** of `xbl`, `abl`, and `xbl_config`.
- **K3 cross-flash repair**: modem, Wi-Fi, and original IMEI restored; device
  returned to C.01.
- **CVE-2021-1931 audit**: real SD710-listed bug, but unreachable behind the
  C.01 token gate.
- **CVE-2020-0423 lab reproduction**: 351 KASAN reports on the vulnerable
  Realme binder vs 0 on the upstream-fixed control.

### Not achieved

- Bootloader unlock, orange state, or `fastboot flashing unlock`.
- Persistent root, Magisk, or dm-verity disable.
- Arbitrary code execution at EL3.
- A modified XBL or ABL that boots.
- A working CVE-2021-1931 trigger on C.01.
- A device CVE-2020-0423 root chain.
- A vendor unlock token or signing key.

## 6. Why the bootloader work stopped where it did

The chain has four separate barriers:

1. **PBL acceptance** — bypassed by fixing the outer SHA-256 table.
2. **Firehose authorization** — VIP, decided in EL3. It is off on this unit,
   but the storage boot path still hangs in UFS when forced.
3. **XBL authentication of ABL** — SBL1 sends SMC `0x82000210`; the ABL is
   authenticated before it runs.
4. **ABL unlock state** — stored in RPMB through `VBRwDeviceState`, not in
   `devinfo`.

Test A (a two-site patched XBL) and B0 (a benign re-hashed XBL) both failed
to boot and fell to EDL. The stock images were restored. The exact rejecting
gate is not localized; the leading hypothesis is the signed XBL hash segment,
but the PBL enforcement point was not proven. The next step is a read-only
probe of the storage path, not another write.

## 7. What is withheld, and why

| Item | Reason |
|---|---|
| GhostLock technical details | Coordinated disclosure; report not public |
| Deep Testing endpoints, key arrays, token bytes | Vendor review; abuse potential |
| K3 NV/IMEI repair values and procedure | Identity/NV regulation; privacy |
| Firmware, OTA, APKs, signed programmers, boot-chain images | Copyright; flashing risk |
| Device backups, `persist`, `modemst*`, `keystore`, RPMB data | Identity and secure state |
| Full CVE-2020-0041 exploit source | Upstream has no license; derivative work |
| Auto-root app source | Launcher for a kernel LPE; separate-repo decision pending |
| Internal agent/review reports | Unverified intermediate material |

Hashes of the withheld artifacts are in [evidence/hashes.md](../evidence/hashes.md).

## 8. How to read this record

- Start with [VERIFIED-RESULTS](VERIFIED-RESULTS.md) if you want the claims
  and their evidence.
- Read [07](07-pbl-programmer-auth.md) through
  [10](10-xbl-abl-auth-negative-tests.md) for the boot-chain arc.
- Read [01](01-runtime-root-cve-2020-0041.md) through
  [03](03-cve-2020-0423-binder-uaf.md) for the Android exploit arc.
- Read [13](13-deeptest-token-flow.md) through
  [17](17-recovery-backup-gpt.md) for the vendor/recovery arc.
- Read [OPEN-QUESTIONS](OPEN-QUESTIONS.md) for what is still unknown.

## 9. Limits of this record

- It is a sanitized record, not a lab notebook. Raw logs and dumps are
  private.
- Some results are single-device and single-build; they are not universal
  claims about SDM710 or Qualcomm secure boot.
- Some static conclusions are inferred from decompiled code and are labelled
  as such.
- The work is time-boxed. A negative result here means "not achieved in this
  effort", not "impossible".
