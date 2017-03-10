#!/usr/bin/env python

"""Tweet motion-detected JPEG image.

This module captures and tweets a motion-detected JPEG image from a Raspberry
Pi with a camera module. The image capture part is credited to the excellent
post https://www.raspberrypi.org/forums/viewtopic.php?t=45235, by brainflakes.
Read brainflakes' original post for the algorithm. I have removed the force
capture part for this script.

"""
import StringIO
import subprocess
import os
import time
import argparse
from datetime import datetime
from PIL import Image
import importlib


# Motion detection settings:
# - threshold: how much a pixel has to change by to be marked as "changed"
# - sensitivity: how many changed pixels before capturing an image
threshold = 10
sensitivity = 20
test_width = 100
test_height = 75

# File settings
save_width = 1280
save_height = 960
reserve_diskspace = 40 * 1024 * 1024 # Keep 40 mb free on disk

# Capture a small bitmap test image, for motion detection
def captureTestImage():
    command = "raspistill -w %s -h %s -t 0 -e bmp -o -" % (test_width,
              test_height)
    image_data = StringIO.StringIO()
    image_data.write(subprocess.check_output(command, shell=True))
    image_data.seek(0)
    im = Image.open(image_data)
    buffer = im.load()
    image_data.close()
    return im, buffer

# Save a full size image to disk
def saveImage(width, height, dirname, diskSpaceToReserve):
    keepDiskSpaceFree(dirname, diskSpaceToReserve)
    time = datetime.now()
    filename = "motion-%04d%02d%02d-%02d%02d%02d.jpg" % (time.year, time.month, time.day, time.hour, time.minute, time.second)
    subprocess.call("raspistill -w %s -h %s -t 0 -e jpg -q 15 -o %s/%s" 
                    % (width, height, dirname.rstrip('/'), filename), shell=True)
    print "Captured %s/%s" % (dirname.rstrip('/'), filename)
    return dirname.rstrip('/') + '/' + filename

# Keep free space above given level
def keepDiskSpaceFree(dirname, bytesToReserve):
    if (getFreeSpace(dirname) < bytesToReserve):
        for filename in sorted(os.listdir(dirname)):
            if filename.startswith("motion") and filename.endswith(".jpg"):
                os.remove(dirname.rstrip('/') +"/" + filename)
                print "Deleted %s/%s to avoid filling disk" % ( dirname.rstrip('/'), filename )
                if (getFreeSpace(dirname) > bytesToReserve):
                    return
    return

# Get available disk space
def getFreeSpace(dir):
    st = os.statvfs(dir)
    du = st.f_bavail * st.f_frsize
    return du
 
# Where work happens
def do_tweet_motion(dirname):
    				          
    mod = importlib.import_module("tweet_image")
    # Get first image
    image1, buffer1 = captureTestImage()

    while (True):

        # Get comparison image
        image2, buffer2 = captureTestImage()

        # Count changed pixels
        changedPixels = 0
        for x in xrange(0, test_width):
            for y in xrange(0, test_height):
                # Just check green channel as it's the highest quality channel
                pixdiff = abs(buffer1[x,y][1] - buffer2[x,y][1])
                if pixdiff > threshold:
                    changedPixels += 1

        # Save an image if pixels changed
        if changedPixels > sensitivity:
            fpath = saveImage(save_width, save_height, reserve_diskspace)
       
        # Swap comparison buffers
        image1 = image2
        buffer1 = buffer2
        # Tweet saved image
        mod.do_tweet(fpath)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("dir_path")
    args = parser.parse_args()
    do_tweet_motion(args.dir_path)

