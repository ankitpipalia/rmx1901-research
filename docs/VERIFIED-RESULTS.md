# Verified results

This table is the claim-by-claim index. Labels:

- **M** — measured on the device or in a controlled lab;
- **D** — derived from static analysis of the named artifact;
- **I** — inferred, with the basis stated;
- **N** — negative result (the thing was attempted and did not work).

If a claim is not in this table, treat it as context, not a result.

## Bootloader and boot chain

| # | Claim | Label | Evidence |
|---:|---|---|---|
| 1 | The bootloader is locked and verified boot is green | **M** | `ro.boot.flash.locked=1`, green state on every boot |
| 2 | No bootloader unlock was achieved | **M** | No orange state, no `fastboot flashing unlock` success |
| 3 | The outer 22-entry SHA-256 table gates programmer acceptance | **M** | Hash-fixed programmer accepted; unpatched modified image rejected |
| 4 | The nested XBL_SEC table is not enforced before the programmer runs | **M** | Outer-only control accepted with a stale inner entry [5] |
| 5 | The OEM PKI leaf is not the gate on this path | **M** | Motorola-leaf `devprg_710` accepted |
| 6 | The outer hash is effectively unsigned in this path | **D** | Static PKI gate analysis; stale outer signature accepted |
| 7 | A `segment1:0x970` payload executes after segment2/3 | **M** | `PBLXORACLE2026!!EXEC-PROOF-0x970` captured |
| 8 | The stock `segment1` payload runs the programmer path | **M** | Boot context type 3, descriptor `0xA` |
| 9 | Forcing type 1 produces a storage descriptor | **M** | Descriptor-init probe |
| 10 | The full-boot storage path hangs in UFS from EDL | **M** | Handlers 0–2 return; hang at `0x30F384`/`0x32104C` |
| 11 | SBL1 authenticates ABL through SMC `0x82000210` | **D** | Decompiled call chain `FUN_14856f5c → FUN_14859598 → FUN_14859d3c` |
| 12 | `VerifiedBootDxe` is the Android boot/vbmeta verifier, not the ABL gate | **D** | Static analysis and SDM710 source comparison |
| 13 | ABL unlock state is RPMB-backed, not `devinfo`-backed | **D + M** | `VBRwDeviceState` path; runtime log `Succeed using rpmb!`; no `devinfo` xref |
| 14 | The Fastboot unlock writer is dead behind `0x57c0` | **D** | `mov w0,#2; ret` |
| 15 | Test A (two-site patched XBL) did not boot | **M** | `OK xbl in 195.6 s`, then EDL |
| 16 | B0 (benign re-hashed XBL) did not boot | **M** | `OK xbl in 195.7 s`, then EDL |
| 17 | Stock XBL/ABL were restored and the device booted | **M** | C.01 green/locked after restore |
| 18 | The XBL hash segment is signed | **D** | 16-entry table at `0x1028`, 256-byte signature at `0x1228`, cert chain at `0x1328` |
| 19 | The PBL enforces the XBL signature on the storage path | **I** | Leading hypothesis for Test A/B0; not localized |
| 20 | A modified ABL would boot | **N** | Blocked by XBL authentication; not attempted |

## Android privilege escalation

