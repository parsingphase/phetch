#!/usr/bin/env python
"""
Fetch photos found in multiple Flickr albums. Run with --help for details
"""
import argparse
import csv
import random
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List

from cron_image_tweet import scan_file_for_coded_filenames
from phetch import init_flickr_client
from phetch_tools import FlickrReader
from phetch_tools.types import Photo

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
    parser.add_argument('--from-date', help='Start date in YYYYmmdd format')
    parser.add_argument('--unique-titles', help='Output only one row per title', action='store_true')
    parser.add_argument('--exclude-from-file', help='Exclude photos already listed in file')
    parser.add_argument('--csv', help='Output as CSV', action='store_true')
    args = parser.parse_args()
    if len(args.album_id) < 2:
        print('Must list at least 2 albums')
        parser.print_usage()
        sys.exit(1)
    return args


def photos_intersection(list_a: List[Photo], list_b: List[Photo]):
    """
    Return photos in both lists
    :param list_a:
    :param list_b:
    :return:
    """
    filtered = [photo for photo in list_a if photo in list_b]
    return filtered


def unique_titles(photos: List[Photo], defer_remainder=False) -> List[Photo]:
    """
    Filter out multiple photos of the same title, keeping only the first
    :param defer_remainder: Whether to re-uniquify non-unique photos and append them
    :param photos:
    :return:
    """
    seen_titles = []
    filtered = []
    deferred = []
    for photo in photos:
        if photo['title'] in seen_titles:
            deferred.append(photo)
        else:
            filtered.append(photo)
            seen_titles.append(photo['title'])

    if defer_remainder and len(deferred) > 0:
        filtered = filtered + unique_titles(deferred, True)

    return filtered


def exclude_from_file(photos: List[Photo], exclusion_file: str) -> List[Photo]:
    """

    :param filtered:
    :param exclusion_file:
    :return:
    """
    exclusion_path = Path(exclusion_file)
    if not exclusion_path.exists():
        raise FileNotFoundError(f"{exclusion_file} not found")
    exclusions = scan_file_for_coded_filenames(exclusion_path)
    exclude_ids = [p['photo_id'] for p in exclusions]
    filtered: List[Photo] = []

    pattern = r"^(?P<description>\S+)_(?P<photo_id>\d{11,12})(\.jpg)?$"
    for photo in photos:
        match = re.match(pattern, photo['local_file'])
        if match:
            matches = match.groupdict()
            if matches['photo_id'] not in exclude_ids:
                filtered.append(photo)

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
        filtered = photos_intersection(filtered, album)

    if args.unique_titles:
        filtered = unique_titles(filtered, False)  # used as a pure uniqueness function here

    if args.exclude_from_file:
        filtered = exclude_from_file(filtered, args.exclude_from_file)

    # report_files(filtered)
    from_date = datetime.strptime(args.from_date, '%Y%m%d').date() if args.from_date else date.today()
    shuffle_and_prepend_date(filtered, from_date, args.csv)


def report_files(filtered: List[Photo]):
    """
    Report a sorted list of filenames
    :param filtered:
    :return:
    """
    filenames = [photo['local_file'] for photo in filtered]
    filenames.sort()
    print("\n".join(filenames))


def shuffle_and_prepend_date(photos: List[Photo], start: date, as_csv: bool = False):
    """
    Generate a random schedule on STDOUT
    :param photos:
    :param start:
    :param as_csv:
    :return:
    """
    csv_writer = csv.writer(sys.stdout) if as_csv else None

    # Make the photos random, but not too random
    random.shuffle(photos)
    photos = unique_titles(photos, True)  # used to reduce clustering here

    filenames = [photo['local_file'] for photo in photos]
    today = start
    for filename in filenames:
        target_date = today.strftime('%Y%m%d')
        if csv_writer:
            matched = re.search(r"_(\d{11,12})\.", filename)
            photo_id = matched.group(1) if matched else None
            csv_writer.writerow([target_date, filename, PHOTO_URL_PREFIX + photo_id if photo_id else ''])
        else:
            print(target_date + '_' + filename)
        today = today + timedelta(days=1)


if __name__ == '__main__':
    run_cli()
