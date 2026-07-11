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

## GPU firmware (not included — source it yourself)

The Adreno 506 GPU needs two sets of firmware. They are **not** shipped in this
repo (one is device-signed and not redistributable). Build a local
`firmware-meizu-m1721` aport out of them.

### 1. a530 render microcode — redistributable

`a530_pfp.fw`, `a530_pm4.fw`, `a530v3_gpmu.fw2` (the 5xx family shares the a530
microcode). postmarketOS pulls these automatically through the
`firmware-qcom-adreno-a530` dependency, so on a normal build you get them for
free. To fetch them by hand:

```sh
git clone --depth 1 https://gitlab.com/kernel-firmware/linux-firmware.git
cp linux-firmware/qcom/a530_pfp.fw \
   linux-firmware/qcom/a530_pm4.fw \
   linux-firmware/qcom/a530v3_gpmu.fw2  .
```

### 2. a506 ZAP shader — Meizu-signed, extract from YOUR device

`a506_zap.mdt` + `a506_zap.b00`/`.b01`/`.b02`. This is signed for this device and
is **not** in linux-firmware.

**Easiest — grab it from the MeizuCustoms vendor tree** (already extracted):

```sh
BASE=https://raw.githubusercontent.com/meizucustoms/proprietary_vendor_meizu/lineage-20/m1721/proprietary/vendor/firmware
for f in a506_zap.mdt a506_zap.b00 a506_zap.b01 a506_zap.b02; do
	curl -fLO "$BASE/$f"
done
```

**Or pull it from your own device's stock Flyme ROM** (rooted stock boot, or an
extracted `vendor`/`system` image):

```sh
adb pull /vendor/firmware/a506_zap.mdt      # + .b00 .b01 .b02
# if the path differs, locate them first:
adb shell 'find /vendor /system -iname "a506_zap*" 2>/dev/null'
```

### 3. Package into a `firmware-meizu-m1721` aport

Put all seven blobs beside a new APKBUILD in your pmaports checkout, then
`abuild checksum`. The install paths matter — `a506_zap.*` go directly in
`/lib/firmware` (the msm/adreno driver looks up `"a506_zap.mdt"` unprefixed),
the a530 microcode goes under `/lib/firmware/qcom`:

```sh
mkdir -p pmaports/device/testing/firmware-meizu-m1721
cd pmaports/device/testing/firmware-meizu-m1721
cp /path/to/{a506_zap.mdt,a506_zap.b00,a506_zap.b01,a506_zap.b02,a530_pm4.fw,a530_pfp.fw,a530v3_gpmu.fw2} .

cat > APKBUILD <<'AP'
# Maintainer: nomorecoolnicknames <78512247+nomorecoolnicknames@users.noreply.github.com>
pkgname=firmware-meizu-m1721
pkgver=1
pkgrel=0
pkgdesc="GPU firmware for Meizu M6 Note (Adreno 506 ZAP + a530 render microcode)"
url="https://postmarketos.org"
arch="aarch64"
license="proprietary"
options="!check !strip !archcheck !tracedeps pmb:cross-native"
source="
	a506_zap.mdt a506_zap.b00 a506_zap.b01 a506_zap.b02
	a530_pm4.fw a530_pfp.fw a530v3_gpmu.fw2
"
package() {
	install -Dm644 "$srcdir"/a506_zap.mdt -t "$pkgdir"/lib/firmware
	install -Dm644 "$srcdir"/a506_zap.b00 -t "$pkgdir"/lib/firmware
	install -Dm644 "$srcdir"/a506_zap.b01 -t "$pkgdir"/lib/firmware
	install -Dm644 "$srcdir"/a506_zap.b02 -t "$pkgdir"/lib/firmware
	install -Dm644 "$srcdir"/a530_pm4.fw   -t "$pkgdir"/lib/firmware/qcom
	install -Dm644 "$srcdir"/a530_pfp.fw   -t "$pkgdir"/lib/firmware/qcom
	install -Dm644 "$srcdir"/a530v3_gpmu.fw2 -t "$pkgdir"/lib/firmware/qcom
}
AP

pmbootstrap checksum firmware-meizu-m1721   # or: abuild checksum
```

The `device-meizu-m1721` package already `depends` on `firmware-meizu-m1721`, so
once this aport exists in your pmaports tree it is pulled into the rootfs.

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
