#!/usr/bin/env python
"""
Fetch one or more Flickr albums. Run with --help for details
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Union

import flickrapi

from pictools import FlickrReader, PhotoListFetcher, Watermarker, load_config


def parse_cli_args() -> argparse.Namespace:
    """
    Specify and parse command-line arguments

    Returns:
        Namespace of provided arguments
    """
    parser = argparse.ArgumentParser(
        description='Download Flickr album images to a directory for use in screensavers, etc',
    )
    parser.add_argument('album_id', help='Numeric ID of album from Flickr URL. Can be a comma-separated list.')
    parser.add_argument('output', help='Directory to save files to', nargs='?')
    parser.add_argument('--no-download', help="Don't download any files", required=False)
    parser.add_argument('--prefer-size-suffix', required=False, help='Preferred download size; see README.md',
                        dest='suffix')
    parser.add_argument('--apply-watermark', required=False, help='Add watermark to bottom right', type=str,
                        dest='watermark_file')
    parser.add_argument('--watermark-opacity', required=False, help='Set watermark opacity, 0-1', type=float)
    parser.add_argument('--limit', required=False, help='Max images to download', type=int, default=0)
    parser.add_argument('--delete-missing', help='Delete images not found in album', action="store_true")
    parser.add_argument('--sort-order', help='One of ', choices=PhotoListFetcher.get_sort_keys(), default='natural')
    parser.add_argument('--sort-reverse', help='Reverse sort order', action='store_true')
    parser.add_argument('--save-photo-list', help='File to export JSON album index to')
    args = parser.parse_args()
    if args.watermark_opacity and not args.watermark_file:
        print('--watermark-opacity is invalid without --apply-watermark')
        parser.print_usage()
        sys.exit(1)
    if (not args.output and not args.no_download) or (args.output and args.no_download):
        print('Must specify either output or --no-download, but not both')
        parser.print_usage()
        sys.exit(1)
    if args.no_download and (args.watermark_file or args.limit):
        print("Can't watermark or limit when not downloading")
        parser.print_usage()
        sys.exit(1)

    return args


def init_flickr_client(config_file: str):
    """
    Initialise and return flickr client library using specified config file
    :param config_file:
    :return:
    """
    config = load_config(config_file)['flickr']

    flickr = flickrapi.FlickrAPI(config['api_key'], config['api_secret'], format='parsed-json')

    return flickr


def run_cli() -> None:
    """
    Run the script from the CLI
    :return:
    """
    args = parse_cli_args()
    flickr_reader = FlickrReader(init_flickr_client('./config.yml'))
    if args.suffix:
        flickr_reader.set_preferred_size_suffix(args.suffix)

    albums = args.album_id.split(',')
    photos = flickr_reader.scan_albums(albums)

    output_dir = args.output.rstrip('/')

    downloader = PhotoListFetcher()
    if not args.no_download:
        if args.watermark_file:
            watermarker = Watermarker(args.watermark_file)
            if args.watermark_opacity:
                watermarker.set_watermark_opacity(args.watermark_opacity)
            downloader.set_post_download_callback(watermarker.mark_in_place)

        limit = args.limit
        sort = args.sort_order
        reverse = args.sort_reverse

        ensure_dir(output_dir)
        selected_photos = downloader.order_photo_list(photos, sort, reverse, limit)
        downloader.fetch_photos(selected_photos, output_dir)

    if args.delete_missing:
        downloader.remove_local_without_remote(photos, local_dir=output_dir)

    photo_list = args.save_photo_list
    if photo_list:
        ensure_dir(Path(photo_list).parent)
        with open(photo_list, 'w') as json_out:
            json.dump(photos, json_out)
            print(f"Wrote file list to {photo_list}")

    print('All done')


def ensure_dir(target_dir: Union[Path, str]):
    """
    Make sure that a required directory exists
    :param target_dir:
    :return:
    """
    target = Path(target_dir)
    if not target.is_dir():
        if target.exists():
            raise FileExistsError(f"{target_dir} exists but is not a directory")
        print(f'{target_dir} did not exist, creating it')
        target.mkdir(parents=True)


if __name__ == '__main__':
    run_cli()
