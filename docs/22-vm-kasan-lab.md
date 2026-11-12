# 22 — VM / KASAN lab

**Result:** the CVE-2020-0423 binder use-after-free was reproduced in a
disposable arm64 KASAN VM with the official Realme X binder driver grafted
into Linux 4.9.112. The vulnerable driver produced **351 KASAN UAF reports**
in a 60 s, 64-object workload; the upstream-fixed control produced **0** in
a comparable run. This is the cleanest evidence that the bug, the trigger,
and the fix are understood — even though the device race was never won.

| Item | Value |
|---|---|
| Host | macOS arm64, QEMU 11.1.3, Lima 2.3.0 |
| Guest | Debian 12 arm64, 6 vCPU, 8 GB, GCC 12.2.0 |
| Kernel | Linux 4.9.112 arm64, KASAN outline, Binder |
| Vulnerable run | 2,357,052 sends, **351** KASAN UAF reports |
| Fixed control | 2,581,894 sends, **0** reports |
| Device exploit | Not achieved |

---

## 1. Why a VM lab

The device is the real target, but a race campaign on a phone is slow,
destructive, and hard to instrument. A local KASAN VM makes the bug
deterministic and gives a clean A/B control:

- same kernel base;
- same binder driver;
- same 64-object workload;
- only the vulnerable function differs.

The lab is not a substitute for the device; it is a way to prove the bug and
the fix before spending device cycles.

## 2. First attempt: wrong binder generation

The first lab used vanilla `linux-4.9.112` from kernel.org. That binder is an
older generation with a global `binder_main_lock` and no
`BINDER_WORK_NODE` path. The observed:

```text
binder: unexpected work type, 3, not freed
```

was the old driver's normal fallback, **not** the CVE. The old driver cannot
execute the CVE-2020-0423 interleaving.

This was an important negative result: a reproducer that “hits the function”
is not the same as a reproducer that reaches the vulnerable access.

## 3. Correct graft

A second tree was created by copying vanilla 4.9.112 and replacing only the
Binder driver/UAPI with the official Realme X `master` files:

```text
drivers/android/binder.c
drivers/android/binder_alloc.c
drivers/android/binder_alloc.h
drivers/android/binder_trace.h
drivers/android/binder_alloc_selftest.c
drivers/android/Kconfig
drivers/android/Makefile
include/uapi/linux/android/binder.h
```

The kernel stayed Linux 4.9.112 arm64 with:

```text
CONFIG_KASAN=y
CONFIG_KASAN_OUTLINE=y
CONFIG_ANDROID_BINDER_IPC=y
CONFIG_ANDROID_BINDER_DEVICES="binder"
```

Two local-only edits, both outside the vulnerable logic:

1. **Build compatibility:** the Realme module-parameter callback takes
   `const struct kernel_param *`; vanilla 4.9's `module_param_call()`
   expects the non-const form. Remove `const` from
   `binder_set_stop_on_user_error()`.
2. **Log capture:** change the `unexpected work type` fallback from `pr_err`
   to `pr_debug` and boot with `binder.debug_mask=0`, so thousands of
   fallback lines do not drop the KASAN report from the console. The UAF was
   also observed on the unmodified `pr_err` build; the logging change is not
   required for the bug.

## 4. Identifier hashes

| Artifact | SHA-256 |
|---|---|
| `linux-4.9.112.tar.xz` | `60ec294e6aaaa20f496c0f7efc08132508371ea053d6f2729a88031171f6f0de` |
| VM `.config` | `3d009bb50ffa13d8af978ea6406efaed65e1499c2e3d0c88f6d621bc10aa208b` |
| Realme `binder.c` pristine | `3dc893f7d108971c0f38230ba7141a5c14b0c97ddfd96613e33e605090c35a50` |
| Realme `binder.c` clean-log | `225a8bf1b6615fa4a288bd25a5c06305f246f4015d44d78394ff1fc0a7063bca` |
| Realme `binder.c` fixed | `6ff5ad51f03263858ea69fc9d72f99fd466722709feed99fdf430354fe0768fc` |
| `binder_alloc.c` | `063664d0237c29dbd39932168f4f5d8a0159156c090320c3443263323d0211b7` |
| UAPI `binder.h` | `bcd2f594322712ac561e56e6872290e013d3480ffbd296e69c622f51d3838996` |
| Upstream fix patch | `d8db6b72ce34caf5bd90d47b4a8fb67dac7d1a5550cafa081dec19fdf2434cb9` |
| Clean-log patch | `b9e95c46a8a54a4c55a33a8933a1d880c669bf25c4f357c738efb3793f7b8b72` |
| 50 ms lab window patch | `67e81e47e14c62f48182151d079dd11873b4bf89011224f06f061e9c0ac507a1` |
| Fixed-vs-cleanlog diff | `d8eee9f8dd315c5fa884ae4daea57569d3f745e7864eb8c3855e62b37c21152b` |

