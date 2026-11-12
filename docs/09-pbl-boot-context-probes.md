# 09 — PBL boot-context and storage probes

**Result:** at the `segment1:0x970` entry, the PBL boot context has type
**3** and the image descriptor has type **0xA** — the programmer/Sahara
path. Forcing type 1 produces a storage descriptor (type 0), but the
full-boot path returns from handlers 0–2 and then hangs in the UFS load at
`0x30F384` / `0x32104C`. The stock `segment1` payload is therefore the
programmer path, not the storage-XBL path.

| Probe | Question | Result |
|---|---|---|
| Boot-context dump | What context/descriptor does the payload see? | type 3, descriptor `0xA` |
| Descriptor init | What does type 1 produce? | storage descriptor, type 0 |
| Full boot | Can handlers 0–2 load storage? | handlers return; UFS load hangs |
| Storage write | Was anything written? | No |

---

## 1. Why the context matters

The stock `segment1` phase payload calls boot handlers 3–9 with
`x0 = 0x1480FBB0`, the boot context. Those handlers are the boot sequence,
not a programmer-only path. The open question was: **at the payload entry,
is the context set up for the programmer or for the storage boot?**

The answer decides whether a payload can call the storage loader, patch XBL
in DRAM, and jump to SBL1 — the “custom PBL loader” route.

## 2. Boot flow (static)

```text
0x302000  early init: sp=0x1480FBB0, VBAR, call 0x3096E0
0x302050  main path: call 0x30FB70, 0x30213C, 0x3240EC; SCR_EL3; jump 0x30DA38
0x30DA38  boot loop: call 0x30E51C, 0x310B84, 0x31020C, then walk 0x324550
```

The table at `0x324550` is the boot-handler list:

| Index | Handler | Stock `segment1` call |
|---:|---:|---|
| 0 | `0x314600` | — |
| 1 | `0x30DAC4` | — |
| 2 | `0x30C158` | — |
| 3 | `0x30E0AC` | stage 1 |
| 4 | `0x30FBF8` | stage 1 |
| 5 | `0x30E164` | stage 2 |
| 6 | `0x310DB4` | stage 2 |
| 7 | `0x30B3B0` | stage 2 |
| 8 | `0x31117C` | stage 2 |
| 9 | `0x30E58C` | stage 2 |

Handler details:

- `0x30E164` reads `[ctx+4]` (boot device/image type), sets
  `[ctx+0x48] = 0x1480B180` (the image descriptor), and dispatches on types
  `0..5`, `0x7F`, `0x80`, `0x81`.
- `0x30F094` initializes the descriptor: `[desc]=0`, `[desc+0x28]=0`,
  `[desc+0x40]=1`, `[desc+0x4C]=0x7FFFFFFF`, `[desc+0x50]=type`,
  `[desc+0x54]=1`, `[desc+0x68]=0`.
- `0x30F384` is the UFS/storage load: sets `[ctx+0x104] |= 8`, initializes
  the storage, sets `[desc]=0`, `[desc+0x60]=0x1480C388`, and calls the
  storage read path (`0x30D724`, `0x30E580`, `0x30D52C`, then the function
  pointer at `0x324778`).
- `0x30B3B0` is the loader dispatch on `[desc]`: type `0xA` → `0x311768`;
  types `4..7` → `0x3102DC`; other types log an error.
- `0x30E58C` jumps to the loaded image: `blr [ctx+0x1D8]` if `[ctx+0xB8]`
  is set, else `blr [ctx+0x40]`.

## 3. Measured context

The read-only probe copied the `0x220`-byte context at `0x1480FBB0` and the
`0x80`-byte descriptor at `0x1480B180` to `0x14815000`, sent
`PBLCTXPROBE0000` followed by the `0x2A0`-byte block, and looped.

