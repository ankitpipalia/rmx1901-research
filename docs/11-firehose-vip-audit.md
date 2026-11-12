# 11 — Firehose / VIP authorization audit

**Result:** the accepted programmer implements stock Qualcomm Firehose with
a 16-command dispatch table. VIP authorization is decided in EL3 through SCM
`0x82000119`. On this unit VIP is **off**, so the programmer performs
unrestricted writes. The static VIP allow-list and 17-range `program`
whitelist are real, but they are inactive here.

| Item | Value |
|---|---|
| Image | accepted `devprg_710` programmer |
| Firehose segment | program header 2, RX, entry `0x1484aa40` |
| Dispatch table | 16 entries at `0x1489b428` |
| VIP predicate | SCM `0x82000119`, single `smc #0` |
| VIP state on this unit | **off** |
| Live consequence | unrestricted Firehose writes |

---

## 1. Where Firehose lives

The Firehose server is the **main program** (program header 2, RX, entry
`0x1484aa40`), not the embedded XBL_SEC component. The command names, the
dispatch table, and all handlers are in that segment.

## 2. Command dispatch table

16 entries of `{char *name; void *handler}` at virtual address
`0x1489b428`:

| # | Command | # | Command |
|---:|---|---:|---|
| 0 | `program` | 8 | `firmwarewrite` |
| 1 | `read` | 9 | `getstorageinfo` |
| 2 | `nop` | 10 | `benchmark` |
| 3 | `patch` | 11 | `emmc` |
| 4 | `configure` | 12 | `ufs` |
| 5 | `setbootablestoragedrive` | 13 | `fixgpt` |
| 6 | `erase` | 14 | `getvar` |
| 7 | `power` | 15 | `dump` |

`ufs` and `fixgpt` share a handler. `setbootablestoragedrive` is a
Motorola-specific addition; the image is Motorola OEM-signed.

## 3. VIP is decided in EL3

The programmer does not decide whether VIP applies. Its predicate calls SCM
function `0x82000119` through the image's **single** `smc #0` instruction
and uses the returned value.

- **VIP off:** dispatch directly.
- **VIP on:** only nine commands are allowed:
  `program`, `read`, `nop`, `configure`, `setbootablestoragedrive`,
  `power`, `getstorageinfo`, `getvar`, `dump`.
  Everything else logs `handler %s is restricted!` and fails.

`program` is additionally checked against a 17-entry
`{lun, start, length}` table, and each received packet is hashed against a
host-supplied signed digest table (`VIP hash table accepted %d packet %d`).

## 4. The whitelist excludes the unlock-relevant partitions

Mapping the 17 ranges onto the device GPT:

| LUN | Allowed ranges cover | Not covered |
|---:|---|---|
| 0 | `ssd`, head and part of `persist` | `misc`, `keystore`, `system`, `userdata` |
| 1 | head of `xbl` only | rest of `xbl`, `xbl_config` |
| 2–3 | `last_parti`, `cdt`, `ddr`, alignment areas | — |
| 4 | heads of `aop`, `tz`, `hyp` | **`abl`**, `boot`, `modem`, `devinfo`, `vbmeta`, `recovery` |
| 5 | `oppodycnvbk` head | `opporeserve*`, `modemst*` |

Even with a valid signed digest table, `program` cannot write `abl`, `boot`,
`devinfo`, or `vbmeta` while VIP is enforced. That closes the “flash a
modified ABL” route at the programmer layer.

## 5. Generic Qualcomm VIP, not OPPO's variant

The image contains:

- `VIP is enabled, receiving the signed table of size %d`
- `Number of VIP hashes %d on initial table`
- `VIP hash table accepted %d packet %d`
- the `MaxDigestTableSizeInBytes` configure parameter.

It does **not** contain OPPO's `EnableVip`, `sha256init`, or `getsigndata`,
which appear in OPPO-specific VIP implementations. This is the stock
Qualcomm mechanism.

## 6. Live result: VIP is off — and the probe erased LUN 0

A dispatcher probe sent `erase` expecting a VIP refusal. The programmer
executed it:

```text
Erasing the whole disk/LUN 0
UFS Format whole LUN
ACK
```

It formatted LUN 0. Recovery writes then succeeded without any digest table.
Conclusion: EL3 reports VIP off for this device/state, and the programmer
performs unrestricted writes.

This was an **operational mistake**, not a planned destructive test. It cost
a full LUN 0 restore. The device was recovered from the C.01 OTA and its own
C.01 state dumps; userdata had to be formatted. The event is recorded here
because it is directly relevant to the safety case for Firehose tooling:

- a read-only intent is not enough if the probe sends a write command;
- VIP state must be established **before** sending any destructive command;
- a tested recovery path must exist before the probe.

The recovery details are in [17](17-recovery-backup-gpt.md).

## 7. Three barriers

The hash-table bypass only clears the first:

1. **PBL acceptance of the programmer** — bypassed by fixing the outer
   SHA-256 table ([07](07-pbl-programmer-auth.md)).
2. **Firehose authorization** — VIP, decided in EL3, enforced by the
   dispatcher, the range table, and the digest table. Off on this unit.
3. **Persistent boot chain** — XBL authenticates ABL; ABL keeps unlock state
   in RPMB ([10](10-xbl-abl-auth-negative-tests.md)).

The next candidate is not another hash patch but the VIP predicate: forcing
it to report “VIP off” would skip the allow-list, the range check, and the
digest check together. Whether EL3 or the storage stack enforces anything
further is unknown and would have to be tested read-only before any write.

## 8. What this does and does not prove

| Claim | Status |
|---|---|
| The programmer is stock Qualcomm Firehose | **Derived** from strings and handler structure |
| VIP is decided in EL3 by SCM `0x82000119` | **Derived** from static analysis |
| The 17-range whitelist excludes `abl`/`boot`/`devinfo` | **Derived** from the table and GPT |
| VIP is off on this unit | **Measured** (unrestricted erase succeeded) |
| VIP can be forced off from the host | **Not attempted** |
| A modified ABL can be flashed through Firehose | **No** while VIP is on; **yes** while off, subject to XBL auth |

The last row is important: VIP off means Firehose will **write** the bytes,
but it does not mean the device will **boot** them. XBL authentication is a
separate barrier.

## 9. Evidence

- Static audit: dispatch table, strings, SCM predicate, range table.
- Live probe: `Erase` ACK and LUN 0 format log (private; sanitized excerpt in
  [evidence README](../evidence/README.md)).
- Recovery: C.01 OTA restore and verified GPTs
  ([17](17-recovery-backup-gpt.md)).

The programmer image is not published; its SHA-256 is in
[evidence/hashes.md](../evidence/hashes.md).

## 10. Limits

- The audit is static plus one live probe; the VIP predicate was not
  instrumented.
- The range mapping is inferred from the table and the GPT; the exact
  partition boundaries may differ for other builds.
- “VIP off” is a property of this device/state, not a universal SDM710
  claim.
- The LUN 0 erase was destructive; it is documented as a mistake, not a
  recommended procedure.

## 11. References

- Companion repository: <https://github.com/ankitpipalia/pblexp-macos>
  (`docs/FIREHOSE-VIP.md`)
- PBL programmer auth: [07](07-pbl-programmer-auth.md)
- XBL/ABL authentication: [10](10-xbl-abl-auth-negative-tests.md)
- Recovery: [17](17-recovery-backup-gpt.md)
