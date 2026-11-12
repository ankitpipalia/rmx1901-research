# Publication gates

Date: **2026-11-13**. This page records the checks run before the repository
was made public. It is a research-integrity and disclosure record, not a
legal opinion.

## Gate summary

| Gate | Check | Result |
|---|---|---|
| History | Fresh repository, no private history imported | **PASS** |
| Secrets | `gitleaks dir` on the working tree | **PASS** — 0 findings |
| Secrets | `trufflehog filesystem` | **PASS** — 0 verified, 0 unverified |
| Identity | Manual serial/IMEI/MAC/account scan | **PASS** — no values |
| Paths | Manual host-path/port scan | **PASS** — placeholders only |
| License | Third-party code not vendored; licenses recorded | **PASS** |
| Firmware | No firmware/OTA/APK/programmer/boot-chain images | **PASS** |
| Disclosure | GhostLock details withheld | **PASS (withheld)** |
| Disclosure | Deep Testing endpoints/keys/token withheld | **PASS (withheld)** |
| Disclosure | K3 NV/IMEI procedure withheld | **PASS (withheld)** |
| Tests | Offline unit tests | **PASS** — 33 tests |
| Links | Relative Markdown links | **PASS** — 0 broken |
| Claims | Bootloader-unlock claim absent; status banner present | **PASS** |

## 1. History

The repository was created with a fresh `git init` and a single initial
commit. The private `rmx1901` repository was never pushed, cloned, or
imported. No `.git` directory from another repository was copied.

## 2. Secret scans

```text
gitleaks 8.30.1
  gitleaks dir -v .            -> no leaks found

trufflehog 3.99.8
  trufflehog filesystem .      -> 0 verified, 0 unverified
```

The scans cover the working tree, including the tools and tests. They do not
cover the private workspace, which is intentionally not part of this
repository.

## 3. Manual identity scan

Searched for:

- device serial (`ro.boot.serialno`, `ro.vold.serialno`, USB serial);
- IMEI/MEID/IMSI/ICCID and phone numbers;
- Wi-Fi/BT MAC, SSID, account names;
- `opporeserve*` token bytes, `unlockCode`, QFPROM/fuse values;
- RPMB/Keymaster data.

Result: no values. The remaining uses of “IMEI” are contextual (“the IMEI
was empty”, “NV/IMEI procedures are withheld”), not data.

## 4. Path and port scan

Searched for `/Users/<name>`, `C:\Users\<name>`, `COM<n>`, `/tmp/<file>`,
and host IP addresses.

Result: no personal host paths or port names. Device paths such as
`/data/local/tmp` are intentional and are not host paths.

## 5. License audit

| Material | Handling |
|---|---|
| This repository's code | MIT |
| This repository's docs | CC BY 4.0 |
| `pblexp-macos` | MIT; linked as companion |
| `xperable` | GPL-3.0; linked, not vendored |
| Katana, DeepTest2.0, sdm710-lk, NO_AVB repos | Linked, not vendored |
| `oppo_ozip_decrypt` | Custom attribution; linked, not vendored |
| `sdat2img` | MIT; linked, not vendored |
| `avbtool` | Apache-2.0; linked, not vendored |
| Blue Frost CVE-2020-0041 | No license; not redistributed |
| Vendor firmware/APKs/programmers | Proprietary; not redistributed |

No GPL code is mixed into the MIT/CC-BY material.

## 6. Content and disclosure review

| Item | Decision |
|---|---|
| GhostLock / rtmutex details | **Withheld** until public report/vendor advisory |
| Deep Testing endpoints, key array, token bytes | **Withheld** pending vendor review |
| K3 NV/IMEI offsets, values, images, procedure | **Withheld** |
| CVE-2020-0041 full exploit source | **Withheld** (upstream has no license) |
| Auto-root app source/native libs/APK | **Withheld** (launcher for a kernel LPE) |
| Signed/modified programmers | **Withheld** (hashes only) |
| XBL/ABL images | **Withheld** (hashes only) |
| Raw logs/dumps/backups | **Withheld** (sanitized excerpts only) |
| Internal agent/review reports | **Withheld** (rewritten, not copied) |

The PBL programmer hash-table behavior is summarized here because it is
already documented in the public `pblexp-macos` repository; the modified
programmer binaries are not published.

## 7. Tests and links

```text
python3 -m unittest discover -s tests -v
  Ran 33 tests ... OK

relative Markdown link check
  broken links: 0
```

## 8. Claim review

- The README and overview state that the bootloader is **locked** and no
  unlock was achieved.
- No document claims persistent root, EL3 code execution, or a booting
  modified XBL/ABL.
- The `VERIFIED-RESULTS` table separates measured, derived, inferred, and
  negative claims.
- The `OPEN-QUESTIONS` page states what remains unresolved.

## 9. Residual risk

| Risk | Mitigation |
|---|---|
| PBL/programmer details could aid misuse | Already public in the companion repo; no binaries or turnkey modified images here |
| CVE-2024-31317 recipe is dual-use | Public CVE; the recipe is scoped to an owned A.05 device and states it is not root |
| Deep Testing protocol shape could aid abuse | Endpoints, keys, and tokens withheld; vendor review pending |
| K3 case study could be misread as an identity-repair guide | No offsets/values/procedure; explicit withholding statement |
| Boot-chain writes described in enough detail to be dangerous | No images/XML/destructive runner; recovery and safety emphasized |

## 10. Decision

All gates passed for the sanitized record, with the withholding decisions
above. The repository may be published publicly **after** the private-repo
verification step: create private, push, inspect the rendered tree and the
remote file list, then change visibility.

## 11. Post-publication checks

- Confirm the remote default branch and commit hash.
- Confirm the repository is public and the description/topics are set.
- Re-run the secret scan against the pushed tree.
- Verify the companion link resolves.
- Confirm no file outside the intended tree was pushed.
