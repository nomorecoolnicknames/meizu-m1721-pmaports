#!/bin/sh
# m1721 bring-up only: dump kernel log RAW into the dedicated Qualcomm
# 'logdump' partition every 2s so it survives cold reboot and is readable
# from TWRP: dd if=/dev/block/mmcblk0p48 bs=1M count=1 | strings | less
# Remove this hook before any daily-driver use.

LOGDEV=/dev/disk/by-partlabel/logdump
[ -b "$LOGDEV" ] || LOGDEV=/dev/mmcblk0p48
[ -b "$LOGDEV" ] || exit 0

echo "m1721-logdump: writing kernel log to $LOGDEV every 2s" > /dev/kmsg

(
	i=0
	while true; do
		{
			echo "=== PMOS-M1721-BOOTLOG seq=$i uptime=$(cat /proc/uptime 2>/dev/null) ==="
			dmesg 2>/dev/null | tail -c 4000000
			echo ""
			echo "=== PMOS-M1721-BOOTLOG-END seq=$i ==="
		} > "$LOGDEV" 2>/dev/null
		sync
		i=$((i+1))
		sleep 2
	done
) &
