#/bin/bash
ROOTDIR=`dirname $0`
photo="/mnt/ramdisk/pic.jpg"
backup_photo="/mnt/ramdisk/pic_bak.jpg"
# copy and keep timestamp
cp -p ${photo} ${backup_photo}
python ${ROOTDIR}/tweet_image.py ${backup_photo}
rm ${backup_photo}