| # | Claim | Label | Evidence |
|---:|---|---|---|
| 21 | CVE-2020-0041 gives uid 0 with full caps on C.01 | **M** | Runtime `id`/`/proc/self/status` |
| 22 | SELinux is Permissive after the exploit | **M** | `getenforce` |
| 23 | Root is lost on reboot | **M** | Repeated cold boots |
| 24 | `mm->pgd` is at `0x48` and `task_struct::stack` at `0x60` | **D + M** | `vmlinux` layout; the correct offsets work |
| 25 | Realme's `oppo_root_check` reboots on ordinary cred changes | **M** | Controlled reboot observations; whitelisted `set*id` path works |
| 26 | CVE-2024-31317 gives uid 1000 `system_app` on A.05 | **M** | Real fork with `ppid=zygote`, `u:r:system_app:s0` |
| 27 | CVE-2024-31317 is not root | **M** | uid 1000 only; no `setuid(0)` |
| 28 | CVE-2024-31317 applies to C.01 | **N** | Not tested in this work |
| 29 | CVE-2020-0423 is present on the device kernel | **M + D** | Disassembly vs upstream fix; lab KASAN |
| 30 | The device race was won | **N** | 0 wins in ~6.5M iterations |
| 31 | The 0423 harness was the limitation, not the bug | **I** | Review conclusion; published model uses the same trigger |
| 32 | The KASAN lab reproduces the UAF | **M** | 351 reports / 2,357,052 sends |
| 33 | The upstream fix removes the UAF | **M** | 0 reports / 2,581,894 sends |
| 34 | Nightzuku runs as root | **M** | `shizuku_server` uid 0; app reports root |
| 35 | Nightzuku's failure was an environment issue | **M** | Same command works with the Android env |
| 36 | App-context root works | **M** | Auto-root app runtime |
| 37 | Boot-time re-root is reliable | **N** | Boot receiver disabled; lifecycle unresolved |

## Vendor, OTA and recovery

| # | Claim | Label | Evidence |
|---:|---|---|---|
| 38 | The realme server rejects RMX1901 with `-1002` | **M** | Replicated client response |
| 39 | The 316-byte blob has a vendor signature the ABL cannot mint | **D + M** | ABL parser; serial-only block rejected by TEE with `0x50` |
| 40 | The HAL writes arbitrary bytes to `opporeserve1+0x45A000` | **M** | Before/after diff |
| 41 | CVE-2021-1931 is SD710-listed | **M** | NVD record |
| 42 | C.01's Fastboot parser is unreachable on stock | **D** | Token gate resets before USB init |
| 43 | The public xperable exploit is Sony-specific | **M** | Upstream target list |
| 44 | The K3 cross-flash repair restored modem/Wi-Fi/IMEI | **M** | Post-repair logs and readback |
| 45 | The K3 server rejects `PCGM00` | **M** | Deep Testing response |
| 46 | C.01 and K3 OTA images were extracted and verified | **M** | 96-check verifier; live partition comparison |
| 47 | Firehose readback of `xbl`/`abl`/`xbl_config` matches the root dump | **M** | `fadc6410…`/`9a57f700…`/`5a551955…` |
| 48 | The earlier `4b5f64a1…` hash was a host framing artifact | **D** | Three framing bugs identified and fixed |
| 49 | The six GPTs are verified | **M** | Six SHA-256 values match |
| 50 | The restore XML is end-to-end tested | **N** | Geometry-verified only |

## Closed routes

| # | Claim | Label | Evidence |
|---:|---|---|---|
| 51 | `devinfo` is inert on C.01 | **D + M** | No ABL xref; RPMB state |
| 52 | Keymaster `0x202` returns `-0xF` | **M** | Read-only probe |
| 53 | NO_AVB does not apply | **D** | VB2 compile-time; no `vbmeta` strings; no TWRP |
| 54 | GBL/`efisp` does not apply | **D** | No GBL/efisp on Android 10 C.01 |
| 55 | e=3 is not present | **D** | All certs `e=65537` |
| 56 | VIP is off on this unit | **M** | Unrestricted `erase` executed |
| 57 | The static VIP whitelist excludes `abl`/`boot`/`devinfo` | **D** | 17-range table + GPT |
| 58 | CVE-2021-30327's `0x13` dispatch chain is present on RMX1901 | **D** | `0x3246a8[0x11] → 0x308e28 → 0x307fd8 → 0x308df8` |
| 59 | The `0x13` finish payload was ported | **N** | SDM845 payload only; not completed |

## Explicitly not claimed

| Claim | Status |
|---|---|
| Bootloader unlocked | **No** |
| Persistent root / Magisk | **No** |
| EL3 arbitrary code execution | **No** |
| Modified XBL/ABL boots | **No** |
| Working CVE-2021-1931 trigger | **No** |
| Device CVE-2020-0423 root chain | **No** |
| Vendor token / signing key | **No** |
| Universal SDM710 result | **No** |
