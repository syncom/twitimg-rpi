#!/usr/bin/env python

import os
import sys
import argparse
import time
import datetime
from twython import Twython

ApiKey = ''
ApiSecret = ''
AccessToken = ''
AccessTokenSecret = ''
cred_file = os.path.dirname(os.path.realpath(__file__)) +'/.auth'
twitter_allowed_char = 140

def get_api_token():
    ''' Obtain Twitter app's API token from file .auth
    Returns list
    '''
    f = open(cred_file, 'rb')
    c = f.read()
    t = c.splitlines()
    return t[0:4]

def get_mtime_str(file):
    ''' Obtain file modification time string.

    Return str
    '''
    try:
        mtime = os.path.getmtime(file)
    except OSError:
        return ''
    is_dst = time.daylight and time.localtime().tm_isdst > 0
    # UTC offset in seconds
    offset = - (time.altzone if is_dst else time.timezone)
    time_str = time.ctime(mtime) + ' UTC' + str(offset/3600)
    return time_str


def do_tweet(file):
    ''' Tweet image modification time and image to Twitter
    '''
    [ApiKey, ApiSecret, AccessToken, AccessTokenSecret] = get_api_token()
    api = Twython(ApiKey, ApiSecret, AccessToken, AccessTokenSecret)
    str = get_mtime_str(file)
    if not str:
        print("Something went wrong. Nothing was tweeted.")
    else:
        photo = open(file, 'rb')
        response = api.upload_media(media=photo)
        api.update_status(status=str, media_ids=[response['media_id']])
        print(f"Tweeted image taken at {str}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path")
    args = parser.parse_args()
    do_tweet(args.image_path)
