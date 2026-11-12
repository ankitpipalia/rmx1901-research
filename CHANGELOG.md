# Changelog

## 2026-11-13 — initial public research record

- Published the sanitized 22-workstream research record for the Realme X
  `RMX1901EX` (SDM710).
- Added the CVE-2020-0041 C.01 runtime-root write-up, including the
  device-specific `mm->pgd`, `task_struct::stack`, and `oppo_root_check`
  details.
- Added the CVE-2024-31317 A.05 uid-1000 write-up and its scope limits.
- Added the CVE-2020-0423 negative-result and KASAN-lab record.
- Added the PBL programmer-auth, execution-oracle, and boot-context probe
  write-ups.
- Added the XBL/ABL authentication analysis and the failed Test A / B0
  boot experiments.
- Added the Firehose/VIP authorization audit and the readback/restore
  procedure.
- Added the CVE-2021-1931 audit, the Deep Testing protocol summary, and the
  OPPO K3 cross-flash recovery case study.
- Added offline analysis and validation tools with synthetic-fixture unit
  tests.
- Added sanitized evidence excerpts and SHA-256 hashes of withheld
  artifacts.

## Scope notes for this release

- The bootloader remains locked; no unlock is claimed.
- GhostLock details are withheld pending disclosure.
- Deep Testing endpoints, key arrays, and token bytes are withheld pending
  vendor review.
- K3 NV/IMEI repair values and procedures are withheld.
- Firmware, OTA packages, APKs, signed programmers, boot-chain images, and
  device backups are not published.
