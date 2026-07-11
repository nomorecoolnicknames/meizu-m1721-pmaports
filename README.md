# postmarketOS port — Meizu M6 Note (m1721)

> ⚠️ **Unofficial, out-of-tree, work-in-progress port. Use at your own risk.**
> This is **not** in upstream pmaports and is **not** installable through the
> official postmarketOS tooling — `pmbootstrap init` does not list this device
> and there is no official image. It is built by overlaying the aports in this
> repo onto a pmaports checkout and flashing manually.

Mainline postmarketOS (phosh) port for the **Meizu M6 Note** (internal id
`m1721`, marketing codename *meilan-note-6*), a Qualcomm Snapdragon 625
(MSM8953) handset. Built on the
[msm8953-mainline](https://github.com/msm8953-mainline/linux) kernel.

Device wiki (status, hardware notes):
<https://wiki.postmarketos.org/wiki/Meizu_M6_Note_(meizu-meilan-note-6)>

## What's in this repo

This is a **pmaports overlay** — the three aports needed to build the port, in
their pmaports-relative paths:

| Path | What |
|---|---|
| `device/testing/device-meizu-m1721/` | Device package: deviceinfo, UCM sound config, camera tuning, polkit rules, helper scripts (`sim-switcher`, `torch`, `gps`, `batmon`), post-install |
| `device/community/linux-postmarketos-qcom-msm8953/` | The shared msm8953-mainline kernel aport **with the 14 device patches** added (DTS, panel, camera sensors, sound/voice, LED/flash, haptics, sensors). Ships kernel **v7.0.9** (device-tested). |
| `temp/libcamera/` | libcamera fork with the IMX362 sensor helper + camera-preview patches |

The clean **kernel patch series** (for a future upstream PR) also lives as a
git branch on a fork of the kernel:
[nomorecoolnicknames/linux @ `meizu-m1721`](https://github.com/nomorecoolnicknames/linux/tree/meizu-m1721)
(rebased onto `barni2000/7.1.3/develop`). Those have **not** been submitted
upstream yet, and the two large camera sensor drivers still need a
`checkpatch.pl --strict` pass before any real submission.

## Firmware (not included)

The GPU needs proprietary firmware that is **not** redistributed here:

- **Adreno a530 render microcode** (`a530_pfp.fw`, `a530_pm4.fw`,
  `a530v3_gpmu.fw2`) — available in the upstream
  [linux-firmware](https://gitlab.com/kernel-firmware/linux-firmware) `qcom/`
  directory.
- **Adreno a506 ZAP shader** (`a506_zap.mdt`/`.b0*`) — Meizu-signed, extract it
  from the device's stock `/vendor/firmware/` (or the `vendor`/`system`
  partition). It is device-specific and not freely redistributable.

Provide these to a local `firmware-meizu-m1721` aport (the recipe is
straightforward: `install -Dm644` each blob under
`/lib/firmware/qcom/msm8953/meizu/m1721/` and, for a506, the Adreno path
`/lib/firmware/qcom/a506_zap.*`).

## Building

```sh
# 1. Get a pmaports checkout (official)
git clone https://gitlab.postmarketos.org/postmarketOS/pmaports.git
# 2. Overlay this repo's aports on top of it
git clone https://github.com/nomorecoolnicknames/meizu-m1721-pmaports.git
cp -r meizu-m1721-pmaports/device/testing/device-meizu-m1721 pmaports/device/testing/
cp -r meizu-m1721-pmaports/temp/libcamera pmaports/temp/
#    the kernel aport REPLACES the shared upstream one (adds the m1721 patches):
cp -r meizu-m1721-pmaports/device/community/linux-postmarketos-qcom-msm8953 pmaports/device/community/
#    …and add your firmware-meizu-m1721 aport (see above).
# 3. Point pmbootstrap at this pmaports and init the device
pmbootstrap config aports "$PWD/pmaports"
pmbootstrap init          # vendor: meizu, device: m1721, UI: phosh
pmbootstrap install       # builds the rootfs + boot.img
```

## Flashing

The boot partition holds [lk2nd](https://wiki.postmarketos.org/wiki/Lk2nd) in
its first 512 KiB; the postmarketOS `boot.img` is written at a **512 KiB
offset** so lk2nd stays intact.

- **lk2nd fastboot**: power on and hold a Volume key after the boot vibration →
  `fastboot flash boot boot.img`.
- **Recovery**: a bad `boot.img` falls back to the on-device recovery, reachable
  over `adb` — this device is hard to brick during kernel bring-up.

See the wiki for the full flashing walkthrough and current hardware status.

## License

Device/kernel/libcamera changes here follow their upstream licenses (kernel
patches GPL-2.0, aports MIT). No proprietary firmware is included (see above).