```text
context 0x1480FBB0
  +0x000  0x0000000300000000   ; [0]=0, [4]=3  (boot type 3)
  +0x008  0x0000000000100000
  +0x010  0x0000000014816000
  +0x018  0x00000000148FFFFF
  +0x020  0x00000000000EA000
  +0x028  0x0000000014680000
  +0x030  0x00000000146BFFFF
  +0x038  0x0000000000040000
  +0x048  0x000000001480B180   ; image descriptor
  +0x070  0x0000000014810000
  +0x078  0x0000000014811690   ; relocated trampoline
  +0x080  0x000000001481568F
  +0x090  0x000000000030B870   ; verifier wrapper
  +0x0B0  0x000000000030B198
  +0x0B8  0x0000000100000001   ; [0xB8]=1
  +0x0C0  0x000000000030C38C
  +0x0C8  0x0000000000311208
  +0x1E0  0x0000000000000015
  +0x1E8  0x0000000014699000   ; XBL_SEC image
  +0x1F0  0x00000000000124BC

descriptor 0x1480B180
  +0x000  0x000000000000000A   ; type 0xA = programmer/Sahara
```

The live descriptor at `0x1480B180` is type `0xA` after the oracle, with
`[+0x20]=0x31194C`. Type `0xA` is the programmer/Sahara path.

## 4. Forced storage descriptor

The descriptor-init probe forced type 1, called `0x30F094`, and dumped the
result. The descriptor came back as type 0 — a storage descriptor — with
the fields `0x30F094` is expected to set. That confirms the init function
behaves as statically analyzed.

The full-boot probe then called handlers 0–2 and type 1. Handlers 0–2
returned, but the UFS load at `0x30F384` hung at `0x32104C`. No magic after
that point. The storage-load route is therefore blocked at UFS **in EDL**:
the storage stack is not usable from this state.

This is a host/trigger limitation, not proof that the storage path is
cryptographically blocked.

## 5. What this means

| Question | Answer |
|---|---|
| Is stock `segment1` the programmer path? | **Yes** — type 3, descriptor `0xA` |
| Does forcing type 1 produce a storage descriptor? | **Yes** — type 0 |
| Can the full boot path load storage from EDL? | **No** — UFS hang |
| Is host-loaded XBL acceptance proven? | **No** |
| Is the storage path blocked by auth? | **Not established** |

The earlier claim that “A1 is blocked by layout, not auth” was too strong.
The fixed host sequence is a host limitation, not a loader limit; the PBL's
requests are driven by the served ELF program headers. A different ELF
would need a new host sequence/trigger. Host-loaded XBL acceptance is
**unresolved**.

## 6. Open questions

1. Which storage API/entry can a PBL-stage payload use, and when is XBL
   loaded and verified?
2. What runtime context type and descriptor does the storage path expect at
   payload entry?
3. What are the descriptor/partition fields that select the XBL partition
   and load address?
4. Why does the UFS read hang at `0x32104C` in EDL — clock, power, or
   initialization state?
5. Can the host sequence serve a 16-phdr, `0x380000`-byte C.01 XBL rather
   than the fixed 22-phdr fake ELF?

These are tracked in [OPEN-QUESTIONS](OPEN-QUESTIONS.md).

## 7. Evidence

| Probe | SHA-256 (full) |
|---|---|
| `segment1_bootctx_probe.bin` | `a64bf13422cab1b1a9f07d70fc25e49d688accf8d8843ad6b4e092af7b209537` |
| `bootctx.bin` (captured block) | `2ffa9243b54531d94a4c15638d991272c8b61cf2f2fdc92dd79f57480d19b7a8` |

The descriptor-init and full-boot probe hashes are recorded as prefixes in
the private record; they are not reproduced here. The sanitized context
table is in
[evidence/logs-sanitized/bootctx-2026-11-12.md](../evidence/logs-sanitized/bootctx-2026-11-12.md).

## 8. Limits

- The probes are read-only, but they loop in PBL by design; a cold power
  cycle restores Android.
- `0x1481F000` is used as scratch by the stock payload and by the probes.
  The probes overwrite it without save/restore; this is RAM-only and
  cold-boot recoverable, but within-session side effects are unknown.
- The UFS hang is an EDL-state observation; it does not prove the storage
  path is unusable after a normal boot.

## 9. References

- PBL execution oracle: [08](08-pbl-execution-oracle.md)
- Programmer authentication: [07](07-pbl-programmer-auth.md)
- XBL/ABL authentication: [10](10-xbl-abl-auth-negative-tests.md)
- Companion tooling: <https://github.com/ankitpipalia/pblexp-macos>
