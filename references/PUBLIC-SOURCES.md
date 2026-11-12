# Public sources

Public material used for comparison, reproduction, or protocol reference.
Nothing here is vendored; see [THIRD-PARTY-LICENSES](THIRD-PARTY-LICENSES.md).

## Qualcomm EDL / PBL / boot chain

| Source | Used for |
|---|---|
| [`ankitpipalia/pblexp-macos`](https://github.com/ankitpipalia/pblexp-macos) | macOS/libusb 9008 transport, `oppo710` host sequence, signed-programmer serve, hashfix builders, oracle |
| [`bkerler/edl`](https://github.com/bkerler/edl) | Firehose framing and command reference |
| [`linux-msm/qdl`](https://github.com/linux-msm/qdl) | Firehose `<read>` framing reference |
| [`838693469/sdm710-lk`](https://github.com/838693469/sdm710-lk) | SDM710 ABL source: `DeviceInfo`, Keymaster client, VerifiedBoot |
| [Qualcomm Product Security](https://www.qualcomm.com/company/product-security) | Advisory and disclosure channel |

## Android privilege escalation

| Source | Used for |
|---|---|
| [Blue Frost CVE-2020-0041](https://github.com/bluefrostsecurity/CVE-2020-0041) | Binder LPE analysis and exploit |
| [Blue Frost part 1](https://labs.bluefrostsecurity.de/blog/2020/03/31/cve-2020-0041-part-1-sandbox-escape/) | Sandbox escape |
| [Blue Frost part 2](https://labs.bluefrostsecurity.de/blog/2020/04/08/cve-2020-0041-part-2-escalating-to-root/) | Escalation to root |
| `vaginessa` Pixel 3/3a port | Starting point for the device port (upstream terms apply) |
| [longterm.io CVE-2020-0423](https://longterm.io/cve-2020-0423.html) | Race trace, fix, root model |
| [`wired0ut/CVE-2020-0423`](https://github.com/wired0ut/CVE-2020-0423) | Closest public reproducer (WIP) |
| [`sparrow-labz/CVE-2020-0423`](https://github.com/sparrow-labz/CVE-2020-0423) | KASAN reproducer reference |
| [AOSP frameworks/base](https://android.googlesource.com/platform/frameworks/base/) | `ActivityManagerService`, `ZygoteProcess`, `ZygoteConnection` |
| [Android security bulletins](https://source.android.com/docs/security/bulletin) | CVE-2020-0041, CVE-2020-0423, CVE-2021-1931, CVE-2024-31317 context |
| [NVD CVE-2020-0041](https://nvd.nist.gov/vuln/detail/CVE-2020-0041) | CVE record |
| [NVD CVE-2020-0423](https://nvd.nist.gov/vuln/detail/CVE-2020-0423) | CVE record |
| [NVD CVE-2024-31317](https://nvd.nist.gov/vuln/detail/CVE-2024-31317) | CVE record |

## Bootloader / vendor flows

| Source | Used for |
|---|---|
| [NVD CVE-2021-1931](https://nvd.nist.gov/vuln/detail/CVE-2021-1931) | SD710 listing, CWE-120, CVSS |
| [NVD CVE-2021-30327](https://nvd.nist.gov/vuln/detail/CVE-2021-30327) | Sahara overflow record; configuration list |
| [NVD CVE-2019-2338](https://nvd.nist.gov/vuln/detail/CVE-2019-2338) | Cross-OEM trust-boundary record |
| [`j4nn/xperable`](https://github.com/j4nn/xperable) | CVE-2021-1931 reference (Sony SD835/SDM845) |
| [`Daniel224455/katana`](https://github.com/Daniel224455/katana) | Sahara `0x13` reference (SDM845) |
| [`koaaN/DeepTest2.0`](https://github.com/koaaN/DeepTest2.0) | 316-byte layout, `0x45A000` slot |
| [`turistu/rmx3474-rooting`](https://github.com/turistu/rmx3474-rooting) | Model-spoof history |
| [`mikoker/deeptest`](https://github.com/mikoker/deeptest) | Newer HeyTap/OnePlus protocol (not compatible) |
| [Pen Test Partners, SDM660 bootloader](https://www.pentestpartners.com/security-blog/) | CVE-2021-1931 class context |
| [`atlas4381/qualcomm_avb_exploit_poc`](https://github.com/atlas4381/qualcomm_avb_exploit_poc) | NO_AVB/Keymaster reference |
| [`kasnria001/qualcomm_noavb_exploit_common`](https://github.com/kasnria001/qualcomm_noavb_exploit_common) | NO_AVB variant |
| [`Qingizi7/iQOO_Neo8_bl-unlock`](https://github.com/Qingizi7/iQOO_Neo8_bl-unlock) | Direct `devinfo` reference |
| [`longterm.io`](https://longterm.io/cve-2020-0423.html) | 0423 root model |

## OTA / tooling

| Source | Used for |
|---|---|
| [`bkerler/oppo_ozip_decrypt`](https://github.com/bkerler/oppo_ozip_decrypt) | OPPO `.ozip` decryption |
| [`xpirt/sdat2img`](https://github.com/xpirt/sdat2img) | Sparse image conversion |
| [AOSP avbtool](https://android.googlesource.com/platform/external/avb/) | AVB verification |
| [Linux 4.9.112](https://cdn.kernel.org/pub/linux/kernel/v4.x/linux-4.9.112.tar.xz) | KASAN lab base |
| [`realme-kernel-opensource/realmeX-kernel-source`](https://github.com/realme-kernel-opensource/realmeX-kernel-source) | Realme binder source |
| [`wired0ut/CVE-2019-2215`](https://github.com/wired0ut/CVE-2019-2215) | Post-race primitive reference |

## Notes

- Links are provided for attribution and verification. Their content is not
  endorsed and may change.
- Some public repos target different SoCs or builds; the documents state
  where a source does **not** apply.
- The absence of a link does not mean a source was not consulted; it means
  the source was not central to a published claim.
