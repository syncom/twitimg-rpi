#/bin/bash
ROOTDIR=`dirname $0`
photo="/mnt/ramdisk/pic.gif"
photo_opt="/mnt/ramdisk/pic_o.gif"
list=$(find /mnt/ramdisk -type f -name "*.jpg" | sort)
# convert to animated gif, 1/2 second delay between frames
convert -delay 50 -loop 1 ${list} ${photo}
# Optimize to reduce gif size
convert -layers Optimize ${photo} ${photo_opt}
mv ${photo_opt} ${photo}
python ${ROOTDIR}/tweet_image.py ${photo}
rm ${list}
#rm ${photo}
