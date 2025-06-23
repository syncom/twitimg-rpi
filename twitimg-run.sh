#/usr/bin/env bash

ROOTDIR=`dirname $0`
photo="/mnt/ramdisk/pic.gif"
list=$(find /mnt/ramdisk -name '*.jpg' | sort)
# strip meta data
mogrify -strip ${list}
# convert to animated gif, 1/2 second delay between frames
convert -delay 50 -loop 1 ${list} ${photo}
# Optimize to reduce gif size
mogrify -layers optimize ${photo}
python ${ROOTDIR}/tweet_image.py ${photo}
rm ${list}
#rm ${photo}
