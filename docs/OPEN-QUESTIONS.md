# Open questions

These are the questions that were not resolved in this effort. Each entry
states why it matters, the next probe, and the current blocker.

---

## Q1. Which gate rejected the Test A and B0 XBL images?

**Why it matters:** It decides whether the PBL enforces the signed XBL hash
segment, whether SBL1 rejects the image later, or whether the image never
reached the verifier.

**Next probe:** A read-only storage-path probe that records the last
successful stage and the first missing magic, with the stock image as the
control.

**Blocker:** The storage path hangs in UFS from EDL; host-loaded XBL
acceptance is unproven.

---

## Q2. Does the PBL verify the XBL signature on the storage path?

**Why it matters:** If it does, re-hashing the XBL table is insufficient and
the hash-only patching route is closed. If it does not, the rejection is
elsewhere.

**Next probe:** Localize `ctx+0x108`/`ctx+0x120` writers, or instrument the
SMC/auth path after SBL1 starts. Compare a self-consistent re-hash against a
signed stock image.

**Blocker:** The setters are outside the PBL image; no runtime trace of the
storage path was captured.

---

## Q3. Is host-loaded XBL acceptance possible?

**Why it matters:** Path A1 depends on loading a patched XBL from the host,
not from storage.

**Next probe:** Serve a 16-phdr, `0x380000`-byte C.01 XBL with a matching
host sequence and observe whether the PBL reaches the loader dispatch.

**Blocker:** The current host sequence is built around a fixed 22-phdr fake
ELF; the PBL's requests are driven by the served ELF, so a new sequence is
needed.

---

## Q4. Which storage API/entry can a PBL payload use?

**Why it matters:** A custom PBL loader that reads XBL from storage, patches
it in DRAM, and jumps to SBL1 would bypass the storage verification path.

**Next probe:** Decode the descriptor/partition fields of the storage read
`0x30F384` and test a read-only load of the XBL partition from the payload.

**Blocker:** The UFS load hangs in EDL; the partition/LUN fields are not
decoded.

---

## Q5. Why does the UFS load hang at `0x32104C`?

**Why it matters:** If the storage stack can be initialized from EDL, the
storage path becomes testable; if not, it is a dead end for this state.

**Next probe:** Read-only register/clock state at the hang, and compare
against a normal boot's storage init.

**Blocker:** No debugger at PBL stage; the payload can only send USB magics.

---

## Q6. Can the CVE-2021-30327 `0x13` finish payload be ported?

**Why it matters:** It is the most direct EL3 code-execution route that is
statically present on the device.

**Next probe:** Build a PBL-accepted payload (the oracle stub already works),
then port the SDM845 finish stages with the RMX1901 fake-stack pointer and
pivot.

**Blocker:** The first ELF attempt was rejected at `END_IMAGE_TX status=0x28`;
the finish-payload layout is not validated.

---

## Q7. Can a PTE store be made visible to the MMU walk?

**Why it matters:** The shadow-remap primitive depends on changing a PTE and
having the walker see it.

**Next probe:** The staged PTE diagnostic (read → store → text store) with a
magic at each step, plus cache maintenance if needed.

**Blocker:** The earlier AP[2] test was ambiguous; no `PBLPTESTART` means the
payload did not run, not that the PTE page is blocked.

---

## Q8. Does the shadow remap actually flip the flag getter and loader hook?

**Why it matters:** It is the core of the stock `segment1` bypass and the
basis for a storage-boot patch.

**Next probe:** Run the `segment1_shadow_test.bin` payload, check the
`PBLSHADOW*` magics, then add the `0x30E0AC`/`0x30FBF8` calls and the flag
effect.

**Blocker:** Not run; `0x1481F000` is overwritten without save/restore.

---

## Q9. Is CVE-2021-1931 reachable after the token gate?

**Why it matters:** It is a real SD710-listed Fastboot bug; if the parser can
be reached, it is a code-execution primitive in ABL.

**Next probe:** A modified ABL that skips the gate, or a valid token.

**Blocker:** XBL authenticates ABL; a locally patched ABL does not boot.

---

## Q10. Does CVE-2024-31317 apply to C.01?

**Why it matters:** It would give a uid-1000 shell on the main research
build.

**Next probe:** Reproduce the A.05 payload on C.01 in a controlled way, with
a recovery plan for the zygote socket.

**Blocker:** Not tested; C.01 was reserved for the 0041 root and boot-chain
work.

---

## Q11. Can the CVE-2020-0423 race be won with a controlled receiver?

**Why it matters:** It is a fallback root route and a clean binder primitive.

**Next probe:** A receiver that frees the node at a known instant, or a
statistically better harness with `signalfd` pinning and `w->type` detection.

**Blocker:** `addService` is denied to shell, and the context manager is
`EBUSY`/`EACCES`.

---

## Q12. Is there a usable KGSL/Adreno primitive?

**Why it matters:** `/dev/kgsl-3d0` is reachable and the published fix
markers are absent.

**Next probe:** A public or independently derived Adreno-616 primitive, plus
a KASLR/address-recovery strategy.

**Blocker:** No verified 4.9/Adreno-616 chain; firmware behavior unknown.

---

## Q13. Will the vendor respond on Deep Testing / PBL?

**Why it matters:** Coordinated disclosure is the right path for the token
flow and the PBL hash-table behavior.

**Next probe:** Vendor notification with the sanitized findings and a 90-day
window.

**Blocker:** No vendor response yet; details withheld.

---

## Q14. Can the auto-root app survive service teardown and reboot?

**Why it matters:** It is the difference between a research convenience and
a persistent root.

**Next probe:** A user-visible persistent service, or a system-level host.

**Blocker:** Android background restrictions; no bootloader unlock.

---

## Q15. What is the rollback/ARB value?

**Why it matters:** It determines whether A.05/A.20 can be flashed safely and
whether a downgrade is possible.

**Next probe:** Read the ARB value with `sectools`/`secimage` or an equivalent
parser.

**Blocker:** Neither tool was available on the hosts; do not flash older
firmware without it.

---

## Q16. Do the F.01 ABL claims hold?

**Why it matters:** The F.01 report was cited as evidence for an alternative
Fastboot path.

**Next probe:** Obtain the F.01 ABL and compare PE layout, token call graph,
RSA key tables, and `0x50` propagation against C.01.

**Blocker:** The F.01 artifact was not available; its RVAs are not
transferable to C.01.

---

## Q17. Can the VIP predicate be forced off from the payload?

**Why it matters:** It would skip the allow-list, range check, and digest
check together.

**Next probe:** A read-only probe of the SCM return path, then a controlled
test of the predicate.

**Blocker:** VIP is already off on this unit, so the motivation is low; a
different unit may differ.

---

## How to use this list

Pick a question only if you have:

1. the matching build and a recovery path;
2. a read-only probe that distinguishes “payload did not run” from “primitive
   blocked”;
3. a control run with the stock image;
4. a stop condition.

The [METHODOLOGY](METHODOLOGY.md) page describes the discipline.
