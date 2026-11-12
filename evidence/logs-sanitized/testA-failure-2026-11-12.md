# Sanitized Test A failure — 2026-11-12

**Type:** summary of the private Firehose/boot log, identifiers removed.
**Candidate:** two-site patched XBL `6982bba2…`.
**Patch:** `mov w0,#0` (`00 00 80 52`) at `0x22dec` and `0x22e80`,
replacing `bl 0x146ae000` (the SMC auth trampoline). No `ret`.
**ABL:** stock (untouched).

```text
[host] program xbl (LUN 1)             -> OK xbl in 195.6 s
[host] verify readback                 -> matches expected XBL
[dev ] reboot                          -> 9008 (EDL)
[host] stock XBL restore               -> OK
[dev ] boot                            -> C.01, green/locked
```

## What this supports

- The patched XBL was written successfully; the write itself was not the
  failure.
- The device did not boot the patched XBL; it fell to EDL.
- The stock restore worked; the device returned to C.01 green/locked.

## What this does not support

- The identity of the rejecting gate.
- That the PBL enforces the XBL signature (the leading hypothesis, not
  localized).
- That the two patch sites were the cause (B0 changed no code and was also
  rejected).

## Notes

- The full write log contains device identifiers and host paths and is
  private.
- Test B was not attempted after Test A failed.
- The stock XBL/ABL hashes after restore are recorded as prefixes in
  [hashes.md](../hashes.md).
