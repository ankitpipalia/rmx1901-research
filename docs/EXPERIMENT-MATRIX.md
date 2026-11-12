# Experiment matrix

Every device or lab experiment that shaped the record. Status values:

- **PASS** — the intended measurement succeeded;
- **NEG** — the experiment ran but the intended result did not occur;
- **BLOCKED** — could not proceed for a technical reason;
- **NOT RUN** — prepared but not executed;
- **CLOSED** — the route was ruled out without a device experiment.

| ID | Experiment | Question | Result | Status | Doc |
|---|---|---|---|---|---|
| E01 | CVE-2020-0423 static diff | Is the device kernel vulnerable? | Pre-fix `binder_release_work` shape confirmed | PASS | [03](03-cve-2020-0423-binder-uaf.md) |
| E02 | 0423 race campaign | Can the device race be won? | 0 wins in ~6.5M iterations | NEG | [03](03-cve-2020-0423-binder-uaf.md) |
| E03 | KASAN binder lab | Does the trigger reach the UAF? | 351 reports vs 0 fixed | PASS | [22](22-vm-kasan-lab.md) |
| E04 | CVE-2024-31317 on A.05 | Is a real uid-1000 fork possible? | `system_app`, `ppid=zygote` | PASS | [02](02-uid1000-cve-2024-31317.md) |
| E05 | CVE-2020-0041 port on C.01 | Can runtime uid 0 be reached? | uid 0, full caps, Permissive | PASS | [01](01-runtime-root-cve-2020-0041.md) |
| E06 | Nightzuku root start | Does the Shizuku server run as root? | Yes, after env fix | PASS | [06](06-nightzuku-root-integration.md) |
| E07 | Auto-root app | Does app-context root work? | Yes; boot persistence no | PASS/NEG | [19](19-autoroot-app.md) |
| E08 | A.05 downgrade | Does the downgrade weaken the kernel/bootloader? | No; kernel same, bootloader same gate | NEG | [20](20-a05-downgrade-a20-kernel.md) |
| E09 | K3 cross-flash | What breaks when K3 firmware runs? | Modem/Wi-Fi/IMEI fail; repaired | PASS | [14](14-k3-crossflash-recovery.md) |
| E10 | Deep Testing server | Does realme support RMX1901? | `-1002` model rejected | NEG/CLOSED | [13](13-deeptest-token-flow.md) |
| E11 | HAL token write | Does the HAL validate the blob? | No; arbitrary bytes written | PASS | [13](13-deeptest-token-flow.md) |
| E12 | ABL serial oracle | Is the serial check solvable? | Yes; TEE rejects with `0x50` | PASS | [13](13-deeptest-token-flow.md) |
| E13 | Signed programmer control | Does the programmer load? | 181 READ_DATA, `DONE 1` | PASS | [07](07-pbl-programmer-auth.md) |
| E14 | Unpatched modified programmer | Is the image rejected? | Reset before `END_IMAGE_TX` | NEG | [07](07-pbl-programmer-auth.md) |
| E15 | Outer-only hash fix | Is the outer table sufficient? | Accepted with stale inner entry | PASS | [07](07-pbl-programmer-auth.md) |
| E16 | Double hash fix | Is a fully consistent image accepted? | Accepted | PASS | [07](07-pbl-programmer-auth.md) |
| E17 | Cross-OEM leaf | Is the OEM leaf the gate? | Motorola leaf accepted | PASS | [07](07-pbl-programmer-auth.md) |
| E18 | Execution oracle | Does `0x970` execute? | Magic captured after segment2/3 | PASS | [08](08-pbl-execution-oracle.md) |
| E19 | Boot-context probe | Programmer or storage path? | Type 3, descriptor `0xA` | PASS | [09](09-pbl-boot-context-probes.md) |
| E20 | Descriptor-init probe | What does type 1 produce? | Storage descriptor type 0 | PASS | [09](09-pbl-boot-context-probes.md) |
| E21 | Full-boot probe | Can handlers 0–2 load storage? | UFS hang at `0x32104C` | BLOCKED | [09](09-pbl-boot-context-probes.md) |
| E22 | PTE AP[2] diagnostic | Is a text store possible? | Ambiguous; no magic | NEG | [09](09-pbl-boot-context-probes.md) |
| E23 | Shadow-remap test | Can a text copy be remapped? | Prepared, not run | NOT RUN | [09](09-pbl-boot-context-probes.md) |
| E24 | Test A: 2-site XBL | Does a patched XBL boot? | EDL; stock restored | NEG | [10](10-xbl-abl-auth-negative-tests.md) |
| E25 | B0: re-hashed XBL | Does a benign re-hash boot? | EDL; stock restored | NEG | [10](10-xbl-abl-auth-negative-tests.md) |
| E26 | VIP `erase` probe | Is VIP enforced? | VIP off; LUN 0 formatted | PASS (destructive) | [11](11-firehose-vip-audit.md) |
| E27 | Firehose readback | Do reads match the root dump? | Yes, after framing fix | PASS | [16](16-edl-readback-and-restore.md) |
| E28 | Restore preflight | Is the restore set consistent? | Geometry/hashes pass; not run end-to-end | PASS/NOT RUN | [16](16-edl-readback-and-restore.md) |
| E29 | GPT verification | Are the six GPTs intact? | Six hashes match | PASS | [17](17-recovery-backup-gpt.md) |
| E30 | CVE-2021-1931 static audit | Is the parser reachable? | Present but behind reset gate | CLOSED | [12](12-cve-2021-1931-audit.md) |
| E31 | CVE-2021-30327 static trace | Is the `0x13` chain present? | Dispatch matches; payload not ported | BLOCKED | [18](18-public-research-cve-triage.md) |
| E32 | Keymaster `0x202` | Is the state readable? | `-0xF`, fuse blown | NEG/CLOSED | [21](21-closed-routes.md) |
| E33 | NO_AVB / GBL static | Do they apply to C.01? | No VB2 runtime check, no GBL | CLOSED | [21](21-closed-routes.md) |
| E34 | Exact-binary VM boot | Can the A.20 kernel boot in QEMU? | No faithful `virt` model | BLOCKED | [20](20-a05-downgrade-a20-kernel.md) |
| E35 | OTA extraction | Can C.01/K3 images be recovered? | Yes, 96-check verification | PASS | [15](15-ota-ozip-extraction.md) |

## Totals

Counted by primary status; a compound result (for example `PASS/NOT RUN`) is
counted under its first label.

| Status | Count |
|---|---:|
| PASS | 21 |
| NEG | 8 |
| BLOCKED | 3 |
| NOT RUN | 1 |
| CLOSED | 2 |

## Notes

- E26 is marked PASS because it answered the question (VIP off), but it was
  a destructive operational mistake. It is not a recommended procedure.
- E22 is ambiguous, not proof that PTE stores are blocked. The missing magic
  is consistent with several failure modes.
- E24/E25 are the only boot-chain writes in the XBL work; both were followed
  by a stock restore.
- E28’s preflight passed, but the restore itself was not run.
