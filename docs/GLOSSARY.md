# Glossary

| Term | Meaning |
|---|---|
| **ABL** | Android Bootloader. The UEFI application that implements Fastboot, verifies boot/vbmeta, and writes unlock state. |
| **ADSP** | Applications DSP. The modem/audio/sensor DSP firmware area; its generation must match the firmware. |
| **AP[2]** | Access-permission bit in an AArch64 page-table entry; AP[2]=1 means read-only at the current exception level. |
| **ARB** | Anti-rollback. A fuse/counter that prevents flashing older firmware. |
| **AVB** | Android Verified Boot. The boot-image/vbmeta verification chain. |
| **Binder** | Android's IPC driver (`/dev/binder`), the target of CVE-2020-0041 and CVE-2020-0423. |
| **C.01** | Realme X build `RMX1901_11_C.01`, Android 10, kernel `4.9.186-perf+`. |
| **Deep Testing** | Realme/OPPO's official bootloader-unlock application flow. |
| **EDL** | Emergency Download mode. Qualcomm's 9008 USB mode for Sahara/Firehose. |
| **efisp** | An EFI system partition used by newer Qualcomm ABL/GBL flows. Not present on C.01. |
| **Firehose** | Qualcomm's post-Sahara command protocol for read/program/erase over 9008. |
| **GBL** | A newer Qualcomm UEFI bootloader stage; not present on Android 10 C.01. |
| **GPT** | GUID Partition Table. The six LUN partition tables on this device. |
| **KGSL** | Qualcomm's kernel graphics system layer (`/dev/kgsl-3d0`). |
| **KSMA** | Kernel-space memory access; an arbitrary read/write primitive via page tables. |
| **KASLR** | Kernel address-space layout randomization. |
| **LUN** | Logical unit number. The device has six physical UFS LUNs. |
| **ozip** | OPPO/Realme's encrypted OTA container format. |
| **PBL** | Primary Boot Loader. The boot ROM code that runs first, at EL3, and implements Sahara. |
| **PTE** | Page-table entry. |
| **QSEECom** | Qualcomm Secure Execution Environment communication interface (`/dev/qseecom`). |
| **RPMB** | Replay-protected memory block. TEE-owned storage used for unlock/device state. |
| **Sahara** | Qualcomm's initial 9008 handshake/image-transfer protocol. |
| **SBL1** | Secondary Boot Loader 1. Authenticates and loads XBL/ABL stages. |
| **SMC** | Secure Monitor Call. The EL3 call interface used for auth and VIP. |
| **TA** | Trusted Application. A TEE-side service such as `keymaster64`. |
| **TEE** | Trusted Execution Environment (Qualcomm QTEE/QSEE). |
| **TTBR0_EL3** | Translation table base register for EL3; on this PBL it is `0x14806000`. |
| **UAF** | Use-after-free. |
| **UFS** | Universal Flash Storage. The device's storage bus. |
| **VIP** | Vendor Image Protection. Qualcomm's Firehose authorization mechanism, decided in EL3. |
| **XBL** | Extensible Boot Loader. The stage after PBL/SBL1; carries the UEFI environment. |
| **XBL_SEC** | The secure sub-component embedded in the XBL image. |
| **vbmeta** | Android Verified Boot metadata partition/image. |
| **Milestone fuse** | A software fuse that, once blown, makes the Keymaster TA refuse device-state reads/writes. |
| **`opporeserve1`** | An OPPO/Realme reserved partition; the Deep Testing token slot is at `+0x45A000`. |
| **`oppo_root_check`** | Realme's syscall wrapper that reboots on unexpected credential changes. |
| **`surootd`** | The research root daemon used to keep a uid-0 command channel after the exploit exits. |
| **`segment1`** | The first payload segment of the fake programmer ELF used in the PBL work. |
