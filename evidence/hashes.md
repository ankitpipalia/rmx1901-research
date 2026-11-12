# Excluded artifacts — hashes

These artifacts are **not** in this repository. They are proprietary vendor
images, signed programmers, boot-chain images, payload binaries, or
device-specific logs. Hashes are recorded so a published observation can be
tied to a specific file without redistributing it.

`…` means only a prefix is recorded in the public note; the full digest is in
the private workspace. A prefix is an identifier, not a complete digest.

## Boot ROM / PBL

| Artifact | SHA-256 |
|---|---|
| PBL clean dump (`0x300000..0x33c000`) | `2736e155eb52457972ab93aeb77041f3a0a1067452147c553ee38220c7f9fb90` |
| PBL IMEM dump (`0x14800000..0x14820000`) | `204df714dba5d1822ff8834d1c0d5ad71c446c152cab513211d904fba3963eb2` |
| `segment1` pristine | `da6cffd174d8bac3d56b7b024ff35cca6d393368f7de7a719ea3e0f2bff58b5b` |
| `segment1_oracle.bin` | `299eaec923f255e38ce4aae309a3050265f21faf3daf69c051cd1e62ebbd9ef3` |
| `segment1_ctx_only.bin` | `c193d96d…6735d3` |
| `segment1_postflags_v2.bin` | `9226f564…be1b7d` |
| `segment1_postflags_v4.bin` | `ece5b759973001a88c6376a6de4d3948592db03058607a3169a98d6d7faf83a6` |
| `segment1_loader_table_v3.bin` | `cc8f186c…8cb40b` |
| `segment1_skipbc4c.bin` (withdrawn) | `7d20280f…ceaa2` |
| `segment1_bc4c_class3.bin` (withdrawn) | `f07b9d5f…a06ce` |
| `segment1_pte_diag.bin` | `63232f87a342a03c87b475c47d3549f10c02621ffc9082700e36d15278d50d12` |
| `segment1_pte_diag_v2.bin` | `17ac5b1b3f2c8d70c7d5c7276b077b7829e6d7bcabe12364a526b0187e9787b4` |
| `segment1_shadow_test.bin` | `744e1f86ded9c7694907cb5c0b734a6638500c11c42f2bb4b48b7a2e13b2dd02` |
| `segment1_bootctx_probe.bin` | `a64bf13422cab1b1a9f07d70fc25e49d688accf8d8843ad6b4e092af7b209537` |
| `segment1_descinit_probe.bin` | `37d687f3…` |
| `segment1_fullboot_probe.bin` | `45431234…` |
| `bootctx.bin` captured block (`0x2D0`) | `2ffa9243b54531d94a4c15638d991272c8b61cf2f2fdc92dd79f57480d19b7a8` |

## Programmer

| Artifact | SHA-256 |
|---|---|
| Signed OEM `devprg_710` | `a9fc1744e2ba010b827a8b019aede426c2a72cc264678b91ae23b82679c6f214` |
| `devprg_710_mod.bin` (one-byte change) | `b1c123b835a88542e4283265c716a31ecc8e71547a575414153f1b8bff473492` |
| `devprg_710_mod_hashfix.bin` (outer only) | `a1e1510e53cf061acf101abd8fdf5732812230a189196087445ff1afb0bff10e` |
| `devprg_710_mod_hashfix2.bin` (double fix) | `3845f397055341d6b7a98f018f2884ae7980400f7febcdb5439a0b1abc81398f` |

## Boot chain

| Artifact | SHA-256 |
|---|---|
| C.01 ABL (extracted PE) | `2e5cbaee60c2ad154fd750f50a5764a6650adf40bc8f3b8fc7e7bd280791426f` |
| Stock C.01 `xbl` | `fadc6410…` |
| Stock C.01 `abl` | `9a57f700…` |
| C.01 `xbl_config` | `5a551955…` |
| Test A patched XBL | `6982bba2…` |
| B0 re-hashed XBL | `f541fbfc…` |
| Earlier wrong readback hash (`xbl`) | `4b5f64a1…` (host framing artifact) |

