# 08 — PBL execution oracle

**Result:** a `segment1` payload placed at offset `0x970` executed after
segment2 and segment3 were served, and sent a USB packet containing
`PBLXORACLE2026!!EXEC-PROOF-0x970`. This is a repeatable proof of
**PBL-stage code execution**. It is not proof of EL3 privilege, not a
persistent modification, and not an unlock.

| Item | Value |
|---|---|
| Entry | `segment1` offset `0x970` |
| Runtime base | `0x149FF000` (relocated) |
| Transport | USB 9008 / Sahara |
| Magic | `PBLXORACLE2026!!EXEC-PROOF-0x970` |
| When | after segment2/3 handoff |
| Meaning | payload code ran at PBL stage |

---

## 1. Why an oracle was needed

During the auth work, it was easy to confuse three different outcomes:

1. the host served the bytes and the PBL accepted the image;
2. the PBL accepted the image but the payload never ran;
3. the payload ran but the host did not see its output.

Without a positive signal from inside the payload, all three look similar in
a serial log. The oracle solves that: it places a unique transmit in the
payload and looks for it after the handoff.

This turned every later probe into a test with a clear “did it run?” answer.

## 2. Payload layout and relocation

The fake programmer ELF maps the payload segment at `p_paddr 0x85e28000`,
but the segment's first instructions are a **trampoline**:

1. copy the phase payload from IMEM `0x14812000` to `0x149FF000`;
2. set `sp = 0x1480FBB0` (the PBL boot stack);
3. branch to `0x149FF000`.

The payload therefore runs **relocated**, not at `0x85e28000`. The
`segment1` file offset `0x970` maps to `0x149FF000` (plus the offset within
the phase area).

Two consequences:

- A fixed `segment1-offset → runtime-address` map is unsafe. The earlier
  specific map (`0xB0C → 0x149FF69C`, etc.) was withdrawn because it was
  internally inconsistent with the `0x149FF000` entry.
- Absolute PBL/IMEM addresses (`0x30B3B0`, `0x30DE40`, `0x1480FBB0`,
  `0x1480C378`) are relocation-immune. PC-relative `bl`/`ret` are also
  safe. `br 0x300B18` is wrong because the payload is at `0x149FF000`, not
  `0x300000`.

## 3. The payload

The oracle payload:

1. runs at `0x149FF000`;
2. calls the PBL transmit helper `0x308B40` with a `0x30`-byte buffer at
   `0x14815000`;
3. sends a packet whose payload begins
   `PBLXORACLE2026!!EXEC-PROOF-0x970`;
4. returns to a safe loop.

The transmit helper is a PBL function, so the payload is using the PBL's own
USB stack. That is why the magic appears on the wire after segment2/3.

## 4. Host sequence

The working `oppo710` sequence is:

| # | Packet | Size | Expected response |
|---:|---|---:|---|
| 0 | initial PBL HELLO (drain) | `0x30` | `01 00 00 00 30 ...` |
| 1 | `Hello710` | `0x30` | `READ_DATA64 image=0xd offset=0 size=0x40` |
| 2 | ELF header | `0x40` | `READ_DATA64 offset=0x40 size=0x4d0` |
| 3 | program headers | `0x4d0` | `READ_DATA64 offset=0x1000 size=0x1000` |
| 4 | segment1 | `0x1000` | `READ_DATA64 offset=0x2000 size=0xbf8` |
| 5 | zero segment | `0xbf8` | `END_IMAGE_TX image=0xd status=0x8` |
| 6 | `0x13` reset | 1 × 175 | one `0x30` HELLO per reset |
| 7 | segment2 | `0x3f0` | no read |
| 8 | segment3 | `0x3a8` | no read |
| 9 | loader reopen | — | new USB address, pending `0x30` HELLO |
| 10 | `LOADER_HELLO` | `0x30` | `READ_DATA64` image requests |
| 11 | programmer data | image | 181 READ_DATA64, `END_IMAGE_TX 0`, `DONE 1` |

The zero segment size is **`0xbf8`**, not `0xbe8`. The `0xbe8` value is a
protocol-arithmetic control; with it the PBL returns a full HELLO instead of
an image-complete acknowledgment, and the USB stack dies near reset 170.

The oracle magic appears after step 8, before the loader reopens. On the
Windows serial path, the COM port is lost after segment3, so the magic must be
captured with a transport that survives the handoff. The macOS libusb path
does, provided the two HELLO drains are handled correctly:

- drain one pending PBL HELLO before the first `Hello710`;
- drain one pending HELLO after the loader re-enumerates, before writing
  `LOADER_HELLO`.

Without the second drain, the host writes `LOADER_HELLO`, gets no
`READ_DATA`, and reports a timeout.

## 5. What the oracle proves

| Claim | Status |
|---|---|
| A payload at `segment1:0x970` executes after segment2/3 | **Measured** |
| The payload can call a PBL function and transmit on USB | **Measured** |
| The payload runs at `0x149FF000` | **Derived** from the trampoline and the observed behavior |
| The payload has EL3 privileges | **Not proven** |
| Code execution persists | **No** |
| Bootloader unlock | **No** |

“PBL-stage code execution” means the payload runs in the PBL's execution
context, before the programmer. The PBL runs at EL3 on this SoC, so this is
a strong position — but privilege is not the same as control of the secure
boot state. The payload did not modify storage, did not change fuses, and
did not survive a power cycle.

## 6. How the oracle was used

The oracle became the control for every later probe:

- **Boot-context probe** — dump the context and descriptor, send
  `PBLCTXPROBE0000` ([09](09-pbl-boot-context-probes.md)).
- **Descriptor-init probe** — force type 1 and dump the descriptor.
- **Full-boot probe** — call handlers 0–2 and type 1, with magics.
- **PTE diagnostic** — read/store the PTE and attempt a text store.
- **Shadow-remap test** — copy a text page to scratch, patch the copy, and
  remap.

If a probe produces no magic, the first question is “did the payload run?”,
not “is the primitive blocked?”. That distinction prevented several false
conclusions.

## 7. Failure modes seen

| Symptom | Meaning |
|---|---|
| No magic, host served all bytes | Payload may not have run, or magic was sent on a lost transport |
| No `PBLPTESTART` | Payload did not run; not evidence the PTE page is blocked |
| COM port lost after segment3 | Windows serial path limitation, not a PBL result |
| `END_IMAGE_TX status=0x28` | Image rejected before the reset loop |
| PBL stuck after a probe | Cold power cycle required; USB replug is not enough |

## 8. Evidence

The captured oracle log is summarized in
[evidence/logs-sanitized/oracle-2026-11-10.md](../evidence/logs-sanitized/oracle-2026-11-10.md).
The original log and the payload binaries are private; their hashes are in
[evidence/hashes.md](../evidence/hashes.md).

## 9. Limits

- The oracle proves execution at PBL stage, not EL3 privilege escalation.
- The payload is RAM-only and is cleared by a cold boot.
- The transport must survive segment3; a serial path that drops the port
  cannot observe the magic.
- The payload relies on PBL addresses that are build-specific. Do not assume
  they apply to another firmware or SoC.

## 10. References

- Companion repository: <https://github.com/ankitpipalia/pblexp-macos>
- Programmer authentication: [07](07-pbl-programmer-auth.md)
- Boot-context probes: [09](09-pbl-boot-context-probes.md)
- XBL/ABL negative tests: [10](10-xbl-abl-auth-negative-tests.md)
