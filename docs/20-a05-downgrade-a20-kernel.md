# 20 — A.05 downgrade and the A.20 kernel corpus

**Result:** A.05 is the oldest RMX1901 Android 9 build, but it is **not** a
kernel-exploit reset. Its kernel (`4.9.112`) is the same generation as A.20,
and the binder, epoll, and rtmutex code is instruction-identical. What the
downgrade changes is **user space**: 18 months of Android/vendor patches and
an older WebView. It does **not** weaken the bootloader token gate or AVB.

| Item | A.05 | A.20 |
|---|---|---|
| Android | 9 | 10 |
| Build date | 2019-07-04 | 2020-07-16 |
| System/vendor patch | 2019-06-05 | 2020-12-05 |
| Kernel | `4.9.112-perf+` | `4.9.112-perf+` |
| WebView / Chrome | 72.0.3626.121 (2019-03) | 2020 build |
| Bootloader | locked / green | locked / green |

---

## 1. Why A.05 was tried

A.05 is older, so it might be expected to have more unpatched kernel bugs.
The question was whether downgrading would create a materially better kernel
exploit surface. The answer is no: the kernel is the same 4.9.112 base, and
the relevant code is the same.

## 2. Measured baseline

A.05 live values:

```text
Build          RMX1901EX_11_A.05
Fingerprint    Realme/RMX1901/RMX1901:9/PKQ1.190101.001/1559614445:user/release-keys
Android / SDK  9 / 28
Patch          2019-06-05
Kernel         4.9.112-perf+ #2 SMP PREEMPT Thu Jul 4 02:16:01 CST 2019
ro.build.type  user
ro.debuggable  0
ro.secure      1
SELinux        Enforcing, policy 30, shell u:r:shell:s0
Verified boot  green
Bootloader     locked (ro.boot.flash.locked=1)
Verity         enforcing
Encryption     encrypted, file-based
WebView        72.0.3626.121 (March 2019)
```

`/proc/kallsyms`, `/proc/cmdline`, most `/proc/sys/kernel/*`, and
`/proc/slabinfo` are permission-denied to shell. `perf_event_paranoid=3`.
`kptr_restrict`/`dmesg_restrict` are active in effect; there is no kernel
address oracle from the shell.

## 3. Kernel delta

The binder, epoll, and rtmutex code is **instruction-identical** between
A.05 and A.20; only debug-string offsets differ in three binder functions.
The A.20 corpus's kernel verdicts therefore carry over:

| CVE | A.05 status | Basis |
|---|---|---|
| CVE-2019-2215 | PATCHED | Same post-fix shape as A.20 |
| CVE-2020-0030 | PATCHED | Same post-fix shape |
| CVE-2020-0041 | N/A | Same pre-refactor code; the bug is in a different binder path |
| CVE-2020-0423 | **UNPATCHED** | Same pre-fix shape; primary kernel LPE candidate |
| CVE-2020-0466 | UNPATCHED | Same pre-fix epoll shape; no public LPE |
| GhostLock / rtmutex | Same address | Pattern unchanged; no working exploit |
| CVE-2020-11179 (KGSL) | Same base/config | A.20 audit is the reference; no chain |

The A.05 kernel was also used for the CVE-2024-31317 uid-1000 work
([02](02-uid1000-cve-2024-31317.md)), because the older framework still
allowed the setting write and the zygote path.

## 4. User-space delta

The downgrade removes 18 months of patches:

- Android framework/media/Bluetooth vendor blobs from June/July 2019;
- Chrome/WebView 72.0.3626.121 (March 2019);
- GMS 15.0.90 (2019-07-03);
- an older framework that still permits the settings/Zygote primitive.

This is a real attack-surface difference, but it is a **user-space** delta.
It does not change the bootloader, AVB, verity, SELinux, or the kernel's
exploitability class.

## 5. Bootloader delta: none

A.05, A.20, and C.01 ABLs were LZMA-decompressed and compared. All three
contain the same 316-byte verifier shape (`+0x1fe=0x55`, `+0x1ff=0xaa`,
`+0x1c2=0xee`) and the same TEE call. The Android 9 A.05 bootloader is
**not** weaker; a downgrade would not remove the token gate.

This is why the Deep Testing route does not improve by downgrading
([13](13-deeptest-token-flow.md)).

## 6. The A.20 kernel corpus

A local corpus of A.20 kernel artifacts was built for static analysis:

- `vmlinux` with symbols;
- Binder, epoll, rtmutex, KGSL, and SELinux code;
- structure offsets and symbol addresses;
- cross-checks against the A.05 and C.01 builds.

The corpus supplied the structure offsets for the CVE-2020-0423 work and the
KGSL audit. It is reference material, not a device exploit.

## 7. VM lab

The exact kernel is Qualcomm/SDM710-specific and is not a faithful generic
QEMU `virt` guest. No exact-binary VM boot or exploit test succeeded. The
retained VM work supports:

- static analysis of the vendor source;
- a generic 4.9.112 source model with the Realme binder grafted in;
- the CVE-2020-0423 KASAN reproduction ([22](22-vm-kasan-lab.md)).

The VM is not a substitute for the device.

## 8. What the downgrade did and did not do

| Claim | Result |
|---|---|
| A.05 has a different kernel generation | **No** — same 4.9.112 |
| A.05 has more unpatched kernel bugs | **No evidence**; relevant code is identical |
| A.05 has older user space | **Yes** — 18 months |
| A.05 weakens the bootloader token gate | **No** — same verifier and TEE call |
| A.05 disables AVB/verity/SELinux | **No** |
| A.05 enables persistent root | **No** |

## 9. Limits

- The comparison is static and single-device.
- “Instruction-identical” was checked for the named functions, not the whole
  kernel.
- The user-space delta was not exhaustively enumerated.
- The VM lab does not reproduce the device's secure boot or vendor
  firmware.

## 10. Evidence

- A.05/A.20 build properties and kernel hashes (private).
- Binder/epoll/rtmutex disassembly comparison (private).
- ABL decompression and verifier comparison (private).
- Binder lab: [22](22-vm-kasan-lab.md).

## 11. References

- A.05 downgrade security note (private).
- Kernel corpus notes (private).
- CVE-2024-31317: [02](02-uid1000-cve-2024-31317.md).
- CVE-2020-0423: [03](03-cve-2020-0423-binder-uaf.md).
- KASAN lab: [22](22-vm-kasan-lab.md).
