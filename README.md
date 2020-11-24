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

    usage: phetch.py [-h] [--prefer-size-suffix SUFFIX] [--apply-watermark WATERMARK_FILE] [--limit LIMIT] [--delete-missing] album_id output
    
    Download Flickr album images to a directory for use in screensavers, etc
    
    positional arguments:
      album_id              Numeric ID of album from Flickr URL. Can be a comma-separated list.
      output                Directory to save files to
    
    optional arguments:
      -h, --help            show this help message and exit
      --prefer-size-suffix SUFFIX
                            Preferred download size; see README.md
      --apply-watermark WATERMARK_FILE
                            Add watermark to bottom right
      --limit LIMIT         Max images to download
      --delete-missing      Delete images not found in album


eg `python3 phetch.py 72157714807457311 download`

To set up an OSX screensaver using a downloaded album, see [docs/osx-saver.md](docs/osx-saver.md)

Valid size suffixes: See https://www.flickr.com/services/api/misc.urls.html

The watermark function is intended only for download and processing of your own images.

## Code Maturity

This code is [WOMM-compliant](https://blog.codinghorror.com/the-works-on-my-machine-certification-program/); 
it is not intended to be generally robust. Feel free to send requests or PRs, or fork this.

## Credits

Built on https://stuvel.eu/software/flickrapi/