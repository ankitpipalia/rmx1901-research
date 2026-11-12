# Sanitized B0 rejection — 2026-11-12

**Type:** summary of the private Firehose/boot log, identifiers removed.
**Candidate:** benign re-hashed XBL `f541fbfc…`.
**Change:** one string byte plus `table[2]`, then a self-consistent
re-hash of the XBL hash segment. No code change.
**ABL:** stock (untouched).

```text
[host] program xbl (LUN 1)             -> OK xbl in 195.7 s
[host] verify readback                 -> matches expected XBL
[dev ] reboot                          -> 9008 (EDL)
[host] stock XBL restore               -> OK
[dev ] boot                            -> C.01, green/locked
```

## What this supports

- Even a benign, self-consistent re-hash was rejected.
- The rejection is not explained by the two Test A code patches alone.
- The stock restore worked.

## What this does not support

- That the XBL signature is the rejecting gate. It is the leading
  hypothesis, because the XBL hash segment is signed (16-entry table at
  `0x1028`, 256-byte signature at `0x1228`, cert chain at `0x1328`), and
  changing `table[2]` invalidates that signature.
- That a different re-hash strategy would also be rejected.

## Notes

- B0 was designed to isolate “hash consistency” from “code change”. It
  succeeded at that: the image was self-consistent and still did not boot.
- The exact rejecting gate remains unresolved.
- The stock XBL/ABL hashes after restore are recorded as prefixes in
  [hashes.md](../hashes.md).
