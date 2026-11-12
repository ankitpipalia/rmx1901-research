# 07 — PBL programmer authentication bypass

**Result:** the PBL gate that accepts a Sahara/Firehose programmer is the
**outer 22-entry SHA-256 table**, not the OEM PKI leaf and not the nested
XBL_SEC table. A programmer with a one-byte payload change and a recomputed
outer hash was accepted on hardware. The outer-only control (inner table
left stale) was also accepted, which shows the inner table is not enforced
before the programmer runs.

This is a **programmer-loading** bypass. It is **not** a bootloader unlock.
No partition write was made for this result, and the device stayed
`flash.locked=1`.

| Item | Value |
|---|---|
| Target | RMX1901 C.01, SDM710 |
| Transport | Qualcomm 9008 (`05c6:9008`), Sahara |
| Image | signed `devprg_710` programmer |
| Gate | outer 22-entry SHA-256 table at file `0x1028` |
| Modified segment | `phdr[21]`, entry 21 at file `0x12c8` |
| Result | hash-fixed programmer accepted |
| Unlock? | No |

---

## 1. The boot path in one page

```text
Power on
  -> PBL (boot ROM, EL3)
     -> Sahara over USB 9008
        -> host sends a programmer ELF
        -> PBL authenticates the programmer
        -> programmer runs Firehose
           -> host sends read/program/erase commands
```

The PBL is the first code that runs. It is small, runs at EL3, and its USB
stack is the only interface before a programmer is loaded. The programmer is
a signed ELF that implements the Firehose command server.

The question for this workstream was: **what exactly does the PBL check
before it runs the programmer?**

## 2. The outer hash table

The accepted `devprg_710` carries a 22-entry SHA-256 table at file offset
`0x1028`:

| Entry | Meaning |
|---:|---|
| 0 | ELF header hash |
| 1 | zero (the hash segment itself is skipped) |
| 2–21 | SHA-256 of each program-header segment |

Entry 21 at file `0x12c8` is the SHA-256 of the programmer executable
segment (`p_filesz` bytes exactly).

The table is **not self-checked**. The outer RSA-signature verifier sits
behind a PKI gate that is not reached on this path, so the outer hash is
effectively unsigned here. That is the core weakness: the PBL compares the
segment to a table, but the table itself is not authenticated in the path
the device takes.

## 3. The nested XBL_SEC table

`phdr[21]` is itself an ELF64 image: a Qualcomm QTI-signed XBL_SEC
component with its own 6-entry hash table at embedded `0x1b8`.

The one-byte payload change (`CRM` → `DRM`) is inside that embedded image's
`phdr[5]`, so it invalidates **both** tables:

- inner entry [5] becomes stale;
- outer entry 21 becomes stale.

Two candidates were built:

| Image | Outer table | Inner table | Hardware |
|---|---|---|---|
| signed `devprg_710` | OK | OK | accepted (control) |
| `devprg_710_mod.bin` (one byte) | stale | stale | rejected at `END_IMAGE_TX` |
| `devprg_710_mod_hashfix.bin` (outer only) | OK | **stale** | **accepted** |
| `devprg_710_mod_hashfix2.bin` (double fix) | OK | OK | **accepted** |

The outer-only control is the decisive experiment. If the inner table were
enforced before the programmer ran, the outer-only image would have been
rejected. It was accepted, with the same success signature as the signed
control:

```text
181 READ_DATA64 requests
END_IMAGE_TX image=0xd status=0
DONE_RESP status=1
```

The unpatched modified image served all 181 requests and then reset before
`END_IMAGE_TX`/`DONE_RESP`. Serving the bytes is not acceptance; the
`END_IMAGE_TX status=0` + `DONE status=1` pair is.

## 4. Cross-OEM certificate chain

The accepted `devprg_710` is not OPPO-signed. It carries six certificates:

| Offset | Subject |
|---|---|
| `0x13e8` | Motorola Attestation 707-1-4 (leaf) |
| `0x18bd` | Motorola Attestation CA 707-1 |
| `0x1c94` | Motorola Root CA 707 |
| `0x972f4` | CASS - CSMS 2.0 (Qualcomm XBL Sec leaf) |
| `0x978aa` | XBL Sec Attestation Root SubCA 1 |
| `0x97cf8` | XBL Sec Attestation Root CA |

