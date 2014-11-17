#!/usr/bin/env python

try:
    from urllib.request import urlopen
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import urlopen
    from urllib2 import HTTPError
import subprocess
import os
import json
import re
import random
import argparse


"""
To use default image viewer, install feh. This will work with WMII.
"""

REDDIT_URL = 'http://www.reddit.com/r/wallpapers/top.json?sort=top&t=day'
TIMEOUT = 0.75
DATA_DIR = os.path.join(os.path.expanduser("~"), '.r_wallpapers')
IMAGE_VIEWER = 'feh'
IMAGE_VIEWS_ARGS = ['--bg-center']

MAX_ATTEMPTS = 3
IMGUR_RE = re.compile(
    r'http://(i\.|www\.)?imgur.com/(?P<filename>\w{2,})(\.jpg|/)?$')


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


def get_filename(post, match_re=IMGUR_RE):
    """
    Gets the filename from the post object.
    """
    return (
        match_re.match(post['data']['url']).group('filename')
        + '.jpg')


def get_image(url, max_attempts=MAX_ATTEMPTS, match_re=IMGUR_RE,
              timeout=TIMEOUT):
    """
    Makes a call to reddit and returns one post randomly from the page
    specified in url.
    """
    i = 0
    while True:
        if i == max_attempts:
            raise Exception('Sorry, can\'t reach reddit.')
        try:
            data = json.loads(
                urlopen(url, timeout=timeout).read().decode('utf-8'))
            break
        except HTTPError:
            i += 1
        
    filtered_posts = list(filter(lambda x: match_re.match(
                x.get('data', []).get('url', '')), data.get(
                'data', []).get('children', [])))

    selected_post = filtered_posts[
        random.randint(0, len(filtered_posts) - 1)]
    return (
        get_url(selected_post),
        get_filename(selected_post, match_re),
        )


def save_image(url, file_path, max_attempts=MAX_ATTEMPTS,
               timeout=TIMEOUT):

    f = open(file_path, 'wb')

    i = 0
    while True:
        if i == max_attempts:
            f.close()
            raise Exception('Sorry, can\'t reach imgur.')
        try:
            data = urlopen(url, timeout=timeout).read()
            if len(data) > 0:
                f.write(data)
            else:
                raise Exception('0 Bytes in download, exiting')
            f.close()
            break
        except HTTPError:
            i += 1
    

def display_image(file_path, image_viewer=IMAGE_VIEWER,
                  extra_args=IMAGE_VIEWS_ARGS):
    args = [image_viewer] + IMAGE_VIEWS_ARGS + [file_path]
    subprocess.call(args)


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
        help=(
            'Set wallpaper? (True / False), default is'
            ' True'),
        )

    args = parser.parse_args()

    if not os.path.exists(args.destination) and args.destination == DATA_DIR:
        os.mkdir(args.destination)

    if not os.path.exists(args.destination):
        raise Exception(
            ('Destination directory %s does not exist, or is '
             'unreadable') % args.destination)

    image = get_image(args.reddit_json_url)
    target_file_name = args.output_name or image[1]
    file_path = os.path.join(args.destination, target_file_name)

    if not os.path.exists(file_path) or (
        os.path.exists(file_path) and args.overwrite_existing == 'True'):
        save_image(image[0], file_path)
    else:
        print("File exists on drive.")

    if args.set_wallpaper == 'True':
        display_image(file_path)
