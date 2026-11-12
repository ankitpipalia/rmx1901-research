# Third-party licenses

No third-party source code is vendored in this repository. The table records
the license of each project that is linked, referenced, or used as a tool, so
a reader can comply with it.

| Project | License | Vendored? | Notes |
|---|---|---|---|
| [`ankitpipalia/pblexp-macos`](https://github.com/ankitpipalia/pblexp-macos) | MIT | No (companion repo) | Transport, host sequence, hashfix, oracle |
| [`j4nn/xperable`](https://github.com/j4nn/xperable) | GPL-3.0 | No | Sony SD835/SDM845; link only, do not copy into MIT |
| [`Daniel224455/katana`](https://github.com/Daniel224455/katana) | See upstream | No | SDM845 Sahara `0x13` reference |
| [`koaaN/DeepTest2.0`](https://github.com/koaaN/DeepTest2.0) | See upstream | No | 316-byte layout reference |
| [`838693469/sdm710-lk`](https://github.com/838693469/sdm710-lk) | See upstream | No | ABL source reference |
| [`atlas4381/qualcomm_avb_exploit_poc`](https://github.com/atlas4381/qualcomm_avb_exploit_poc) | See upstream | No | NO_AVB reference |
| [`kasnria001/qualcomm_noavb_exploit_common`](https://github.com/kasnria001/qualcomm_noavb_exploit_common) | See upstream | No | NO_AVB reference |
| [`Qingizi7/iQOO_Neo8_bl-unlock`](https://github.com/Qingizi7/iQOO_Neo8_bl-unlock) | See upstream | No | `devinfo` reference |
| [`bkerler/edl`](https://github.com/bkerler/edl) | See upstream | No | Protocol reference |
| [`linux-msm/qdl`](https://github.com/linux-msm/qdl) | See upstream | No | Protocol reference |
| [`bkerler/oppo_ozip_decrypt`](https://github.com/bkerler/oppo_ozip_decrypt) | Custom attribution (“share/modify, refer original author”) | No | OTA decryption tool |
| [`xpirt/sdat2img`](https://github.com/xpirt/sdat2img) | MIT | No | Sparse image conversion |
| [AOSP `avbtool`](https://android.googlesource.com/platform/external/avb/) | Apache-2.0 | No | AVB verification |
| [AOSP frameworks/base](https://android.googlesource.com/platform/frameworks/base/) | Apache-2.0 | No | Source reference |
| [Linux 4.9.112](https://cdn.kernel.org/pub/linux/kernel/v4.x/linux-4.9.112.tar.xz) | GPL-2.0 | No | KASAN lab base |
| [Realme X kernel source](https://github.com/realme-kernel-opensource/realmeX-kernel-source) | GPL-2.0 | No | Binder source reference |
| Blue Frost CVE-2020-0041 | **No license** | No | Analysis/exploit reference; not redistributed |
| `vaginessa` Pixel port | See upstream | No | Starting point; not redistributed |
| Qualcomm / OPPO / Realme firmware, programmers, APKs | Proprietary | No | Not redistributed |

## This repository

| Material | License |
|---|---|
| Code in `tools/` and `tests/` | MIT (see [LICENSE](../LICENSE)) |
| Documentation in `docs/`, `evidence/`, `references/` | CC BY 4.0 (see [LICENSE-DOCS](../LICENSE-DOCS)) |
| Hashes and sanitized excerpts | CC BY 4.0, subject to the exclusions above |

## Compliance notes

- GPL-3.0 material is linked, not copied. If you reuse it, comply with
  GPL-3.0.
- The OPPO decryption tool's custom attribution license requires preserving
  the author's notice. It is not relicensed here.
- The Blue Frost repository has no license; no code or binary from it is
  included. The write-up cites it and links to it.
- Vendor firmware and APKs are not licensed for redistribution and are not
  included.
- If you believe a credit or license is missing, open an issue with the
  source and the specific file.
