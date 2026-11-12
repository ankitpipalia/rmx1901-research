# 04 — GhostLock / rtmutex audit (withheld)

**Status:** the workstream was performed as a static audit of the OPPO K3
4.9.186 kernel and a feasibility check on the RMX1901 4.9.112 kernel. It did
**not** produce a working exploit. The technical details are **withheld**
pending public release of the report and any vendor advisory.

This page exists so the workstream is not silently missing from the record.
It intentionally contains no trigger, primitive, offset, or exploit
instructions.

---

## 1. What can be said

| Item | Statement |
|---|---|
| Class | rtmutex / priority-inheritance lifetime issue in the futex path |
| Targets examined | OPPO K3 `4.9.186`, RMX1901 `4.9.112` |
| Method | Static source and binary audit; two gate checks |
| Gate 1 | Passed on the audited kernels (the relevant PI path is unconditional) |
| Gate 2 | **Failed** on the audited kernels; the stack-overlay assumption does not hold |
| Exploit produced | No |
| Device test | None; no trigger was run |
| Disclosure | Withheld until the report and vendor advisory are public |

The negative result is useful: a public technique that works on newer
kernels does not automatically transfer to a 4.9 arm64 device. Gate 2 was
measured, not assumed.

## 2. Why the details are withheld

- The underlying report was not public at the time of writing.
- A vendor advisory may still be pending.
- Publishing a partial trigger without the full context would be more
  dangerous than useful.
- The workstream produced no exploit, so withholding the details does not
  remove a verified capability from the public record.

## 3. What would change this

The page will be expanded when:

1. the report is public, or
2. the vendor confirms that disclosure is acceptable, or
3. the embargo period ends.

At that point the page will include the audit method, the gate definitions,
the measured reason Gate 2 fails on 4.9, and the negative result, but still
not a weaponized trigger.

## 4. Relation to the rest of the work

- The audit was part of the kernel-exploit triage described in
  [18](18-public-research-cve-triage.md) and
  [20](20-a05-downgrade-a20-kernel.md).
- The primary runtime root came from CVE-2020-0041
  ([01](01-runtime-root-cve-2020-0041.md)), not from this workstream.
- The KASAN lab ([22](22-vm-kasan-lab.md)) is the reusable kernel-testing
  infrastructure that would be used to validate a future trigger.

## 5. References

- Public rtmutex/futex literature (not linked here while the report is
  under embargo).
- Kernel hardening and disclosure policy: [SECURITY.md](../SECURITY.md).
