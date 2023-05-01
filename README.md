# twitimg-rpi

A simple tool turns a Raspberry Pi (RPi) into a security monitoring system.

# What are needed

- A Raspberry Pi (version 1-3) Model B (needs Internet connectivity)
- A camera module (this would work:
  <https://www.raspberrypi.org/products/camera-module/>)
- imagemagick (for image conversion on the RPi), libssl-dev, build-essential,
  python-imaging, libffi-dev
- Python 2.7: twython, pyOpenSSL, ndg-httpsclient, pyasn1, PIL
- A Twitter account (for multimedia storage and accessibility)

## Tweet a time-lapse GIF every 20 minutes

Usage:

1. Install the camera module on the RPi, and enable camera module from `raspi-config` menu.

2. Create a Twitter app and obtain the API Key, API Secret, Access Token, and
   Access Token Secret for the app. This can be done by following the
   instructions at:
   <http://www.instructables.com/id/Raspberry-Pi-Twitterbot/?ALLSTEPS>. After
   April 2023, if you start seeing API authentication errors, and a message like
   "This app has violated Twitter rules and policies" on the Twitter app setting
   page, sign up for the Free tier of "[Twitter API
   v2](https://developer.twitter.com/en/portal/products)" (at no cost), and
   clicked button "downgrade to free"; this resolved the auth issue
   ([reference](https://twittercommunity.com/t/this-app-has-violated-twitter-rules-and-policies/191204/10)).

3. Override the corresponding strings in the file '.auth' with appropriate
   Twitter app API access token strings obtained in the last step.

4. Because we are going to write and delete a lot of files, in order to prevent
   the SD card worn out, create a ramdisk (of size 25M bytes) to store image
   files created during the process.

   ```bash
   mkdir /mnt/ramdisk
   mount -t tmpfs -o size=25m tmpfs /mnt/ramdisk
   ```

   To make the ramdisk persist over reboots, add the following lines to `/etc/fstab`:

   ```text
   # ramdisk for camera capture (added 20160306)
   tmpfs       /mnt/ramdisk tmpfs   nodev,nosuid,noexec,nodiratime,size=25m   0 0
   ```

5. Create a cron job to take a still picture from the RPi camera module every 1
   minute. Do `crontab -e` and add the following:

   ```text
   # take still picture every 1 minute
   * * * * * /home/pi/bin/twitimg-rpi/camera_raspistill.sh 2>&1
   ```

   Create a cron job to upload an animated GIF image combined from the still
   images taken in the past 20 minutes. Do `crontab -e` and add the following:

   ```text
   # upload image every 20 minutes
   0,20,40 * * * * /home/pi/bin/twitimg-rpi/twitimg-run.sh
   ```

   Because currently Twitter only allows uploading of an animated GIF of maximum
   size of 5M bytes, this setting works well for me. You may want to tweak the
   frequencies of taking still pictures and uploading according to your
   situation.

6. Connect the RPi to the Internet, and watch the stream of videos from your
   Twitter timeline.

7. (Optional) To turn off the LED red light in the camera module when taking
   pictures, edit the file `/boot/config.txt` to add / change the following line:

   ```text
   disable_camera_led=1
   ```

## Tweet a JPEG image upon motion detection

Usage:

1. Follow the same steps 1-3 as above to install the camera module and set up
   the twitter account.

2. Create another ramdisk of size 80M bytes to store motion-detected image
   files.

   ```bash
   mkdir /mnt/ramdisk_motion
   mount -t tmpfs -o size=80M tmpfs /mnt/ramdisk_motion 
   ```

   To make the ramdisk persist over reboots, add the following lines to
   `/etc/fstab`:

   ```text
   # ramdisk for camera capture (added 20170309)
   tmpfs       /mnt/ramdisk_motion tmpfs   nodev,nosuid,noexec,nodiratime,size=80m   0 0
   ```

3. Run `twitimg-motion-run.sh`.

4. (Optional) To run the program upon system boot, create a cron job:

   ```bash
   crontab -e
   ```

   And add the following lines (and redirect stdout and stderr output to a file)

   ```text
   # Upon reboot
   @reboot stdbuf -oL -eL /home/pi/bin/twitimg-rpi/twitimg-motion-run.sh > /home/pi/bin/twitimg-rpi/twitimg.log 2>&1
   ```

   In the above line, we use `stdbuf -oL -eL` tool in the `coreutils` package to
   set line buffering for stdout and stderr, so that log messages are written to
   the log file immediately. (If you wish to completely turn off buffering for
   stdout and stderr, use the `-o0 -e0` options.)

5. (Optional) Reboot the RPI nightly.

   ```bash
   sudo crontab -e
   ```

   Add the following lines

   ```text
   # reboot at 00:05 every day
   0  0 * * * /sbin/shutdown -r +5 
   ```
