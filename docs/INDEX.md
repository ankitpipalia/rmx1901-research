# Index

Navigation for the RMX1901 research record. Start with the
[overview](00-overview.md) or the [README](../README.md).

## Status

The bootloader is **locked**; verified boot is **green**. No unlock and no
persistent root were achieved. Runtime uid 0 on C.01 is temporary and is
lost on reboot. See [VERIFIED-RESULTS](VERIFIED-RESULTS.md) for the
claim-by-claim evidence table.

## Core write-ups (22 workstreams)

### Android privilege escalation

| # | Document | Outcome |
|---:|---|---|
| 1 | [Runtime root via CVE-2020-0041](01-runtime-root-cve-2020-0041.md) | uid 0, full caps, Permissive — runtime only |
| 2 | [uid 1000 via CVE-2024-31317](02-uid1000-cve-2024-31317.md) | `system_app` shell on A.05 — not root |
| 3 | [CVE-2020-0423 binder UAF](03-cve-2020-0423-binder-uaf.md) | Bug verified; race not won on device |
| 4 | [GhostLock / rtmutex audit](04-ghostlock-audit.md) | Negative; details withheld |
| 5 | [KGSL/Adreno audit](05-kgsl-adreno-audit.md) | Surface reachable; no chain |
| 6 | [Nightzuku/Shizuku as root](06-nightzuku-root-integration.md) | Working with runtime root |

### PBL, EDL and the boot chain

| # | Document | Outcome |
|---:|---|---|
| 7 | [PBL programmer authentication](07-pbl-programmer-auth.md) | Outer hash table is the gate; hash-fixed programmer accepted |
| 8 | [PBL execution oracle](08-pbl-execution-oracle.md) | `0x970` payload executed; USB magic captured |
| 9 | [PBL boot-context probes](09-pbl-boot-context-probes.md) | Programmer path confirmed; storage boot hangs |
| 10 | [XBL/ABL authentication and negative tests](10-xbl-abl-auth-negative-tests.md) | Test A/B0 rejected; stock restored |
| 11 | [Firehose/VIP authorization](11-firehose-vip-audit.md) | VIP off; 17-range whitelist analysed |

### Vendor flows and recovery

| # | Document | Outcome |
|---:|---|---|
| 12 | [CVE-2021-1931 audit](12-cve-2021-1931-audit.md) | Real bug; unreachable on stock C.01 |
| 13 | [Deep Testing token flow](13-deeptest-token-flow.md) | Server rejects model; vendor signature missing |
| 14 | [OPPO K3 cross-flash recovery](14-k3-crossflash-recovery.md) | Repaired; returned to C.01; NV withheld |
| 15 | [OPPO OTA / `.ozip` extraction](15-ota-ozip-extraction.md) | Images extracted and verified; none published |
| 16 | [EDL readback and restore](16-edl-readback-and-restore.md) | Readback verified; restore XML untested |
| 17 | [Backup, GPT and recovery](17-recovery-backup-gpt.md) | Six GPTs verified; recovery validated |

### Research context

| # | Document | Outcome |
|---:|---|---|
| 18 | [Public research and CVE triage](18-public-research-cve-triage.md) | What was validated or ruled out |
| 19 | [Auto-root app](19-autoroot-app.md) | App-context root; lifecycle unresolved |
| 20 | [A.05 downgrade / A.20 corpus](20-a05-downgrade-a20-kernel.md) | Kernel unchanged; user space older |
| 21 | [Closed routes](21-closed-routes.md) | `devinfo`, RPMB, NO_AVB, GBL, token, e=3 |
| 22 | [VM/KASAN lab](22-vm-kasan-lab.md) | 351 UAF reports vs 0 on fixed control |

## Cross-cutting documents

- [Research timeline](RESEARCH-TIMELINE.md)
- [Verified results](VERIFIED-RESULTS.md)
- [Experiment matrix](EXPERIMENT-MATRIX.md)
- [Open questions](OPEN-QUESTIONS.md)
- [Methodology](METHODOLOGY.md)
- [Glossary](GLOSSARY.md)
- [Publication gates](PUBLICATION-GATES.md)

## Evidence and tooling

- [Evidence guide](../evidence/README.md)
- [Hashes of withheld artifacts](../evidence/hashes.md)
- [Sanitized oracle log](../evidence/logs-sanitized/oracle-2026-11-10.md)
- [Sanitized boot-context result](../evidence/logs-sanitized/bootctx-2026-11-12.md)
- [Sanitized Test A failure](../evidence/logs-sanitized/testA-failure-2026-11-12.md)
- [Sanitized B0 rejection](../evidence/logs-sanitized/b0-rejection-2026-11-12.md)
- [Tools](../tools/README.md)
- [Public sources](../references/PUBLIC-SOURCES.md)
- [Upstream credits](../references/UPSTREAM-CREDITS.md)
- [Third-party licenses](../references/THIRD-PARTY-LICENSES.md)

## Reading paths

**If you want the unlock story:** [07](07-pbl-programmer-auth.md) →
[08](08-pbl-execution-oracle.md) → [09](09-pbl-boot-context-probes.md) →
[10](10-xbl-abl-auth-negative-tests.md) → [21](21-closed-routes.md).

**If you want the Android exploit story:** [01](01-runtime-root-cve-2020-0041.md)
→ [02](02-uid1000-cve-2024-31317.md) → [03](03-cve-2020-0423-binder-uaf.md)
→ [22](22-vm-kasan-lab.md).

**If you want the vendor/recovery story:** [13](13-deeptest-token-flow.md)
→ [14](14-k3-crossflash-recovery.md) → [16](16-edl-readback-and-restore.md)
→ [17](17-recovery-backup-gpt.md).

**If you want to know what is *not* true:** [VERIFIED-RESULTS](VERIFIED-RESULTS.md)
and [OPEN-QUESTIONS](OPEN-QUESTIONS.md).
