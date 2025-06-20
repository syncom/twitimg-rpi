#!/usr/bin/env bash
# This script captures an image using the Raspberry Pi camera and saves it to a
# RAM disk.  Ensure the RAM disk is mounted at /mnt/ramdisk

DATE=$(date +"%Y-%m-%d_%H%M")
rpicam-still --width 640 --height 480 --quality 15 -o /mnt/ramdisk/${DATE}.jpg