## 5. Build

```sh
make ARCH=arm64 HOSTCFLAGS="-fcommon" \
     KCFLAGS="-fcommon -Wno-error" -j6 Image
```

GCC 12 requires the `-fcommon` workaround for the 4.9 `dtc` common symbols.

## 6. Workload and A/B

Both runs used the same command and the same 64-object initramfs:

```sh
qemu-system-aarch64 -M virt -cpu host -accel hvf -m 2048 -smp 4 \
  -kernel Image-realme-cleanlog   # or Image-realme-fixed \
  -initrd initramfs-realme-obj64.cpio.gz \
  -append "console=ttyAMA0 rdinit=/init panic=-1 binder.debug_mask=0" \
  -nographic -no-reboot
```

Harness settings:

```text
CM_HOLD_US=0
LB_OBJECTS=64
LB_WAIT=0
LB_TRIG=2
LB_SPRAY=0
LB_SPRAY_MODE=0
LB_PREEMPT=2
LB_TIMEOUT=60
```

Results:

| Kernel | Sends | KASAN UAF reports | Log SHA-256 |
|---|---:|---:|---|
| `Image-realme-cleanlog` (vulnerable) | 2,357,052 | **351** | `082e06ccdf2d7b3ba6caed52d901fd8c42e2630b0f2fb897127ae234cca2e99f` |
| `Image-realme-cleanlog` repeat (20 s) | — | **112** | `d1c0b614e025dd77416b2a288e0ceef7dca1f36bdadfd371ff48046fed82b38d` |
| `Image-realme-fixed` (patched) | 2,581,894 | **0** | `33f8b44952fb0486717fbc93b23d832c6adac9716722f739b95fde947dfacdbe` |

The fixed control produced no `BUG:`, `WARNING:`, `Oops`, or panic, and
powered down cleanly.

## 7. Instruction-level check

- **Fixed:** `ldr w20, [x19, #16]` at `+0xb4`, then `_raw_spin_unlock` at
  `+0xc0`; the switch uses the saved `w20`.
- **Vulnerable:** `_raw_spin_unlock` at `+0xb4`, then `ldr w2, [x19, #16]`
  at `+0xc0` — the KASAN UAF site.

This matches the source-level fix: read `w->type` under the lock, then
switch on the saved value, and add a `BINDER_WORK_NODE` no-op.

## 8. What the lab does and does not prove

| Claim | Status |
|---|---|
| The Realme binder has the CVE-2020-0423 shape | **Measured** (source + disassembly + KASAN) |
| The trigger reaches the vulnerable access | **Measured** (351 reports) |
| The upstream fix removes the UAF | **Measured** (0 reports) |
| The device race can be won | **Not proven** |
| The post-race chain works on 4.9 arm64 | **Not proven** |
| The device is rooted via 0423 | **No** |

The lab proves the bug and the fix. It does not prove exploitability on the
device, which requires the race and the post-race chain.

## 9. Caveats

- The lab kernel is vanilla 4.9.112 plus the Realme binder, not the exact
  device kernel. Vendor patches outside binder are not represented.
- KASAN changes timing and memory layout; a race that reproduces in KASAN is
  not guaranteed to win on the device.
- The QEMU `virt` machine has no SDM710-specific secure firmware, GPU, or
  storage. It is a binder test rig, not a device model.
- The vendor source and images are not published; the hashes above identify
  them.

## 10. Reproducibility

1. Fetch vanilla 4.9.112.
2. Apply the Realme binder files.
3. Apply the build-compatibility edit and, for clean logs, the
   `pr_err` → `pr_debug` patch.
4. Build with `-fcommon`.
5. Boot with the 64-object initramfs under QEMU/HVF.
6. Run the same workload on the fixed tree as the control.

The exact host paths and VM names are private; the recipe above is enough to
rebuild the experiment with the same public sources.

## 11. References

- CVE-2020-0423: [03](03-cve-2020-0423-binder-uaf.md)
- A.05/A.20 kernel context: [20](20-a05-downgrade-a20-kernel.md)
- Upstream fix: `f3277cbfba763cd2826396521b9296de67cf1bbc`
- Realme kernel source:
  `realme-kernel-opensource/realmeX-kernel-source`
