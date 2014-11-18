#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from urllib.request import urlopen
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import urlopen
    from urllib2 import HTTPError
import time
import sys
import subprocess
import os
import json
import re
import random
import argparse
import socket


REDDIT_URL = 'http://www.reddit.com/r/wallpapers/top.json?t=week&limit=50'
TIMEOUT = 2
DATA_DIR = os.path.join(os.path.expanduser("~"), '.r_wallpapers')

MAX_ATTEMPTS = 3
IMGUR_RE = re.compile(
    r'http://(i\.|www\.)?imgur.com/(?P<filename>\w{2,})(\.jpg|/)?$')
RES_RE = re.compile('\d{3,5}x\d{3,5}')
RES_DATA_RE = re.compile(
    r'.*([^\d]|^)+(?P<x>\d{3,5}) ?(x|_|×){1} ?(?P<y>\d{3,5}).*', re.UNICODE)


ARG_MAP = {
    'feh': ['feh', ['--bg-center'], '%s'],
    'gnome': ['gsettings',
              ['set', 'org.gnome.desktop.background', 'picture-uri'],
              'file://%s']
}

WM_BKG_SETTERS = {
    'spectrwm': ARG_MAP['feh'],
    'scrotwm': ARG_MAP['feh'],
    'wmii': ARG_MAP['feh'],
    'i3': ARG_MAP['feh'],
    'awesome': ARG_MAP['feh'],
    'awesome-gnome': ARG_MAP['gnome'],
    'gnome': ARG_MAP['gnome'],
    'ubuntu': ARG_MAP['gnome']
}


def get_url(post):
    """
    Gets the url of the actual JPG file from the post object.
    """
    url = post['data']['url']
    if url.endswith == 'jpg':
        return url
    elif url.endswith == '/':
        return url.strip('/') + '.jpg'
    else:
        return url + '.jpg'


def get_filename(post):
    """
    Gets the filename from the post object.
    """
    return (
        IMGUR_RE.match(post['data']['url']).group('filename')
        + '.jpg')


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
            if getattr(e, 'code', None) == 429:
                time.sleep(1)
            i += 1
        except socket.timeout:
            # Socket timeout, try again.
            i += 1

    candidates = []

    # Alright let's try to find some images with matching resolution.
    for item in data.get('data', {}).get('children', {}):
        url = item.get('data', {}).get('url', '')
        if IMGUR_RE.match(url):
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
                        candidates.append(item)
            else:
                candidates.append(item)

    if len(candidates) == 0:
        return None
    else:
        image = candidates[random.randrange(0, len(candidates))]
        return (
            get_url(image),
            get_filename(image),
        )


def save_image(url, file_path):

    f = open(file_path, 'wb')

    i = 0
    while True:
        if i == MAX_ATTEMPTS:
            f.close()
            raise Exception('Sorry, can\'t reach imgur.')
        try:
            data = urlopen(url, timeout=TIMEOUT).read()
            if len(data) > 0:
                f.write(data)
            else:
                raise Exception('0 Bytes in download, exiting')
            f.close()
            break
        except HTTPError:
            time.sleep(1)
            i += 1
        except socket.timeout:
            # Socket timeout, try again.
            i += 1


def background_setter():
    pass


def display_image(file_path):
    # Try to find background setter
    desktop_environ = os.environ.get('DESKTOP_SESSION', '')

    if desktop_environ and desktop_environ in WM_BKG_SETTERS:
        bkg_setter, args, pic_arg = WM_BKG_SETTERS.get(
            desktop_environ, [None, None])
    else:
        bkg_setter, args, pic_arg = WM_BKG_SETTERS['spectrwm']

    pargs = [bkg_setter] + args + [pic_arg % file_path]
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
        default=REDDIT_URL,
        help='Specify a subreddit .json url. (default %s)' % REDDIT_URL,
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

    image = get_image(args.reddit_json_url, desired_res=desired_res)

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
