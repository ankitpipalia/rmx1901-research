# 13 — Realme Deep Testing token flow

**Result:** the realme Deep Testing flow was reversed end to end and
reproduced from runtime root. The realme server rejects the RMX1901 with
`resultCode -1002` (“this model does not support the application”), so no
`unlockCode` can be obtained. The authorization is a 316-byte vendor-signed
blob; the ABL serial check can be satisfied, but the XBL/TEE signature check
cannot be minted locally.

| Item | Value |
|---|---|
| App | `com.coloros.deeptesting` 1.0.1 (RMX1901 build) |
| Signer | Same certificate as the device platform |
| Server result | `-1002`, model not supported |
| Stored blob | 316 bytes at `opporeserve1 + 0x45A000` |
| ABL check | serial at `+0x100`, version prefix `"00"` |
| TEE check | `VBVerifyFastbootUnlockVerify` → `0x50` |
| Unlock | **Not achieved** |

> **Withheld:** the exact endpoint paths, AES key array, request/response
> field values, account fields, and any token bytes are not published. They
> are withheld pending vendor review. This page describes the protocol shape
> and the measured outcome, not a reusable client.

---

## 1. The app

The RMX1901 Deep Testing APK is the genuine realme build:

- package `com.coloros.deeptesting`, version 1.0.1 (versionCode 11);
- signed with the same certificate as the device platform
  (`framework-res.apk` and `oppo-framework-res.apk`);
- runs as `userId=1000`, `sharedUser=android.uid.system`.

Because it is platform-signed, `adb install -r` succeeds and the app runs
with system uid. It is the official app, not the K3 build.

The K3 app is different: it is signed with the K3 platform certificate and
is not the RMX1901 flow. It was used only in the cross-flash experiment
([14](14-k3-crossflash-recovery.md)).

## 2. Protocol shape

The app selects a realme endpoint by system feature and sends a JSON request
containing device identity fields (board serial, IMEI, model, OTA version,
client status, operator field). The request is wrapped in an AES envelope:

- a random seed selects a key from a built-in array and a slice of the seed;
- the JSON is AES-128-ECB/PKCS5 encrypted and base64-encoded;
- the response uses a second seed and key;
- there is **no account token** in the realme variant.

The encryption is obfuscation, not authentication: the key array ships in
the APK. It does not create a vendor signature.

The app's local sequence is:

```text
applyLkUnlock
  -> resultCode 0 + data.unlockCode
checkApproveResult
  -> approval state
updateLockStatus
  -> resultCode 0 without unlockCode
     -> fastbootUnlock(unlockCode bytes)
     -> setOemUnlockEnabled(true)
     -> reboot bootloader
```

If `updateLockStatus` returns another `unlockCode`, the handler treats it as
a failure and does not call `fastbootUnlock`. The app also has a
`fastbootUnlock(new byte[]{0}, 1)` call on the `closeApply` exit path, which
writes one zero byte at the slot.

## 3. Server result

Using a replicated client with the device's real values:

```text
applyLkUnlock       -> -1002  "this model does not support the application"
checkApproveResult  -> -1008  "no application submitted"
updateLockStatus    -> -1008
closeApply          -> -1008
acquireClientStatus -> 0      applyStatus 0, lkLockStatus 1
```

The alternate realme host returned HTTP 404; only one host answered. The
rejection is a **device/model check**, not an account check. Model-spoofing
attempts (submitting under a supported model) also failed with `-1002`; the
public model-spoof trick stopped working in 2023.

**Consequence:** no server-issued `unlockCode` exists for this model.

## 4. Where the blob goes

The app calls, by reflection:

```java
android.engineer.OppoEngineerManager.fastbootUnlock(byte[] data, int length)
```

The binder service `engineer` requires the caller to be uid 1000 or 1001,
then calls `OppoEngineerNative.nativeSaveEngineerData(1000055, data, len)`,
which goes through the OPPO engineering HAL to
`/dev/block/bootdevice/by-name/opporeserve1` at offset `0x45A000`.

