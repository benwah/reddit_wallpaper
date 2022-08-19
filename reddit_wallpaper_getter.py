#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib.request import urlopen
from urllib.error import HTTPError
import time
import sys
import subprocess
import os
import json
import re
import random
import argparse
import socket


SOURCES = [
    'http://www.reddit.com/r/WQHD_Wallpaper/top.json?t=week&limit=10',
    'http://www.reddit.com/r/wallpapers/top.json?t=week&limit=10',
    'http://www.reddit.com/r/wallpaper/top.json?t=week&limit=10',
    'http://www.reddit.com/r/EarthPorn/top.json?t=week&limit=10',
    'http://www.reddit.com/r/CityPorn/top.json?t=week&limit=10',
    'http://www.reddit.com/r/SkyPorn/top.json?t=week&limit=10',
    'http://www.reddit.com/r/WeatherPorn/top.json?t=week&limit=10',
    'http://www.reddit.com/r/BotanicalPorn/top.json?t=week&limit=10',
    'http://www.reddit.com/r/SpacePorn/top.json?t=week&limit=10',
]
TIMEOUT = 3
DATA_DIR = os.path.join(os.path.expanduser("~"), 'Pictures', 'wallpapers')

MAX_ATTEMPTS = 3
SLEEP_SECONDS_AFTER_ATTEMPT = 2
REGEXES = [
    re.compile(
        r'https://i\.redd\.it/(?P<filename>\w{2,})(\.jpg|\.png|/)?$'
    ),
    re.compile(
        r'https://live\.staticflickr\.com/[0-9]+/(?P<filename>[\w]+\.(png|jpg))'
    ),
]
RES_RE = re.compile('\d{3,5}x\d{3,5}')
RES_DATA_RE = re.compile(
    r'.*([^\d]|^)+(?P<x>\d{3,5}) ?(x|_|×){1} ?(?P<y>\d{3,5}).*', re.UNICODE)


def get_image(url, desired_res=None):
    """
    Makes a call to reddit and returns one post randomly from the page
    specified in url.
    """
    i = 0
    while True:
        if i == MAX_ATTEMPTS:
            raise Exception('Sorry, can\'t reach reddit.')
        try:
            data = json.loads(
                urlopen(url, timeout=TIMEOUT).read().decode('utf-8'))

            break
        except HTTPError as e:
            # Too many requests, give reddit a break, try again.
            print("JSON api throttled, attempt %s on %s" % (i, MAX_ATTEMPTS))
            if getattr(e, 'code', None) == 429:
                time.sleep(SLEEP_SECONDS_AFTER_ATTEMPT)
            i += 1
        except socket.timeout:
            print("Timeout, attempt %s on %s" % (i, MAX_ATTEMPTS))
            time.sleep(SLEEP_SECONDS_AFTER_ATTEMPT)
            i += 1

    candidates = []

    # Alright let's try to find some images with matching resolution.
    for item in data.get('data', {}).get('children', {}):
        url = item.get('data', {}).get('url', '')
        print(url)
        for regex in REGEXES:
            if image_match := regex.match(url):
                if desired_res:
                    title = item.get('data', {}).get('title', '')
                    permalink = item.get('data', {}).get('permalink', '')

                    match = (RES_DATA_RE.match(permalink) or
                             RES_DATA_RE.match(title))

                    if match:
                        found_res = match.groupdict()
                        if (
                                int(desired_res[0]) <= int(found_res['x'])
                                and int(desired_res[1]) <= int(found_res['y'])):
                            candidates.append((url, image_match[1]))
                else:
                    candidates.append((url, image_match[1]))

    if len(candidates) == 0:
        return None
    else:
        return random.choice(candidates)


def save_image(url, file_path):
    f = open(file_path, 'wb')

    i = 0
    while True:
        if i == MAX_ATTEMPTS:
            f.close()
            raise Exception('Sorry, can\'t reach host.')
        try:
            data = urlopen(url, timeout=TIMEOUT).read()
            if len(data) > 0:
                f.write(data)
            else:
                raise Exception('0 Bytes in download, exiting')
            f.close()
            break
        except HTTPError as exc:
            time.sleep(1)
            i += 1
        except socket.timeout:
            # Socket timeout, try again.
            i += 1


def display_image(file_path):
    # Try to find background setter
    commands = [
        [
            'gsettings',
            'set',
            'org.gnome.desktop.background',
            'picture-uri',
            f'file://{file_path}'
        ],
        [
            'gsettings',
            'set',
            'org.gnome.desktop.background',
            'picture-uri-dark',
            f'file://{file_path}'
        ],
    ]
    for pargs in commands:
        subprocess.call(pargs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=('Use reddit for wallpapers'))

    parser.add_argument(
        '--destination',
        type=str,
        default=DATA_DIR,
        help='Destination directory (default: %s)' % DATA_DIR,
        )

    parser.add_argument(
        '--overwrite-existing',
        type=str,
        default='',
        help=(
            'Overwrite file if exists? (True / False), default is'
            ' False'),
        )

    parser.add_argument(
        '--output-name',
        type=str,
        default=None,
        help='Output filename (defaults to imgur name)',
        )

    parser.add_argument(
        '--reddit-json-url',
        type=str,
        default=None,
        help='Specify a subreddit .json url.'
        )

    parser.add_argument(
        '--set-wallpaper',
        type=str,
        default='True',
        help='Set wallpaper? (True / False), default is True',
    )

    parser.add_argument(
        '--min-resolution',
        type=str,
        default='None',
        help=('Specify resolution (format is NxN, example: 1920x1080). '
              'Enter from 3 to 5 digits. We\'ll try to guess the '
              'resolution based on the post title and permalink')
    )

    args = parser.parse_args()

    if not os.path.exists(args.destination) and args.destination == DATA_DIR:
        os.mkdir(args.destination)

    if not os.path.exists(args.destination):
        raise Exception(
            ('Destination directory %s does not exist, or is '
             'unreadable') % args.destination)

    if args.min_resolution == 'None':
        desired_res = None
    elif RES_RE.match(args.min_resolution):
        desired_res = args.min_resolution.split('x')
    else:
        print("Error: Bad resolution, or resolution too big (or small)\n")
        parser.print_help()
        sys.exit(1)

    reddit_json_url = args.reddit_json_url or random.choice(SOURCES)

    print(f"Attempting to fetch from {reddit_json_url}")
    image = get_image(reddit_json_url, desired_res=desired_res)

    if not image:
        print("No image found")
        sys.exit(1)

    target_file_name = args.output_name or image[1]
    file_path = os.path.join(args.destination, target_file_name)

    if not os.path.exists(file_path) or (
            os.path.exists(file_path) and
            args.overwrite_existing == 'True'):
        save_image(image[0], file_path)

    if args.set_wallpaper == 'True':
        display_image(file_path)