The two Qualcomm moduli are byte-identical to the C.01 XBL Sec chain:

```text
XBL C.01 0x285f9e  042f46b6a177674e935130f737845163ca7e6e47f8d2769001e56bea9491f4dc
devprg   0x978aa   042f46b6a177674e935130f737845163ca7e6e47f8d2769001e56bea9491f4dc

XBL C.01 0x2863ec  a3767dde8e4e210feaf056cefef3df514a432ee662edad8605d7a1db269b78c6
devprg   0x97cf8   a3767dde8e4e210feaf056cefef3df514a432ee662edad8605d7a1db269b78c6
```

The PBL accepted an image whose **leaf** is a Motorola attestation
certificate. Combined with the outer-only hash fix, this shows the outer
table is the gate, not the OEM PKI leaf. That is leaf-level cross-OEM
acceptance — the practical shape of CVE-2019-2338 — although the exact
chain the PBL selected is still unproven.

This finding should be read carefully: it does not mean “any certificate
works”. It means the OEM leaf is not the deciding factor on this path; the
outer hash table is.

## 5. What this does and does not prove

| Claim | Status |
|---|---|
| A hash-fixed modified programmer is accepted | **Measured on hardware** |
| The inner XBL_SEC table is not enforced before execution | **Measured** (outer-only control accepted) |
| The outer table is not self-checked in this path | **Derived** from static analysis and the accepted stale signature |
| The OEM leaf is not the gate | **Measured** (Motorola leaf accepted) |
| Arbitrary code execution at EL3 | **Not proven** |
| Bootloader unlock | **Not achieved** |
| Persistent modification | **Not achieved** |

The accepted programmer ran its normal Firehose server. The bypass is about
**what image the PBL will load**, not about gaining EL3 privileges. A
modified programmer that runs at the same privilege as the signed one is
still a programmer; it is not an EL3 exploit.

## 6. Why the outer hash is not a signature

A hash table answers “does this segment match this digest?” It does not
answer “who produced this table?” If the table is not covered by a signature
that the PBL verifies before use, an attacker who can modify the image can
also modify the table. That is exactly what the hashfix does.

The static analysis found the outer RSA verifier behind a dead PKI gate on
this path. The hardware result is consistent with that: the outer signature
was stale in both accepted candidates and the PBL did not reject them.

## 7. What came next

Programmer acceptance is only the first barrier. The accepted programmer
still authorizes individual Firehose commands through VIP, which is decided
in EL3. On this unit VIP is **off**, so the programmer performs unrestricted
writes. See [11](11-firehose-vip-audit.md).

The next barrier is the persistent boot chain: XBL authenticates ABL through
SBL1, and ABL keeps unlock state in RPMB. See
[10](10-xbl-abl-auth-negative-tests.md) and [21](21-closed-routes.md).

## 8. Evidence

| Claim | Evidence |
|---|---|
| Outer table layout | Static parse of `devprg_710` |
| One-byte modification rejected unpatched | `END_IMAGE_TX` reset |
| Outer-only fix accepted | 181 READ_DATA64 + `END_IMAGE_TX 0` + `DONE 1` |
| Double fix accepted | Same |
| Inner table not enforced | Outer-only control accepted with stale inner entry |
| Certificate chain | Certificate subjects and matching moduli |
| No unlock | `flash.locked=1` after the runs |

Hashes of all programmer images are in
[evidence/hashes.md](../evidence/hashes.md). The images themselves are not
published.

## 9. References

- Companion repository: <https://github.com/ankitpipalia/pblexp-macos>
  (transport, host sequence, hashfix builders, evidence).
- CVE-2019-2338 (NVD): cross-OEM trust-boundary issue; SDM710 listed.
- Firehose/VIP: [11](11-firehose-vip-audit.md).
- PBL execution oracle: [08](08-pbl-execution-oracle.md).
- Boot-context probes: [09](09-pbl-boot-context-probes.md).
