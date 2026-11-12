# Upstream credits

This work builds on public research and tooling. The credit here is
specific: what each source contributed, and what was **not** copied.

## Exploit research

**Blue Frost Security** published the CVE-2020-0041 analysis and exploit.
The device port in this work started from that public research and from a
Pixel 3/3a port. The Blue Frost repository carries no license, so no source
or binary from it is redistributed here. The write-up, the device-specific
offsets, and the observations are this project's contribution.

**`vaginessa`** published the Pixel 3/3a port used as the starting point.
Its terms should be checked independently; it is not vendored.

**longterm.io** published the CVE-2020-0423 race trace, the fix, and the
root model. **`wired0ut`** published the closest public reproducer, and
**`sparrow-labz`** published a KASAN reproducer. These informed the 0423
analysis and the lab. No code was copied.

## Boot chain

**`j4nn/xperable`** is a public CVE-2021-1931 exploit for Sony
SD835/SDM845. It was used to understand the bug class and to establish that
it does not transfer to SD710. It is GPL-3.0 and is not vendored.

**`Daniel224455/katana`** implements the Sahara `0x13` recursion for
SDM845. Its dispatch and finish-payload structure were compared with the
RMX1901 PBL. The RMX1901 has the same dispatch chain, but the finish payload
was not ported. No code was copied.

**`838693469/sdm710-lk`** is a public SDM710 ABL source tree. Its
`DeviceInfo.h`, `KeymasterClient.c`, and `VerifiedBoot.c` corroborated the
C.01 binary analysis. It is a reference, not a vendored dependency.

**`koaaN/DeepTest2.0`** documented the 316-byte Deep Testing blob layout and
the `0x45A000` slot. The layout was used to interpret the ABL parser. No
code or token is included.

**`atlas4381/qualcomm_avb_exploit_poc`**,
**`kasnria001/qualcomm_noavb_exploit_common`**, and
**`Qingizi7/iQOO_Neo8_bl-unlock`** were used to evaluate the NO_AVB,
Keymaster, and direct-`devinfo` routes. All three were ruled out for C.01.
No code was copied.

**`bkerler/edl`** and **`linux-msm/qdl`** were protocol references for the
Firehose framing and the `<read>` command. The readback gate was written
from the protocol behavior, not copied.

## Tooling

**`bkerler/oppo_ozip_decrypt`** decrypted the OPPO `.ozip` packages. It is
under a custom attribution license (“share/modify, refer original author”)
and is linked, not vendored.

**`xpirt/sdat2img`** (MIT) converted the sparse OTA images. Linked, not
vendored.

**AOSP `avbtool`** (Apache-2.0) verified AVB metadata. Linked, not vendored.

The **Linux 4.9.112** source and the **Realme X kernel source** were used
for the KASAN lab. The lab patches are described in
[docs/22](../docs/22-vm-kasan-lab.md); the vendor source is not
redistributed.

## This project's tooling

The macOS/libusb transport, the `oppo710` host sequence, the signed
programmer serve path, the hashfix builders, and the execution oracle are in
[`ankitpipalia/pblexp-macos`](https://github.com/ankitpipalia/pblexp-macos)
(MIT).

The offline analysis and validation tools in this repository are original
and MIT-licensed.

## What was not copied

No vendor firmware, OTA, APK, signed programmer, boot-chain image, or device
dump is included. No GPL code is mixed into the MIT/CC-BY material. No
unlicensed exploit source is redistributed.

If a credit is missing, it is an omission, not a claim of authorship. Open
an issue with the source and the specific contribution.
