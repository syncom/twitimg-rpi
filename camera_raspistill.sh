#!/bin/bash

DATE=$(date +"%Y-%m-%d_%H%M")
raspistill --nopreview -w 640 -h 480 -q 50 -o /mnt/ramdisk/${DATE}.jpg

