#!/usr/bin/env bash

ROOTDIR=`dirname $0`
photo_dir="/mnt/ramdisk_motion"
python ${ROOTDIR}/tweet_motion_jpg.py ${photo_dir}
