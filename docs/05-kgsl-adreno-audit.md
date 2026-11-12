# 05 — KGSL / Adreno CVE-2020-11179 audit

**Result:** the KGSL device node is reachable from an unprivileged process,
and the published Qualcomm remediation markers for the Adreno privilege
issue are **absent** from the audited A.20 driver. No verified 4.9 /
Adreno-616 root chain was produced. The finding is deliberately narrow:
**published-fix markers absent**, not “the device is exploitable”.

| Item | Value |
|---|---|
| Target | RMX1901 A.20 kernel `4.9.112-perf+`, Adreno 616 |
| Interface | `/dev/kgsl-3d0`, mode `0666` (reachable) |
| Feature word | `0x000132E0` |
| APRIV bit | Bit 21 clear |
| Remediation markers | M2–M4 absent |
| Exploit | None verified |

---

## 1. Why KGSL was in scope

The GPU driver is a large, historically vulnerable attack surface that is
reachable from the app sandbox. On this device `/dev/kgsl-3d0` is mode
`0666`, so an unprivileged process can open it without a vendor permission.
That makes it a plausible local privilege-escalation surface, and
CVE-2020-11179 is a public Adreno issue in the relevant era.

## 2. What was measured

- The A20 kernel's A616 feature word is `0x000132E0`.
- APRIV (bit 21) is **clear**.
- The published Qualcomm remediation markers M2–M4 are **absent** from the
  driver.
- The device node is present and openable with mode `0666`.

The interpretation is deliberately limited: absent remediation markers mean
the published fix is not present in the driver. They do **not** prove that a
specific published exploit works, that the firmware is vulnerable, or that a
full chain exists.

## 3. Why no chain was produced

| Requirement | Status |
|---|---|
| Reachable device node | Yes |
| Published fix absent | Yes (markers M2–M4 absent) |
| Known 4.9 / Adreno-616 exploit | No verified public chain |
| GPU firmware behaviour | Partly inferred / unknown |
| Address recovery | Not solved |
| Payload delivery | Not solved |

The gap is not the entry point; it is the rest of the chain. A GPU exploit
needs a stable primitive, a way to recover addresses under KASLR, and a
payload that survives the GPU firmware's scheduling and memory management.
None of that was established.

## 4. What would be needed

1. A public or independently derived Adreno-616 primitive for this firmware
   generation.
2. A KASLR/address-recovery strategy that works from the GPU mapping.
3. A payload-delivery method that does not depend on a debugger or root.
4. A device test with a recovery path (the runtime root and EDL programmer
   are available).

Until then, this remains an audit note, not an exploit.

## 5. Limits

- The audit is static and single-build.
- “Markers absent” is not a vulnerability proof.
- GPU firmware was not reversed in this workstream.
- No device crash or exploit test was run for this route.

## 6. Evidence

| Claim | Evidence |
|---|---|
| `/dev/kgsl-3d0` is `0666` | Live device file listing (private) |
| Feature word `0x000132E0` | A.20 driver/kernel analysis |
| APRIV bit 21 clear | Same |
| M2–M4 absent | Driver comparison against published remediation |
| No chain | No verified primitive or test |

## 7. References

- CVE-2020-11179 (Qualcomm Adreno/KGSL).
- A.20 kernel corpus: [20](20-a05-downgrade-a20-kernel.md).
- Public research triage: [18](18-public-research-cve-triage.md).
