#!/usr/bin/env python
"""
Fetch photos found in multiple Flickr albums. Run with --help for details
"""
import argparse
import csv
import random
import re
import sys
from datetime import date, timedelta
from typing import List

from phetch import init_flickr_client
from pictools import FlickrReader
from pictools.types import Photo

PHOTO_URL_PREFIX = "https://www.flickr.com/photos/parsingphase/"


def parse_cli_args() -> argparse.Namespace:
    """
    Specify and parse command-line arguments

    Returns:
        Namespace of provided arguments
    """
    parser = argparse.ArgumentParser(
        description='List photos found in multiple flickr albums',
    )
    parser.add_argument('album_id', help='Numeric IDs of album from Flickr URL', nargs='+')
    args = parser.parse_args()
    if len(args.album_id) < 2:
        print('Must list at least 2 albums')
        parser.print_usage()
        sys.exit(1)
    return args


def photos_union(list_a: List[Photo], list_b: List[Photo]):
    """
    Return photos in both lists
    :param list_a:
    :param list_b:
    :return:
    """
    filtered = [photo for photo in list_a if photo in list_b]
    return filtered


def run_cli() -> None:
    """
    Run script at CLI
    :return:
    """
    args = parse_cli_args()
    album_ids: List = args.album_id
    flickr_reader = FlickrReader(init_flickr_client('./config.yml'))
    flickr_reader.set_silent(True)
    albums = [flickr_reader.scan_album(album_id) for album_id in album_ids]

    filtered = albums.pop()
    for album in albums:
        filtered = photos_union(filtered, album)

    # report_files(filtered)
    shuffle_and_prepend_date(filtered, date.today(), True)


def report_files(filtered: List[Photo]):
    """
    Report a sorted list of filenames
    :param filtered:
    :return:
    """
    filenames = [photo['local_file'] for photo in filtered]
    filenames.sort()
    print("\n".join(filenames))


def shuffle_and_prepend_date(filtered: List[Photo], start: date, as_csv: bool = False):
    """
    Generate a random schedule on STDOUT
    :param filtered:
    :param start:
    :param as_csv:
    :return:
    """
    csv_writer = csv.writer(sys.stdout) if as_csv else None

    filenames = [photo['local_file'] for photo in filtered]
    random.shuffle(filenames)
    today = start
    for filename in filenames:
        target_date = today.strftime('%Y%m%d')
        if csv_writer:
            matched = re.search(r"_(\d{11,12})\.", filename)
            photo_id = matched.group(1) if matched else 'n-a'
            csv_writer.writerow([target_date, filename, PHOTO_URL_PREFIX + photo_id])
        else:
            print(target_date + '_' + filename)
        today = today + timedelta(days=1)


if __name__ == '__main__':
    run_cli()
