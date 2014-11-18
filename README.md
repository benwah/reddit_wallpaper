# Reddit wallpaper getter

Run this script at startup to set your background to a random image from reddit, by default using /r/wallpapers. It works with gnome, smii, spectrwm, and perhaps others. Not KDE or XFCE as far as I know.

**Note**: Reddit sometimes throttles requests to it's json API, or sometimes the request times out. Try again if it fails to work.

**Note2**: It only currently support image links from imgur.com

## Requirements:

* Python 2.7+ or 3

For tiling window managers:

* feh (sudo apt-get install feh)

## Usage:

You can just run:

    $ ./reddit_wallpaper_getter.py

Output of --help:

<pre>
usage: reddit_wallpaper_getter.py [-h] [--destination DESTINATION]
                                  [--overwrite-existing OVERWRITE_EXISTING]
                                  [--output-name OUTPUT_NAME]
                                  [--reddit-json-url REDDIT_JSON_URL]
                                  [--set-wallpaper SET_WALLPAPER]
                                  [--min-resolution MIN_RESOLUTION]

Use reddit for wallpapers

optional arguments:
  -h, --help            show this help message and exit
  --destination DESTINATION
                        Destination directory (default: /home/b/.r_wallpapers)
  --overwrite-existing OVERWRITE_EXISTING
                        Overwrite file if exists? (True / False), default is
                        False
  --output-name OUTPUT_NAME
                        Output filename (defaults to imgur name)
  --reddit-json-url REDDIT_JSON_URL
                        Specify a subreddit .json url. (default http://www.red
                        dit.com/r/wallpapers/top.json?t=week&limit=50)
  --set-wallpaper SET_WALLPAPER
                        Set wallpaper? (True / False), default is True
  --min-resolution MIN_RESOLUTION
                        Specify resolution (format is NxN, example:
                        1920x1080). Enter from 3 to 5 digits. We'll try to
                        guess the resolution based on the post title and
                        permalink
</pre>
