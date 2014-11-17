# Reddit wallpaper getter

This will get images from reddit.com and use feh to set it as your background. Mostly useful for tiling windows managers like wmii, i3, awesome or spectrwm

## Usage:

You can just run:

    $ ./reddit_wallpaper_getter.py

Output of --help:

usage: reddit_wallpaper_getter.py [-h] [--destination DESTINATION]
                                  [--overwrite-existing OVERWRITE_EXISTING]
                                  [--output-name OUTPUT_NAME]
                                  [--reddit-json-url REDDIT_JSON_URL]
                                  [--set-wallpaper SET_WALLPAPER]

Use reddit for wallpapers

optional arguments:
  -h, --help            show this help message and exit
  --destination DESTINATION
                        Destination directory (default: /home/b/.r_wallpapers)
  --overwrite-existing OVERWRITE_EXISTING
                        Overwrite file if exists? (True / False), default is False
  --output-name OUTPUT_NAME
                        Output filename (defaults to imgur name)
  --reddit-json-url REDDIT_JSON_URL
                        Specify a subreddit .json url. (default http://www.reddit.com/r/wallpapers/top.json?sort=top&t=day)
  --set-wallpaper SET_WALLPAPER
                        Set wallpaper? (True / False), default is True
