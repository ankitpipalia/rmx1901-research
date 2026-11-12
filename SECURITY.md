# Security policy

## Scope

This repository is a sanitized research record for a personally owned
device. It does not ship an exploit, a bootloader-unlock service, firmware,
device backups, or a one-click root package. The tools are read-only
analysis and fail-closed validation helpers.

## Reporting a vulnerability

If you find a vulnerability in a vendor product described here, report it to
the vendor first:

- **Qualcomm Product Security**: <https://www.qualcomm.com/company/product-security>
- **OPPO/Realme security**: use the official OPPO/Realme security contact or
  support channel.

If you find a problem in this repository's documentation or tooling, open a
private security advisory on GitHub or contact the maintainer. Please do not
publish device-specific secrets, IMEI/NV data, tokens, account data, or
proprietary blobs in an issue.

## Coordinated disclosure

Some findings in this work are **not** published in full:

- **GhostLock / rtmutex audit** — withheld until the report and any vendor
  advisory are public. The workstream is listed, its scope and negative
  outcome are stated, and the technical details are not.
- **Deep Testing token protocol** — described at the protocol level, with
  endpoints, key arrays, account fields, and token bytes withheld pending
  vendor review.
- **OPPO K3 NV/modem repair** — methodology only; no NV values, offsets,
  images, or step-by-step identity repair.

The PBL programmer hash-table behavior overlaps public CVE-2019-2338 and is
already documented in the companion `pblexp-macos` repository. It is
summarized here with hashes and analysis, not with redistributable modified
programmers.

A 90-day coordination window is suggested for any new vendor finding.
Public CVEs cited here (CVE-2020-0041, CVE-2020-0423, CVE-2021-1931,
CVE-2024-31317) are already public; include the vendor advisory when you
discuss them.

## Legal and ethical use

Bootloader unlocking and circumvention can be restricted by law (for example
DMCA §1201, CFAA, India IT Act, export-control rules, and IMEI/NV
regulations). This repository is not legal advice.

Use this material only on hardware you own or are explicitly authorized to
modify, with a tested recovery path. Do not use it to bypass someone else's
lock, to alter identity or NV data, or to build a turnkey unlock service.
