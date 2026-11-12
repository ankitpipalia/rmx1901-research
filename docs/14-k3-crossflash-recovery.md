# 14 — OPPO K3 cross-flash and recovery

**Result:** an OPPO K3 `PCGM00_11_C.13` firmware set was cross-flashed onto
the RMX1901. The device booted, but the modem crashed, Wi-Fi did not work,
and the IMEI was empty. A two-part repair — a hybrid modem filesystem with
the K3 ADSP generation, and a corrected NV board profile — restored the
modem, Wi-Fi, and the original IMEI. The device was later returned to C.01.

This is a **compatibility and recovery case study**. It is not an unlock
method. NV/IMEI values, offsets, images, and step-by-step identity repair are
**withheld**.

| Item | Value |
|---|---|
| Hardware | RMX1901 / SDM710 |
| Cross-flashed firmware | OPPO K3 `PCGM00_11_C.13`, Android 10 |
| Symptoms | modem crash, no Wi-Fi, empty IMEI |
| Repair | hybrid modem + NV board-profile alignment |
| Outcome | modem/Wi-Fi/IMEI restored; device usable |
| Final state | returned to C.01 |

---

## 1. Why the experiment was done

The K3 and the Realme X share the SDM710 platform. A K3 firmware set was
available, and the question was whether a different OEM's Android 10 build
would boot and what would break. The experiment was performed on the owned
RMX1901, with the original A.20 backup and EDL recovery available.

It was not an attempt to bypass the bootloader. The device remained locked
and verified boot green throughout.

## 2. What happened

The K3 system/vendor/boot images booted. ADB and Bluetooth worked. But:

- the modem crashed repeatedly;
- Wi-Fi did not initialize (`wlan0` absent);
- the IMEI was empty;
- camera/ADSP/sensor functions failed.

The failures were not a bad flash: the GPTs and partition writes were
verified by readback and matched the intended images. The problem was a
**firmware/hardware compatibility mismatch**.

## 3. Root causes

Two mismatches were identified:

1. **ADSP firmware generation.** The K3 build requested an `adsp_v3`-style
   firmware set, while the restored RMX1901 modem filesystem supplied the
   older `adsp.mdt` generation. The modem could not load its DSP firmware.
2. **NV board profile.** The K3 firmware used a different numeric board
   dictionary, so it selected a different NV board profile from the
   RMX1901's original NV containers. The RF calibration and modem
   configuration therefore did not match the hardware.

Both are compatibility problems, not security bypasses.

## 4. Repair, at the level that can be published

The repair had two parts:

1. **Hybrid modem filesystem.** Start from the original RMX1901 modem
   filesystem and add the K3 ADSP-v3 files the firmware expects. All
   original modem files were preserved with identical hashes. The hybrid
   image was written to the modem partition and verified by full readback.
2. **NV board-profile alignment.** Correct the board labels in the NV
   container headers so the K3 loader selects the profile that matches the
   original RMX1901 calibration, and fix the header checksum. Only the
   first sector of each container was changed; the calibration data after it
   was left intact. The two containers were written one block each and
   verified by full readback.

The exact offsets, labels, checksum procedure, and images are withheld
because they are an identity/NV modification recipe. The high-level lesson
is publishable: **cross-flashing an OEM firmware set is not just a partition
copy; the modem DSP generation and the NV board profile must match the
hardware.**

## 5. Result

After the repair:

- the RF fatal disappeared;
- the modem initialized;
- the original IMEI was restored;
- Wi-Fi loaded, scanned, and connected;
- the repair survived a second boot.

The device was usable on K3 firmware. The bootloader remained locked.

## 6. The unlock attempt on K3

The K3 Deep Testing app was installed. It is signed with the K3 platform
certificate and runs as a system app, but the realme/OPPO server rejected
the K3 model (`PCGM00`) as not supported. No token was issued.

This confirmed that the server-side model check is independent of the local
app: a platform-signed app is not enough if the model is not eligible.

The device was later returned to C.01, where the PBL/XBL/ABL work continued.

## 7. Why the details are withheld

| Item | Reason |
|---|---|
| NV container offsets and board labels | Identity/NV modification recipe |
| IMEI, serial, MAC, calibration values | Privacy and identity theft risk |
| Modem/NV images | Proprietary and identity-bearing |
| Exact checksum/repair steps | Could be used to alter another device's identity |

Publishing these would enable IMEI alteration and device cloning, which is
illegal or restricted in many jurisdictions. The case study keeps the
engineering lesson without the recipe.

## 8. Lessons

- Platform similarity is not firmware compatibility. The modem DSP
  generation and NV profile are part of the hardware contract.
- A verified partition write can still produce a non-working device if the
  firmware expects different companion images.
- Keep the original modem/NV backup before any cross-flash. The repair here
  depended on the original RMX1901 containers.
- A locked bootloader does not prevent a cross-flash; it prevents booting
  modified boot images. The two are different risks.
- Recovery is a prerequisite, not an afterthought.

## 9. Limits

- Single device, single K3 build.
- The repair is not a general procedure for other models.
- The NV alignment was validated by behavior and readback, not by a
  vendor tool.
- The device was returned to C.01; long-term stability on K3 was not the
  goal.

## 10. Evidence

| Claim | Evidence |
|---|---|
| K3 booted on RMX1901 | Boot logs and build properties (private) |
| Modem/Wi-Fi/IMEI failures | Logs and service state (private) |
| Repair worked | Post-repair logs and readback hashes (private) |
| Server rejects K3 model | Deep Testing response (private) |
| Returned to C.01 | Build properties and verified boot state |

## 11. References

- K3 firmware compatibility notes (private).
- Realme Deep Testing flow: [13](13-deeptest-token-flow.md).
- C.01 recovery: [17](17-recovery-backup-gpt.md).
- OTA extraction: [15](15-ota-ozip-extraction.md).
