# postmarketOS port — Meizu M6 Note (m1721)

Unofficial mainline **postmarketOS** (phosh) port for the Meizu M6 Note
(`m1721`, Snapdragon 625 / MSM8953). Built on the
[msm8953-mainline](https://github.com/msm8953-mainline/linux) kernel.

> ⚠️ Not in official pmaports — `pmbootstrap init` won't list it. Overlay these
> aports onto a pmaports checkout and build. Use at your own risk.

Full hardware status + flashing walkthrough on the wiki:
<https://wiki.postmarketos.org/wiki/Meizu_M6_Note_(meizu-meilan-note-6)>

## Works

Display, touch, Wi-Fi, Bluetooth, sound (speaker/earpiece/mic/headphones),
**voice calls** (incl. speakerphone + in-call mute), SMS, mobile data, GPS,
sensors (accel, light, proximity), vibrator, flashlight, charging, notification
LED, both cameras (still capture; live preview is usable-with-work).

**Not working:** fingerprint (SPI controller locked under lk2nd), NFC (no hw).

## Build

```sh
# 1. a pmaports checkout
git clone https://gitlab.postmarketos.org/postmarketOS/pmaports.git
# 2. overlay this port's aports onto it
git clone https://github.com/nomorecoolnicknames/meizu-m1721-pmaports.git
cp -r meizu-m1721-pmaports/device meizu-m1721-pmaports/temp pmaports/
# 3. point pmbootstrap at it and build
pmbootstrap config aports "$PWD/pmaports"
pmbootstrap init          # vendor: meizu, device: m1721, UI: phosh
pmbootstrap install
```

GPU and modem firmware are handled automatically: the a530 render microcode
comes from the `firmware-qcom-adreno-a530` package, and the Adreno 506 ZAP
shader is fetched at build time by the bundled `firmware-meizu-m1721` aport
(from the MeizuCustoms vendor tree — no manual extraction needed).

## Flash

The boot partition keeps [lk2nd](https://wiki.postmarketos.org/wiki/Lk2nd) in
its first 512 KiB, so the pmOS `boot.img` is written at a **512 KiB offset**.
From lk2nd fastboot (hold a Volume key at power-on): `fastboot flash boot
boot.img`. A bad `boot.img` falls back to the on-device recovery (reachable over
`adb`), so it's hard to brick during bring-up. See the wiki for details.

## Kernel patches

The 14 device patches are carried as `.patch` files in the
`linux-postmarketos-qcom-msm8953` aport here. A cleaned-up series (for a future
upstream submission) also lives on a kernel fork branch:
[nomorecoolnicknames/linux @ `meizu-m1721`](https://github.com/nomorecoolnicknames/linux/tree/meizu-m1721)
(on `barni2000/7.1.3/develop`). Not yet submitted upstream.

## License

Kernel patches GPL-2.0, aports MIT. No proprietary firmware is stored in this
repo — it is downloaded at build time from its published locations.
