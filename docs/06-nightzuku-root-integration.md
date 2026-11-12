# 06 — Nightzuku / Shizuku root integration

**Result:** Nightzuku 13.7.1.r60 runs in root mode on top of the C.01
runtime root, with its Shizuku server as uid 0. The fix was environmental,
not a new exploit: the root daemon had been started with a minimal
environment, so `app_process` could not load the target class.

| Item | Value |
|---|---|
| Host | RMX1901 C.01, runtime uid 0 (CVE-2020-0041) |
| App | Nightzuku 13.7.1.r60 |
| Result | `Nightzuku is running`, `Version 13.7.1, root`, `ADB: full access` |
| Server | `shizuku_server` and `libshizuku.so` as uid 0 |
| Persistence | None; reboot clears root and the server |

---

## 1. The symptom

After the runtime root was working, Nightzuku's “Start (for rooted devices)”
path spawned `su` and then `app_process` for
`moe.shizuku.starter.ServiceStarter`. The log showed:

```text
AndroidRuntime: >>>>>> START com.android.internal.os.RuntimeInit uid 0 <<<<<<
Shizuku: shizuku_server exited with code 0 after 0s
```

`app_process` started, but the target class never ran. The starter reported
a clean exit 0, so Nightzuku kept saying “not running”. This looked like a
Nightzuku bug, but it was not: the same manual command with a full adb-shell
environment ran correctly and produced the expected
`ShizukuServiceStarter: UserService launch token is not active, aborting`
for a fake token — proof that the class loaded.

## 2. Root cause

The root daemon (`surootd`) was started from the exploit shell with a
minimal environment. Its children inherited that environment, so
`app_process` had no `ANDROID_ROOT`, `BOOTCLASSPATH`,
`DEX2OATBOOTCLASSPATH`, `SYSTEMSERVERCLASSPATH`, and related variables. ART
started, but could not resolve the boot class path and the target class.

This is a general lesson for runtime-root tooling: **root is not enough;
the Android runtime environment must also be correct.**

## 3. Fix

1. Build `/data/local/tmp/envfull.sh` from `adb shell env`, exporting at
   least:

   ```text
   ANDROID_ROOT
   ANDROID_DATA
   ANDROID_RUNTIME_ROOT
   ANDROID_TZDATA_ROOT
   BOOTCLASSPATH
   DEX2OATBOOTCLASSPATH
   SYSTEMSERVERCLASSPATH
   ```

2. Restart the daemon so its children inherit the environment:

   ```bash
   kill <old-surootd-pid>
   rm -f /data/local/tmp/suroot.sock
   . /data/local/tmp/envfull.sh
   nohup /data/local/tmp/surootd >>/data/local/tmp/surootd.log 2>&1 &
   ```

3. Open Nightzuku → **Start (for rooted devices)** → Start.

If an old `su` client is stuck after a daemon restart, kill it and press
Back / Start again.

## 4. Verification

- App UI: “Nightzuku is running”, “Version 13.7.1, root”, “ADB: full
  access”.
- `ps -A`:

  ```text
  root 15363 1     libshizuku.so --apk=/data/app/.../base.apk
  root 15364 15363 shizuku_server
  ```

- logcat: `Service : send binder (SHIZUKU) to user app ... in user 0`.
- `su -c id` → `uid=0(root) ...`.

## 5. Limits

- Runtime only; a reboot clears root and the Shizuku server.
- No bootloader unlock, no persistent root, no partition writes.
- The `su` bind mount at `/system/xbin` is tmpfs and runtime-only.
- Nightzuku and Shizuku APKs are **not** redistributed here. Obtain them
  from their upstream projects and respect their licenses.
- The integration depends on a working runtime root
  ([01](01-runtime-root-cve-2020-0041.md)); it is not an independent root
  method.

## 6. What failed

| Attempt | Result | Lesson |
|---|---|---|
| Start Nightzuku from the exploit shell | `shizuku_server` exit 0 | Minimal environment broke ART |
| Start `surootd` without env | Same | Children inherit the daemon environment |
| Manual `app_process` with adb env | Class loaded | Environment was the only difference |
| Repeated Start with a stale `su` | Stuck client | Kill the old client after a daemon restart |

## 7. Evidence

| Claim | Evidence |
|---|---|
| Nightzuku reports root | App UI screenshot (private; no personal data) |
| Server runs as uid 0 | `ps -A` capture (private) |
| Class-load proof | logcat transcript (private) |
| Environment fix | `envfull.sh` and daemon restart |

## 8. References

- Nightzuku (upstream project).
- Shizuku (upstream project).
- Runtime root: [01](01-runtime-root-cve-2020-0041.md).
- `surootd`/`su` helper design: [19](19-autoroot-app.md).