The HAL does **not** validate or sign the data. A 16-byte test payload and a
one-byte payload both returned `true` and were written at the slot. The
bootloader is the verifier.

This was verified with a same-boot before/after diff: the test bytes appeared
at `opporeserve1 + 0x45A000`, exactly the requested length.

## 5. The 316-byte structure

The public `DeepTest2.0` helper established the shape:

| Offset | Size | Meaning |
|---|---:|---|
| `0x000..0x0FF` | 256 | authorization / signature |
| `0x100..0x107` | 8 | ASCII serial / chip id (first ABL check) |
| `0x108..0x10B` | 4 | version/magic; first two bytes `"00"` |
| `0x10C..0x12B` | 32 | public blob field |
| `0x12C..0x13B` | 16 | model name, `#`-padded |

Older payloads were 264 bytes (`0x100` signature + 8 serial). The C.01 ABL
accepts the 316-byte form.

The ABL:

- verifies the serial at `+0x100`;
- checks that the version field starts with ASCII `"00"`;
- copies the `0x100`-byte legacy token into a `0x20C`-byte descriptor;
- passes the descriptor to XBL/TEE through the Qualcomm verified-boot
  protocol (`VBVerifyFastbootUnlockVerify`).

The ABL does **not** inspect the 256-byte signature. The cryptographic
decision is in XBL/TEE.

## 6. Measured oracle

| Block content | ABL serial check | XBL/TEE |
|---|---|---|
| correct serial at `+0x100` | passes | `VB_Fastboot_Unlock_Verify : verify fail`, status `0x50` |
| wrong serial at `+0x100` | `the serial is not match` | not reached |

This isolates the blocker: the serial check is solvable, and the vendor
signature checked by XBL/TEE is the only thing rejecting the payload.

The serial expected by the ABL is the 8-character board serial, not the UFS
VPD serial printed by XBL. Using the UFS serial fails the ABL check.

## 7. Why root cannot mint the blob

Root can:

- install the platform-signed app;
- drop to uid 1000 and call the HAL;
- write arbitrary bytes to the slot;
- set the OEM-unlock flag.

Root cannot:

- produce a valid 256-byte vendor signature;
- obtain an `unlockCode` from the server;
- make XBL/TEE accept an unsigned blob.

The 256-byte authorization is the blocking cryptographic part. Writing only
the serial at `+0x100` cannot pass the later verify, even if the serial check
is satisfied.

## 8. What was withheld, and why

| Item | Reason |
|---|---|
| Endpoint paths and request field values | Vendor review; abuse potential |
| AES key array and seed construction | Same |
| Any real token bytes | Would be a device-specific credential |
| Account/identity fields | Privacy |
| Full client source | Could be used as a turnkey token client |

The protocol shape is enough to explain the result and to support the
conclusion that the route is closed for this model.

## 9. Limits

- The server result is a snapshot; a future server change could alter it.
- The ABL/TEE analysis is static plus on-device oracle; the exact signature
  algorithm inside XBL/TEE was not reversed.
- The 316-byte layout is inferred from the public helper and the ABL parser;
  it was not confirmed with a valid vendor token (none was available).
- No unlock was achieved.

## 10. Evidence

| Claim | Evidence |
|---|---|
| Platform-signed app runs as uid 1000 | `dumpsys package` (private) |
| Server rejects model | `-1002` response (private) |
| HAL writes the slot | Before/after diff (private) |
| ABL serial check passes, TEE rejects | On-device oracle log (private) |
| 316-byte layout | Public helper + ABL parser |

The public `DeepTest2.0` repository is credited in
[UPSTREAM-CREDITS](../references/UPSTREAM-CREDITS.md); its code is not
vendored.

## 11. References

- `koaaN/DeepTest2.0` — public 316-byte layout and slot offset.
- `turistu/rmx3474-rooting` — model-spoof history (no longer works).
- `mikoker/deeptest` — newer HeyTap/OnePlus protocol (not compatible).
- CVE-2021-1931 audit and the Fastboot gate:
  [12](12-cve-2021-1931-audit.md).
- Closed routes: [21](21-closed-routes.md).
