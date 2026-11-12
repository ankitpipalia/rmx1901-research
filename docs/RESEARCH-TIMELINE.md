# Research timeline

A condensed chronology of the two-week effort. Dates are local (Asia/Kolkata).
The private working tree has more granular logs; this page records the
milestones that shaped the published record.

| Date | Phase | Event | Outcome |
|---|---|---|---|
| 2026-10-30 | Android triage | External audit of the A.20 kernel corpus; earlier reports reconciled and superseded | Kernel CVE verdicts consolidated |
| 2026-11-02 | Android | CVE-2024-31317 mechanism proven on A.05; `system_app` domain corrected; output-channel limits mapped | uid 1000, not root |
| 2026-11-02 | Android | CVE-2020-0423 controlled-receiver blocker identified; `addService`/context-manager routes ruled out | Race harness redesigned |
| 2026-11-05 | Android | 0423 race campaigns (timerfd/futex storms, signalfd spray) | No win; harness limitations noted |
| 2026-11-06 | K3 | Cross-flash repair completed: hybrid modem + NV board-profile alignment | Modem/Wi-Fi/IMEI restored |
| 2026-11-07 | Android | A.05 downgrade study; C.01 OTA analysis; A.05 exploit run | Kernel unchanged; 31317 uid 1000 on A.05 |
| 2026-11-07 | Lab | 0423 KASAN lab: 351 UAF reports vs 0 on the fixed control | Bug and fix reproduced |
| 2026-11-09 | Root | CVE-2020-0041 port reaches uid 0 on C.01 | Runtime root |
| 2026-11-09 | Boot chain | Deep Testing flow reversed; server rejects RMX1901 `-1002` | Official route closed |
| 2026-11-09 | Boot chain | PBL baseline programmer accepted; Keymaster `0x202` returns `-0xF` | RPMB route measured closed |
| 2026-11-09 | Recovery | C.01 boot-chain set and GPT verification | Recovery basis |
| 2026-11-10 | PBL | PBL dump and IMEM window analysed | Page tables and boot flow mapped |
| 2026-11-10 | PBL | Execution oracle: `PBLXORACLE2026!!EXEC-PROOF-0x970` | PBL-stage code execution |
| 2026-11-10 | EDL | Reset automation and Firehose power helper | `reset_to_edl` ACK |
| 2026-11-11 | PBL | Hash-fixed programmer accepted; outer-only control accepted | Outer hash table is the gate |
| 2026-11-11 | Firehose | VIP audit; live `erase` probe formatted LUN 0 | VIP off; recovery required |
| 2026-11-12 | XBL/ABL | Test A: two-site patched XBL written, device fell to EDL | Negative boot test; stock restored |
| 2026-11-12 | XBL/ABL | B0: benign re-hashed XBL written, device fell to EDL | Negative boot test; stock restored |
| 2026-11-12 | PBL | Boot-context probe: type 3, descriptor `0xA` | Stock payload is programmer path |
| 2026-11-12 | PBL | Descriptor-init and full-boot probes: type 1 descriptor, UFS hang | Storage path blocked in EDL |
| 2026-11-12 | PBL | PTE ground truth from IMEM; shadow-remap payloads rebuilt | Primitive identified, not run |
| 2026-11-12 | Root | Nightzuku root mode fixed by exporting the Android environment | Shizuku server as uid 0 |
| 2026-11-12 | Research | CVE-2021-1931 audit; F.01 claims checked | Real bug, unreachable on stock C.01 |
| 2026-11-13 | Publication | Sanitized 22-workstream repository assembled, scanned, and published | This record |

## Phase summary

### Phase 1 — Android privilege escalation (Oct 30 – Nov 9)

Started with the A.20 kernel corpus and the CVE-2020-0423 race, moved to the
CVE-2024-31317 uid-1000 accelerator on A.05, then found the CVE-2020-0041
path that gave runtime root on C.01. The 0423 work became a documented
negative result with a strong lab reproduction.

### Phase 2 — Boot chain (Nov 9 – Nov 12)

Moved from the official Deep Testing route (closed by the server) to the
PBL. Proved programmer acceptance is gated by the outer hash table, proved
PBL-stage execution, measured the boot context, and ran two negative XBL
boot tests. Ended with the storage path blocked in UFS and the XBL
enforcement point unlocalized.

### Phase 3 — Consolidation (Nov 12 – Nov 13)

Recovery, sanitization, tooling, and publication. The K3 and OTA work were
folded in as compatibility/recovery case studies.

## What changed the plan

| Event | Plan change |
|---|---|
| Server rejects RMX1901 | Abandoned the official token route |
| Keymaster `-0xF` | Abandoned RPMB/Keymaster |
| Outer hash table accepted | Focused on programmer auth and PBL execution |
| Boot context type 3 | Realized stock payload is the programmer path |
| UFS hang | Storage-load route blocked in EDL |
| Test A/B0 EDL | Stopped boot-chain writes; returned to read-only probes |
| Runtime root | Enabled read-only dumps and Nightzuku |

## What did not change

The safety rule did not change: no boot-chain write without a tested
recovery, and no claim beyond what was measured.
