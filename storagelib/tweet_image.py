#!/usr/bin/env python

from pathlib import Path
import os
import argparse
import time
import tweepy

twitter_allowed_char = 140
current_dir = Path(__file__).parent.resolve()
CRED_FILE = current_dir / '.auth'

def get_credential():
    """Botain Twitter app's API credentials from environment or file .auth

    If any of the environment variables TWITIMG_API_KEY, TWITIMG_API_SECRET,
    TWITIMG_ACCESS_TOKEN, TWITIMG_ACCESS_TOKEN_SECRET is set, it will be used.
    Otherwise, the credentials will be read from the file .auth

    Returns:
        list: A list containing API key, API secret, access token, and access token secret.
    """
    api_key = os.environ.get('TWITIMG_API_KEY')
    api_secret = os.environ.get('TWITIMG_API_SECRET')
    access_token = os.environ.get('TWITIMG_ACCESS_TOKEN')
    access_token_secret = os.environ.get('TWITIMG_ACCESS_TOKEN_SECRET')
    credential = [api_key, api_secret, access_token, access_token_secret]

    if os.path.exists(CRED_FILE):
        with open(CRED_FILE, 'r', encoding='utf-8') as fil:
            content = fil.read()
            templ = content.splitlines()
            if len(templ) < 4:
                raise ValueError(CRED_FILE
                                + " is malformed. "
                                + "It needs to contain at least 4 secrets")
            return [fil if env is None else env
                    for env, fil in zip(credential, templ)]

    return credential

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
    [api_key, api_secret, access_token, access_token_secret] = get_credential()
    auth = tweepy.OAuth1UserHandler(
        api_key, api_secret, access_token, access_token_secret)
    api = tweepy.API(auth)
    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    try:
        image = api.media_upload(filename=file)
        print(f"Image {file} uploaded successfully. Media ID: {image.media_id}")

        status_str = get_mtime_str(file)

        response = client.create_tweet(
            text=status_str[:twitter_allowed_char],
            media_ids=[image.media_id]
        )

        print(f"Tweeted image taken at {status_str}")
        print(response)
    except tweepy.TweepyException as e:
        print(f"Error occurred: {e}")
        raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path")
    args = parser.parse_args()
    do_tweet(args.image_path)
