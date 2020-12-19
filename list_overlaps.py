#!/usr/bin/env python
"""
Fetch photos found in multiple Flickr albums. Run with --help for details
"""
import argparse
import sys
from typing import List

from phetch import init_flickr_client
from pictools import FlickrReader
from pictools.types import Photo


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
    filtered = [photo for photo in list_a if photo in list_b]
    return filtered


def run_cli():
    args = parse_cli_args()
    print(args.album_id)
    album_ids: List = args.album_id
    flickr_reader = FlickrReader(init_flickr_client('./config.yml'))
    albums = [flickr_reader.scan_album(album_id) for album_id in album_ids]

    filtered = albums.pop()
    for album in albums:
        filtered = photos_union(filtered, album)

    report_files(filtered)


def report_files(filtered: List[Photo]):
    filenames = [photo['local_file'] for photo in filtered]
    filenames.sort()
    print("\n".join(filenames))


if __name__ == '__main__':
    run_cli()
