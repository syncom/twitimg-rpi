#!/usr/bin/env python

"""Tweet motion-detected JPEG image.

This module captures and tweets a motion-detected JPEG image from a Raspberry
Pi with a camera module. The image capture part is credited to the excellent
post https://www.raspberrypi.org/forums/viewtopic.php?t=45235, by brainflakes.
Read brainflakes' original post for the algorithm. I have removed the force
capture part for this script.

"""
import io
import subprocess
import os
import time
import argparse
from datetime import datetime
from PIL import Image
import importlib
import tweet_image

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
    command = f"rpicam-still --nopreview --width {test_width} --height {test_height} --timeout 1000 --encoding bmp --output -"
    output = None
    image_data = io.BytesIO()
    try:
        output = subprocess.check_output(command, shell=True)
    except subprocess.CalledProcessError:
        print("Command exited with non-zero code. No output.")
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
    command = (
        f"rpicam-still --nopreview --width {width} --height {height} "
        f"--timeout 10 --encoding jpg --quality 42 "
        f"--output {dirname.rstrip('/')}/{filename}"
    )
    try:
        subprocess.call(command, shell=True)
    except subprocess.CalledProcessError:
        print("Command exited with non-zero code. No file captured.")
        return None

    print(f"Captured {dirname.rstrip('/')}/{filename}")
    return dirname.rstrip('/') + '/' + filename

# Keep free space above given level
def keepDiskSpaceFree(dirname, bytesToReserve):
    if (get_free_space(dirname) < bytesToReserve):
        for filename in sorted(os.listdir(dirname)):
            if filename.startswith("motion") and filename.endswith(".jpg"):
                os.remove(dirname.rstrip('/') +"/" + filename)
                print(f"Deleted {dirname.rstrip('/')}/{filename} to avoid filling disk")
                if (get_free_space(dirname) > bytesToReserve):
                    return
    return

# Get available disk space
def get_free_space(dir):
    st = os.statvfs(dir)
    du = st.f_bavail * st.f_frsize
    return du
 
# Where work happens
def do_tweet_motion(dirname, is_dryrun=False):
    				          
    # Get first image
    captured1 = False
    image1, buffer1 = None, None
    while (not captured1):
        if is_dryrun:
            print("Dry run mode: not capturing first test image.")
            captured1 = True
        else:
            image1, buffer1 = captureTestImage()
            if image1:
                captured1 = True

    count = 0
    # Main loop
    print("Starting main loop. Press Ctrl+C to stop.")
    while (True):
        print(f"Iteration {count + 1} of main loop")

        # Time granule for wait in the case of error/exception
        basic_wait = 300
        # Double multiplicity when error/exception happens
        mult = 1

        # Get comparison image
        image2, buffer2 = None, None
        captured2 = False
        while (not captured2):
            if is_dryrun:
                print("Dry run mode: not capturing second test image.")
                captured2 = True
            else:
                image2, buffer2 = captureTestImage()
                if image2:
                    captured2 = True

        # Count changed pixels
        changedPixels = 0
        fpath = "/dev/null"

        if is_dryrun:
            print("Dry run mode: not counting changed pixels.")
        else:
            for x in range(0, test_width):
                for y in range(0, test_height):
                    # Just check green channel as it's the highest quality channel
                    pixdiff = abs(buffer1[x,y][1] - buffer2[x,y][1])
                    if pixdiff > threshold:
                        changedPixels += 1

        # Save an image if pixels changed
        if changedPixels > sensitivity:
            fpath = saveImage(save_width, save_height, dirname, reserve_diskspace)
            # Tweet saved image
            if fpath:
                print(f"Image captured with {changedPixels} changed pixels, tweeting {fpath}")
                if is_dryrun:
                    print("Dry run mode: not tweeting.")
                    continue
                else:
                    try:
                        tweet_image.do_tweet(fpath)
                        mult = 1
                    except Exception as e:
                        print("Tweet failed. Encountered exception, as follows: ")
                        print(e)
                        sleeptime = mult * basic_wait
                        time.sleep(sleeptime) # Wait some time
                        print(f"Retry after {sleeptime} seconds")
                        mult = mult * 2
       
        # Swap comparison buffers
        print("Swapping first and second comparison images and buffers")
        image1 = image2
        buffer1 = buffer2

        count += 1
        if is_dryrun and count >= 5:
            print("Dry run mode: exiting after 5 iterations.")
            break

def parse_args():
    parser = argparse.ArgumentParser(description="Tweet motion-detected JPEG image.")
    parser.add_argument("dir_path", help="Directory to save images")
    parser.add_argument("--dry-run", action='store_true', help="Run without tweeting")
    args = parser.parse_args()
    if not os.path.exists(args.dir_path):
        print(f"Directory {args.dir_path} does not exist.")
        exit(1)
    if not os.path.isdir(args.dir_path):
        print(f"Path {args.dir_path} is not a directory.")
        exit(1)
    return args

def main():
    args = parse_args()
    dry_run = args.dry_run
    if dry_run:
        print("Dry run mode enabled.")
    else:
        print("Running in normal mode. Images will be tweeted.")
    
    do_tweet_motion(args.dir_path, is_dryrun=dry_run)

if __name__ == '__main__':
    main()
