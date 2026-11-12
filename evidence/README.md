# Evidence

This directory contains **sanitized excerpts** and **hashes**, not raw
device data.

## What is here

| Path | Contents |
|---|---|
| `hashes.md` | SHA-256 of the withheld artifacts (programmers, payloads, images, logs) |
| `logs-sanitized/oracle-2026-11-10.md` | Oracle magic and handoff sequence |
| `logs-sanitized/bootctx-2026-11-12.md` | Parsed boot context and descriptor |
| `logs-sanitized/testA-failure-2026-11-12.md` | Test A write/boot result |
| `logs-sanitized/b0-rejection-2026-11-12.md` | B0 write/boot result |

## What is not here

- Raw USB captures, serial logs, and host paths.
- Device serials, IMEI/MEID, MAC addresses, account data.
- Firmware, OTA packages, APKs, signed programmers, boot-chain images.
- Partition dumps, `persist`, `modemst*`, `keystore`, RPMB, fuse data.
- Full CVE-2020-0041 exploit source or binaries.
- Internal agent/review reports.

## Sanitization rules

The excerpts remove:

- device identifiers (serial, IMEI, UDID, USB serial string);
- host paths (`/Users/<user>`, `C:\Users\<user>`), port names, and IP
  addresses;
- timestamps that could identify a session;
- token/key bytes and NV values.

They keep:

- the packet-level facts needed to support a claim (magic strings, status
  codes, sequence);
- the hashes that identify the original artifact;
- the distinction between “payload did not run” and “primitive blocked”.

## Provenance

Each excerpt states whether it is:

- a **direct excerpt** from a private log (with identifiers removed);
- a **parsed table** produced from a private binary/log;
- a **summary** written from the private record.

The hashes in `hashes.md` are the integrity link. If a hash is a prefix
(marked `…`), the full digest is in the private record; the prefix is
published because it is enough to identify the artifact without implying a
full digest.

## Reproducing

The public record is not a byte-for-byte reproduction kit. Some artifacts
are proprietary or identity-bearing and cannot be published. What can be
reproduced is:

- the analysis (from public tools and the described offsets);
- the protocol behavior (from the sanitized sequences);
- the lab (from public kernel sources and the described patches);
- the tooling (offline tests in `tests/`).

## Ethics

Do not use these excerpts to target a device you do not own. The boot-chain
writes described here can brick hardware, and the identity/NV material is
withheld for legal and privacy reasons.
