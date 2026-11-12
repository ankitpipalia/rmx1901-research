# Methodology

## 1. Evidence labels

Every non-trivial claim in this record is labelled:

- **Measured (M):** observed on the device or in a controlled lab, with a
  log or capture.
- **Derived (D):** obtained by static analysis of a named artifact
  (decompiled function, parsed table, compared hash).
- **Inferred (I):** a conclusion from indirect evidence, with the basis
  stated.
- **Negative (N):** the thing was attempted and did not work.

The labels matter. A static “the branch is dead” is not the same as a
runtime “the device rejected the image”. A runtime “the payload sent the
magic” is not the same as “the payload has EL3 privilege”.

## 2. Read-only first

For every layer, the order was:

1. parse the image offline;
2. map the functions and data;
3. build a read-only probe;
4. run the probe with the stock image as the control;
5. only then consider a write.

The boot-context, descriptor, PTE, Keymaster, and Firehose readback probes
were all read-only. The two XBL boot tests were the only boot-chain writes in
that workstream, and both were followed by a stock restore.

## 3. Controls

A control answers “what does success look like?” before the experiment:

- the signed programmer control (181 READ_DATA, `END_IMAGE_TX 0`, `DONE 1`);
- the stock `segment1` oracle (magic after segment2/3);
- the pristine programmer hash table (both tables verify);
- the fixed binder KASAN control (0 reports);
- the stock XBL/ABL after each boot test.

Without a control, a timeout or a reset is ambiguous.

## 4. One variable

Each auth test changed one thing:

- one byte in the programmer;
- one table entry;
- one patch site;
- one context field.

This is slower, but it makes the result interpretable. When two things
changed at once (as in the early PBL payloads), the failure could not be
attributed.

## 5. Readback and hashes

A write is not “done” until it is read back and hashed. The Firehose
readback gate was built for this, and it caught a real host-framing bug that
had produced a wrong hash.

The readback gate is fail-closed:

- short/long/desynchronized reads are failures;
- a missing final ACK is a failure;
- a hash mismatch is a failure;
- a device-side `filename` is never used for a raw read.

## 6. Recovery before writes

Before any boot-chain write:

- the signed programmer must load;
- the GPTs must be verified;
- the C.01 boot-chain set must pass its offline verifier;
- the cold-power-cycle procedure must be known;
- the restore path must be understood, even if not yet tested end-to-end.

The LUN 0 erase during the VIP probe is the counter-example: a destructive
command was sent as a “probe” before the VIP state was established.

## 7. Negative results

A failed experiment is recorded with:

- the exact image/command;
- the expected result;
- the observed result;
- the likely cause;
- what it rules out, and what it does not.

“Test A fell to EDL” does not identify the rejecting gate. “The 0423 race
was not won” does not prove the bug is unexploitable. The record keeps those
distinctions.

## 8. Sanitization

The public record removes:

- device serials, IMEI/MEID, MAC addresses, account data;
- absolute host paths and port names;
- token bytes, NV data, and calibration values;
- firmware, APKs, programmers, and boot-chain images;
- internal agent/review material.

What remains is the analysis, the sanitized excerpts that support specific
claims, and SHA-256 hashes that identify the withheld artifacts without
distributing them.

## 9. Tool separation

The repository separates:

- **analysis** tools (parse, hash, decode) — no device writes;
- **validation** tools (geometry, manifests, readback verification) —
  fail-closed, no device writes;
- **destructive runners** — not published.

The companion `pblexp-macos` repository contains the transport and the
signed-programmer serve path. It is a research loader, not an unlock tool.

## 10. Limitations

- Single device, single build for most results.
- Static analysis is not runtime proof.
- A negative result is time-boxed, not a proof of impossibility.
- The lab kernel is not the exact device kernel.
- The vendor firmware and images are not published, so some results cannot
  be independently reproduced byte-for-byte.

## 11. What “verified” means here

“Verified” means the claim has a matching measurement or a named static
artifact, and the claim is no stronger than that evidence. It does not mean
“universally true” or “the vendor agrees”.

The [VERIFIED-RESULTS](VERIFIED-RESULTS.md) table is the authoritative list.
