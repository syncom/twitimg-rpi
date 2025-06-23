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
from twython import Twython

# Motion detection settings:
# - threshold: how much a pixel has to change by to be marked as "changed"
# - sensitivity: how many changed pixels before capturing an image
threshold = 10
sensitivity = 800
test_width = 100
test_height = 75

# File settings
save_width = 1280
save_height = 960
reserve_diskspace = 40 * 1024 * 1024 # Keep 40 mb free on disk

# Capture a small bitmap test image, for motion detection
def captureTestImage():
    command = "raspistill -n -w %s -h %s -t 1000 -e bmp -o -" % (test_width,
              test_height)
    output = None
    image_data = StringIO.StringIO()
    try:
        output = subprocess.check_output(command, shell=True)
    except subprocess.CalledProcessError:
        print "Command exited with non-zero code. No output."
        return None, None

    if output:
        image_data.write(output)
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
    command = "raspistill -n -w %s -h %s -t 10 -e jpg -q 15 -o %s/%s" % (width, height, dirname.rstrip('/'), filename)
    try:
        subprocess.call(command, shell=True)
    except subprocess.CalledProcessError:
        print "Command exited with non-zero code. No file captured."
        return None

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
    captured1 = False
    while (not captured1):
        image1, buffer1 = captureTestImage()
        if image1:
            captured1 = True

    while (True):
        # Time granule for wait in the case of error/exception
        basic_wait = 300
        # Double multiplicity when error/exception happens
        mult = 1

        # Get comparison image
        captured2 = False
        while (not captured2):
            image2, buffer2 = captureTestImage()
            if image2:
                captured2 = True

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
            fpath = saveImage(save_width, save_height, dirname, reserve_diskspace)
            # Tweet saved image
            if fpath:
                try:
                    mod.do_tweet(fpath)
                    mult = 1
                except Exception as e:
                    print "Tweet failed. Encountered exception, as follows: "
                    print(e)
                    sleeptime = mult * basic_wait
                    time.sleep(sleeptime) # Wait some time
                    print("Retry after {0} seconds".format(sleeptime))
                    mult = mult * 2
       
        # Swap comparison buffers
        image1 = image2
        buffer1 = buffer2

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("dir_path")
    args = parser.parse_args()
    do_tweet_motion(args.dir_path)
