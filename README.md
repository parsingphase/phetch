Flickr API tools
================

Uses https://stuvel.eu/software/flickrapi/

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

eg `python3 phetch.py 72157714807457311 download`

To set up an OSX screensaver using a downloaded album, see [docs/osx-saver.md]

Valid size suffixes: See https://www.flickr.com/services/api/misc.urls.html