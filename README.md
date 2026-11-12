# RMX1901 Research — Snapdragon 710 boot-chain, EDL and Android privilege-escalation notes

Independent security research on a personally owned **Realme X `RMX1901EX`**
(Qualcomm Snapdragon 710 / SDM710), covering Android runtime privilege
escalation, Qualcomm EDL/Sahara/Firehose, PBL/XBL/ABL reverse engineering,
Realme Deep Testing, OPPO K3 firmware compatibility, and device recovery.

This is a **research portfolio**. It is not a bootloader-unlock release, a
root toolkit, or a one-click exploit.

> **Status: the bootloader is locked and verified boot is green.**
> No bootloader unlock was achieved. No persistent root was achieved.
> Runtime uid 0 was obtained on C.01 through CVE-2020-0041 and is lost on
> reboot. The official Realme Deep Testing service rejects this model.
> Modified XBL images did not boot. All experiments were performed on an
> owned device, with recovery available, and no third-party device was
> touched.

---

## What is in this repository

| Area | Result | Document |
|---|---|---|
| CVE-2020-0041 binder LPE on C.01 (Android 10) | uid 0, full capabilities, SELinux Permissive — runtime only | [01](docs/01-runtime-root-cve-2020-0041.md) |
| CVE-2024-31317 Zygote injection on A.05 (Android 9) | uid 1000 `system_app` shell — not root | [02](docs/02-uid1000-cve-2024-31317.md) |
| CVE-2020-0423 binder UAF | Bug and offsets verified; race never won on device; KASAN lab reproduced it | [03](docs/03-cve-2020-0423-binder-uaf.md) |
| GhostLock / rtmutex audit | Gate 2 measured infeasible on 4.9.112/4.9.186; details withheld | [04](docs/04-ghostlock-audit.md) |
| KGSL/Adreno CVE-2020-11179 | Reachable surface; remediation markers absent; no chain | [05](docs/05-kgsl-adreno-audit.md) |
| Nightzuku/Shizuku as root | Working after fixing the daemon environment | [06](docs/06-nightzuku-root-integration.md) |
| PBL programmer authentication | Outer 22-entry SHA-256 table is the gate; hash-fixed programmer accepted | [07](docs/07-pbl-programmer-auth.md) |
| PBL code execution | Payload at `0x970` executed after segment2/3; USB magic captured | [08](docs/08-pbl-execution-oracle.md) |
| PBL boot-context probes | Stock payload is the programmer path; storage boot hangs in UFS | [09](docs/09-pbl-boot-context-probes.md) |
| XBL/ABL authentication | SBL1 SMC `0x82000210`; Test A and B0 rejected; stock restored | [10](docs/10-xbl-abl-auth-negative-tests.md) |
| Firehose/VIP authorization | VIP off on this unit; 17-range whitelist analysed | [11](docs/11-firehose-vip-audit.md) |
| CVE-2021-1931 | Real SD710-listed bug; unreachable behind the C.01 token gate | [12](docs/12-cve-2021-1931-audit.md) |
| Deep Testing token flow | Protocol reversed; server returns `-1002`; 316-byte vendor blob | [13](docs/13-deeptest-token-flow.md) |
| OPPO K3 cross-flash | Repaired modem/Wi-Fi; returned to C.01; NV details withheld | [14](docs/14-k3-crossflash-recovery.md) |
| OPPO `.ozip` / OTA extraction | C.01 and K3 images decrypted and verified; no firmware published | [15](docs/15-ota-ozip-extraction.md) |
| EDL readback and restore | Hardware-verified three-phase readback; restore XML drafted, untested | [16](docs/16-edl-readback-and-restore.md) |
| Backup, GPT and recovery | Six GPTs verified; C.01 boot-chain set; cold-power-cycle recovery | [17](docs/17-recovery-backup-gpt.md) |
| Public research and CVE triage | Repos and CVEs validated or ruled out | [18](docs/18-public-research-cve-triage.md) |
| Auto-root app | App-context root proven; daemon lifecycle unresolved; source not published | [19](docs/19-autoroot-app.md) |
| A.05 downgrade / A.20 corpus | Kernel code unchanged; user space 18 months older; bootloader not weakened | [20](docs/20-a05-downgrade-a20-kernel.md) |
| Closed routes | `devinfo`, RPMB/Keymaster, NO_AVB, GBL, ABL token, e=3 | [21](docs/21-closed-routes.md) |
| VM/KASAN lab | CVE-2020-0423 reproduced: 351 reports vs 0 on the fixed control | [22](docs/22-vm-kasan-lab.md) |

Supporting material:

- [docs/INDEX.md](docs/INDEX.md) — full navigation
- [docs/RESEARCH-TIMELINE.md](docs/RESEARCH-TIMELINE.md) — chronology
- [docs/VERIFIED-RESULTS.md](docs/VERIFIED-RESULTS.md) — claim / evidence / confidence
- [docs/EXPERIMENT-MATRIX.md](docs/EXPERIMENT-MATRIX.md) — every experiment and outcome
- [docs/OPEN-QUESTIONS.md](docs/OPEN-QUESTIONS.md) — unresolved questions
- [docs/METHODOLOGY.md](docs/METHODOLOGY.md) — how the work was done
- [docs/GLOSSARY.md](docs/GLOSSARY.md) — terms
- [docs/PUBLICATION-GATES.md](docs/PUBLICATION-GATES.md) — sanitization and disclosure checks
- [evidence/](evidence/README.md) — sanitized excerpts and hashes of withheld artifacts
- [references/PUBLIC-SOURCES.md](references/PUBLIC-SOURCES.md) — public sources used
- [tools/](tools/README.md) — offline analysis and validation tools

