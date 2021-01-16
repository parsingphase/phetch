Flickr API tools [![Build Status](https://travis-ci.org/parsingphase/phetch.svg?branch=master)](https://travis-ci.org/parsingphase/phetch)
================

## Setup 

### On macOS / *nix:

    python3 -m venv venv
    source ./venv/bin/activate
    make install

## Configuration

- Get a non-commercial key from https://www.flickr.com/services/apps/create/noncommercial/
- Copy `config.yml.sample` to `config.yml` and fill in the values from this key
- Twitter keys can be obtained from https://developer.twitter.com/en/apps, if needed

## Tools

#### phetch.py

Fetch images from a list of albums into a local directory

For usage, `python3 phetch.py --help`

    usage: phetch.py [-h] [--no-download] [--prefer-size-suffix SUFFIX] [--apply-watermark WATERMARK_FILE] [--watermark-opacity WATERMARK_OPACITY] [--limit LIMIT] [--delete-missing]
                     [--sort-order {natural,random,alphabetical,taken}] [--sort-reverse] [--save-photo-list SAVE_PHOTO_LIST]
                     album_id [output]
    
    Download Flickr album images to a directory for use in screensavers, etc
    
    positional arguments:
      album_id              Numeric ID of album from Flickr URL. Can be a comma-separated list.
      output                Directory to save files to
    
    optional arguments:
      -h, --help            show this help message and exit
      --no-download         Don't download any files
      --prefer-size-suffix SUFFIX
                            Preferred download size; see README.md
      --apply-watermark WATERMARK_FILE
                            Add watermark to bottom right
      --watermark-opacity WATERMARK_OPACITY
                            Set watermark opacity, 0-1
      --limit LIMIT         Max images to download
      --delete-missing      Delete images not found in album
      --sort-order {natural,random,alphabetical,taken}
                            One of
      --sort-reverse        Reverse sort order
      --save-photo-list SAVE_PHOTO_LIST
                            File to export JSON album index to

eg `python3 phetch.py 72157714807457311 download`

To set up an OSX screensaver using a downloaded album, see [docs/osx-saver.md](docs/osx-saver.md)

Valid size suffixes: See https://www.flickr.com/services/api/misc.urls.html

The watermark function is intended only for download and processing of your own images.

#### automark.py

Watermark all of the JPG images in a specified folder, adding new versions in a subdirectory. 
You will need to supply a transparent png/gif as  the watermark. The watermark is assumed to be 
white-on-transparent and will be inverted when being applied to a lighter area.

For usage, `python3 automark.py --help`

    usage: automark.py [-h] [--limit LIMIT] [--resize MAX_EDGE] dir
    
    Watermark images in a directory, saved to a /watermarks subdirectory
    
    positional arguments:
      dir                Directory containing files to watermark
    
    optional arguments:
      -h, --help         show this help message and exit
      --limit LIMIT      Max images to process
      --resize MAX_EDGE  Resize to fit box

#### cron_image_tweet.py

Post tweets containing an image on a daily schedule. The script can take input in two forms; either
a directory full of files or a text file listing images to post. The format of filenames or lines of
the file should be:

    20211219_red-winged_blackbird_49947009881.jpg

ie:
    
    YYYYMMDD_description_FLICKRID.jpg

Each time the script runs, it will check today's date, look for a flickr ID in a filename containing
that date, and use the Flickr and Twitter APIs to find, describe and tweet that image.

This script can be also used as an AWS lambda script, to run from a Cloudwatch schedule.
The batch file "build-potd-lambda.sh" helps build the appropriate lambda bundle.

For usage, `python3 cron_image_tweet.py --help`

    usage: cron_image_tweet.py [-h] (--source-flickr-download-dir SOURCE_FLICKR_DOWNLOAD_DIR | --source-flickr-file-list SOURCE_FLICKR_FILE_LIST) [--dry-run]
    
    Create tweet with image from encoded input
    
    optional arguments:
      -h, --help            show this help message and exit
      --source-flickr-download-dir SOURCE_FLICKR_DOWNLOAD_DIR
                            Directory of coded flickr downloads to use as source
      --source-flickr-file-list SOURCE_FLICKR_FILE_LIST
                            File containing list of Flickr photo dates/ids  
      --dry-run             Prepare the tweet but don't send it
    
#### introspect.py

Modifies image keywords, subject and filename to help find and identify files, for all files in a 
directory:

 - If no subject, longest keyword is assumed to be subject
 - Any image ID found in the filename is stored as a keyword 'library:fileId=NUMBER'
 - Optionally, filename is modified to include the subject

Usage: `python3 introspect.py -h`

    usage: introspect.py [-h] [--rename] dir
    
    Improve keywords and title organization for all images in a folder for upload to flickr, etc
    
    positional arguments:
      dir         Directory containing files to watermark
    
    optional arguments:
      -h, --help  show this help message and exit
      --rename    Modify filename to include subject

#### list_overlaps.py

A utility script to help generate a list of files suitable for `cron_image_tweet.py`

This script is very specific to my workflow, so feel free to work with it but I won't document it here.
`--help` works as you'd expect.

#### fetch_from_json.py

Another utility script, this one lets you download files listed in a JSON file of specific format, 
which can be hosted online or shared.

Again, fairly specific to my use-case, so use `--help` for info

JSON format is:

    [
        {
        "url": "https://domain.tld/path/to/file.jpg",
        "local_file": "intended_local_filename.jpg",
        "title": "Plain Text",
        "taken": "2020-07-04 12:04:54"
        },
    ...
    ]

## Code Maturity

This code is [WOMM-compliant](https://blog.codinghorror.com/the-works-on-my-machine-certification-program/); 
it is not intended to be generally robust. Feel free to send requests or PRs, or fork this.

## Credits

Built on https://stuvel.eu/software/flickrapi/