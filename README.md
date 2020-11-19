Flickr API tools [![Build Status](https://travis-ci.org/parsingphase/phetch.svg?branch=master)](https://travis-ci.org/parsingphase/phetch)
================

## Setup 

### On macOS / *nix:

    python3 -m venv venv
    source ./venv/bin/activate
    make install

## Configuration

- Get a non-commercial key from https://www.flickr.com/services/apps/create/noncommercial/
- Copy `flickr.yml.sample` to `flickr.yml` and fill in the values from this key

## Tools

#### phetch.py

Fetch images from a list of albums into a local directory

For usage, `python3 phetch.py --help`

    usage: phetch.py [-h] [--prefer-size-suffix PREFER_SIZE_SUFFIX] [--limit LIMIT] album_id output
    
    Download Flickr album images to a directory for use in screensavers, etc
    
    positional arguments:
      album_id              Numeric ID of album from Flickr URL. Can be a comma-separated list.
      output                Directory to save files to
    
    optional arguments:
      -h, --help            show this help message and exit
      --prefer-size-suffix PREFER_SIZE_SUFFIX
                            Preferred download size; see README.md
      --limit LIMIT         Max images to download per album


eg `python3 phetch.py 72157714807457311 download`

To set up an OSX screensaver using a downloaded album, see [docs/osx-saver.md](docs/osx-saver.md)

Valid size suffixes: See https://www.flickr.com/services/api/misc.urls.html

## Credits

Built on https://stuvel.eu/software/flickrapi/