---

## Device and firmware matrix

| Build | Android | Kernel | Role in this work |
|---|---|---|---|
| `RMX1901EX_11_A.05` | 9 | 4.9.112-perf+ | CVE-2024-31317 uid-1000 work; downgrade study |
| `RMX1901EX_11_A.20` | 10 | 4.9.112-perf+ | Kernel corpus and reference backups |
| `RMX1901EX_11_C.01` | 10 | 4.9.186-perf+ | CVE-2020-0041 runtime root; EDL/PBL/XBL/ABL work |
| OPPO K3 `PCGM00_11_C.13` | 10 | 4.9.186 | Cross-flash compatibility experiment |
| F.01 (referenced only) | 10 | — | Third-party report; not available for verification |

The C.01 build is `RMX1901_11_C.01`, security patch `2020-02-05`, kernel
`4.9.186-perf+`. The A.05 build is `RMX1901EX_11_A.05`, patch `2019-06-05`,
kernel `4.9.112-perf+`.

---

## The short version

1. **Runtime root is real but temporary.** A device-specific port of the
   Blue Frost CVE-2020-0041 binder exploit gives uid 0 with full
   capabilities and SELinux Permissive on C.01. It does not touch the
   bootloader, does not persist, and is cleared by reboot.
2. **The bootloader gate is layered.** PBL accepts a signed programmer;
   the outer 22-entry SHA-256 table is the acceptance gate, and a
   hash-fixed programmer is accepted. Firehose then decides authorization
   through VIP in EL3. XBL authenticates ABL through SBL1 and SMC
   `0x82000210`. ABL keeps unlock state in RPMB, not `devinfo`.
3. **PBL-stage code execution was proven.** A `segment1` payload at
   `0x970` runs after segment2/3 and can send a USB magic. That is code
   execution at PBL stage; it is not proof of EL3 privilege or of a
   persistent unlock.
4. **Modified boot chains were rejected.** A two-site patched XBL and a
   benign re-hashed XBL both failed to boot and fell to EDL. The stock
   images were restored. The exact rejecting gate is not localized.
5. **The official unlock route is closed for this model.** Realme's server
   returns `-1002` ("this model does not support the application"). The
   316-byte vendor blob is signed; root can write the slot but cannot mint
   the signature. The ABL serial check is solvable; the XBL/TEE signature
   check is not.
6. **The device is recoverable.** The signed programmer, verified GPTs,
   C.01 boot-chain set, and cold-power-cycle procedure were all validated.

---

## What is *not* claimed

- No bootloader unlock, no `fastboot flashing unlock`, no orange state.
- No persistent root, no Magisk, no dm-verity disable.
- No arbitrary code execution at EL3.
- No bypass of XBL's ABL authentication.
- No working CVE-2021-1931 trigger on C.01.
- No working CVE-2020-0423 root chain on the device.
- No vendor token, signing key, or engineering ABL.
- No claim that a modified programmer is a universal unlock.

Where a result is inferred rather than measured, the document says so. The
[VERIFIED-RESULTS](docs/VERIFIED-RESULTS.md) table separates measured,
derived, and inferred claims.

---

## Safety and scope

- All work was performed on a personally owned device.
- No third-party device, account, or network was targeted.
- No IMEI, MEID, serial, MAC, account, or NV data is published.
- No firmware, OTA, APK, signed programmer, boot-chain image, or device
  backup is published.
- No step-by-step IMEI/NV modification procedure is published.
- Destructive Firehose runners are not published. The tools here are
  read-only analysis and fail-closed validation helpers.
- Some findings are withheld pending coordinated disclosure; see
  [SECURITY.md](SECURITY.md) and [docs/04](docs/04-ghostlock-audit.md).

If you use any of this, use it on hardware you own, with a tested recovery
path. Boot-chain writes can permanently brick a device.

---

## Companion repository

The macOS/libusb Qualcomm 9008 transport, the `oppo710` PBL host sequence,
the signed-programmer serve path, the programmer hash-table work, and the
`segment1` oracle live in:

**<https://github.com/ankitpipalia/pblexp-macos>** (MIT)

This repository is the research record around that tooling: what was tried,
what was measured, what failed, and what remains open.

---

## Licensing

- **Code** (tools, tests): MIT — see [LICENSE](LICENSE).
- **Documentation and diagrams**: CC BY 4.0 — see [LICENSE-DOCS](LICENSE-DOCS).
- Third-party material is linked, not vendored; see
  [references/THIRD-PARTY-LICENSES.md](references/THIRD-PARTY-LICENSES.md).

Vendor firmware, OTA packages, APKs, signed programmers, and device dumps
are **not** licensed for redistribution and are not included.

---

## Citation

```bibtex
@misc{pipalia_rmx1901_research_2026,
  author       = {Ankit Pipalia},
  title        = {RMX1901 Research: Snapdragon 710 boot-chain, EDL and
                  Android privilege-escalation notes},
  year         = {2026},
  howpublished = {\url{https://github.com/ankitpipalia/rmx1901-research}}
}
```

---

## A note on evidence

The private working tree contains raw USB captures, device logs, partition
dumps, firmware, and proprietary images. Those are not published. What is
published is the analysis, the sanitized excerpts that support specific
claims, and SHA-256 hashes that identify the withheld artifacts without
distributing them. See [evidence/hashes.md](evidence/hashes.md).