## Lab kernels and patches

| Artifact | SHA-256 |
|---|---|
| `linux-4.9.112.tar.xz` | `60ec294e6aaaa20f496c0f7efc08132508371ea053d6f2729a88031171f6f0de` |
| VM `.config` | `3d009bb50ffa13d8af978ea6406efaed65e1499c2e3d0c88f6d621bc10aa208b` |
| Realme `binder.c` pristine | `3dc893f7d108971c0f38230ba7141a5c14b0c97ddfd96613e33e605090c35a50` |
| Realme `binder.c` clean-log | `225a8bf1b6615fa4a288bd25a5c06305f246f4015d44d78394ff1fc0a7063bca` |
| Realme `binder.c` fixed | `6ff5ad51f03263858ea69fc9d72f99fd466722709feed99fdf430354fe0768fc` |
| `binder_alloc.c` | `063664d0237c29dbd39932168f4f5d8a0159156c090320c3443263323d0211b7` |
| UAPI `binder.h` | `bcd2f594322712ac561e56e6872290e013d3480ffbd296e69c622f51d3838996` |
| Upstream fix patch | `d8db6b72ce34caf5bd90d47b4a8fb67dac7d1a5550cafa081dec19fdf2434cb9` |
| Clean-log patch | `b9e95c46a8a54a4c55a33a8933a1d880c669bf25c4f357c738efb3793f7b8b72` |
| 50 ms lab window patch | `67e81e47e14c62f48182151d079dd11873b4bf89011224f06f061e9c0ac507a1` |
| Fixed-vs-cleanlog diff | `d8eee9f8dd315c5fa884ae4daea57569d3f745e7864eb8c3855e62b37c21152b` |

## K3 repair images

| Artifact | SHA-256 |
|---|---|
| Hybrid modem image | `372ffae708abc4e51b35a32125d8123d9bb6c35899765cb43e4401e2e2af8392` |
| Post-repair `oppodycnvbk` readback | `178e8ce46bc045c3685ab675a0488207db6bd01c054467a1c9fe43ba83c18c90` |
| Post-repair `oppostanvbk` readback | `e83372e97d5309ba14a44be39bd564f25248b06d0d0f32f447bf1a6fd13d2c69` |

## GPTs (live, verified)

| LUN | SHA-256 |
|---:|---|
| 0 | `5edfc06bf86c935664dcd0b0215b5df1faf1679b6b5c3b2d57d8efcbddf2fbc3` |
| 1 | `f3d4a6f83f1d1e734178c9c2940d8276a5582c7c8aa0ac02452c7177d37b4e07` |
| 2 | `9806a84e1831157aad8937f21527225d393592206588e4d7a3ac45b350fdf3d3` |
| 3 | `3717b0ef49a4046ba4265513c30eef17dafcb0c9600dd7fde8fedb2fba7ff34c` |
| 4 | `fc4610ceacf78158e458f5299b3973fd0e08ed350693081590a6de6a7757fc78` |
| 5 | `a54132455825116f21837266591a53c90e009965f6fe87b663d7870ecb97ffad` |

## Logs and dumps

| Artifact | SHA-256 |
|---|---|
| KASAN vulnerable run log | `082e06ccdf2d7b3ba6caed52d901fd8c42e2630b0f2fb897127ae234cca2e99f` |
| KASAN vulnerable repeat log | `d1c0b614e025dd77416b2a288e0ceef7dca1f36bdadfd371ff48046fed82b38d` |
| KASAN fixed control log | `33f8b44952fb0486717fbc93b23d832c6adac9716722f739b95fde947dfacdbe` |

The raw device logs, USB captures, backups, programmer images, XBL/ABL
images, and payload binaries are retained privately and are not published.

## Verification

The full hashes can be checked against the private workspace by the author.
The published prefix hashes are enough to identify a file in a discussion
without implying that the full digest is public.

The companion repository
[`pblexp-macos`](https://github.com/ankitpipalia/pblexp-macos) carries the
full PBL/programmer hashes and the transport evidence index.
