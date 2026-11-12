# 19 — Auto-root app and boot persistence

**Result:** a minimal Android app was built that runs the CVE-2020-0041
port from **app context**, obtains root, and starts the root daemon. App
context root was proven. Daemon survival after service teardown and reliable
boot-time re-root were **not** fully solved. The app source and native
libraries are **not published** in this repository.

| Item | Value |
|---|---|
| Package | `com.rmx.autoroot` (research build) |
| Components | activity, foreground service, boot receiver (disabled in the first test) |
| Payload | user-supplied CVE-2020-0041 port (`libpoc.so` in the private build) |
| Result | app-context root; daemon started |
| Persistence | **Unresolved** |
| Published | Design and lessons only |

---

## 1. Why an app

The runtime root from CVE-2020-0041 is obtained by a native process. Running
it from an app is attractive because:

- the app can request the exploit at boot (with a boot receiver);
- the app can keep a foreground service alive;
- the app can ship its payload in `lib/arm64-v8a/`, which is readable and
  executable by the app's uid;
- the app can start the root daemon with a proper Android environment.

The goal was a repeatable “re-root after boot” path for research
convenience, not a consumer root product.

## 2. Design

```text
MainActivity
  -> startForegroundService(RootService)
     -> run libpoc.so from nativeLibraryDir
        -> exploit obtains uid 0
        -> stage script writes /data/local/tmp
        -> starts surootd with a full Android environment
           -> su client connects to the socket
BootReceiver (disabled in the first test)
  -> startForegroundService(RootService) after BOOT_COMPLETED
```

The service creates a low-importance notification channel and calls
`startForeground`, so Android is less likely to kill it. The exploit runs on
a worker thread. The stage script exports `ANDROID_ROOT`, `ANDROID_DATA`,
`ANDROID_RUNTIME_ROOT`, `ANDROID_TZDATA_ROOT`, `BOOTCLASSPATH`,
`DEX2OATBOOTCLASSPATH`, and `SYSTEMSERVERCLASSPATH` before starting the
daemon.

## 3. App-context root

Running the exploit from an app is different from running it from a shell:

- the app's SELinux domain and uid are different;
- the app may not have the same file access;
- the vendor `oppo_root_check` wrapper behaves differently for app-context
  credential changes;
- `setgid`/`setuid` from an app can hang or be denied in ways a shell does
  not see.

The working approach used **direct credential writes** through the exploit's
arbitrary write, avoiding the app-context `setgid` hang. The app-context root
was proven: the process became uid 0 with the expected capabilities, and the
daemon started.

## 4. What was not solved

| Problem | Status |
|---|---|
| Daemon survival after service teardown | Not fully solved |
| Reliable re-root after boot | Boot receiver disabled; not validated |
| Android 10 background-start restrictions | Worked around with a foreground service, but not solved generally |
| SELinux domain transitions for the daemon | Runtime-only; not hardened |
| App update / reinstall behavior | Not tested |

The core issue is lifecycle: Android is designed to stop background work,
and a root daemon started from an app is still a background process. A
foreground service helps, but it is not a guarantee. A robust design would
need a persistent user-visible service or a system-level host, neither of
which is available without a bootloader unlock.

## 5. Why the source is not published

The app's only purpose is to launch a kernel local-privilege-escalation
payload. Even without the native payload, publishing a ready-to-build
launcher lowers the bar for misuse and is not necessary to document the
research.

The manifest's original plan allowed “source only, no `libpoc.so`, no APK”.
This release takes the more conservative option:

- the design, the lifecycle problem, and the lessons are published;
- the Java source, native libraries, and APK are withheld;
- a separate, clearly labelled repository may be considered later, with the
  payload explicitly user-supplied and the legal constraints stated.

This is a deliberate editorial decision, not an oversight. It is recorded in
the withheld list in the README and in the final report.

## 6. Lessons

- Root from an app is not the same as root from a shell; the vendor wrapper
  and SELinux domain matter.
- Direct credential writes avoid the app-context `setgid` hang.
- The Android runtime environment must be exported for any child that starts
  `app_process` ([06](06-nightzuku-root-integration.md)).
- A foreground service is not a persistence guarantee.
- Boot receivers are easy to add and hard to make reliable under Android 10
  background restrictions.
- Shipping a root launcher is a policy decision, not just a technical one.

## 7. Limits

- The app was a research build, not a product.
- It depends on a working CVE-2020-0041 port for C.01; a different build
  needs different offsets.
- No persistent root was achieved.
- No bootloader unlock is implied.

## 8. Evidence

| Claim | Evidence |
|---|---|
| App-context root | Runtime uid/caps and daemon start (private) |
| Direct cred writes avoid hang | Controlled comparison (private) |
| Daemon lifecycle issue | Service teardown observations (private) |
| Boot path unproven | Boot receiver disabled |

## 9. References

- Runtime root: [01](01-runtime-root-cve-2020-0041.md)
- Nightzuku environment fix: [06](06-nightzuku-root-integration.md)
- Security policy: [SECURITY.md](../SECURITY.md)
