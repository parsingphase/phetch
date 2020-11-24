#!/usr/bin/env python
"""
Fetch one or more Flickr albums. Run with --help for details
"""

import argparse
import sys
from pathlib import Path

import flickrapi
from yaml import BaseLoader
from yaml import load as yload

from downloader import Downloader
from watermarker import Watermarker


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
    parser.add_argument('output', help='Directory to save files to')
    parser.add_argument('--prefer-size-suffix', required=False, help='Preferred download size; see README.md',
                        dest='suffix')
    parser.add_argument('--apply-watermark', required=False, help='Add watermark to bottom right', type=str,
                        dest='watermark_file')
    parser.add_argument('--limit', required=False, help='Max images to download', type=int, default=0)
    parser.add_argument('--delete-missing', help='Delete images not found in album', action="store_true")
    args = parser.parse_args()
    return args


def init_flickr_client(config_file: str):
    """
    Initialise and return flickr client library using specified config file
    :param config_file:
    :return:
    """
    config_path = Path(config_file)
    if not config_path.exists():
        print(f'Configfile {config_file} not found')
        sys.exit(1)

    config = yload(config_path.read_text(), Loader=BaseLoader)

    flickr = flickrapi.FlickrAPI(config['api_key'], config['api_secret'], format='parsed-json')

    return flickr


def run_cli() -> None:
    """
    Run the script from the CLI
    :return:
    """
    args = parse_cli_args()
    downloader = Downloader(init_flickr_client('./flickr.yml'))
    if args.suffix:
        downloader.set_preferred_size_suffix(args.suffix)

    if args.watermark_file:
        watermarker = Watermarker(args.watermark_file)
        downloader.set_post_download_callback(watermarker.mark_in_place)

    output_dir = args.output.rstrip('/')
    if not Path(output_dir).is_dir():
        print(f'Output dir {output_dir} did not exist, creating it')
        Path(output_dir).mkdir(parents=True)

    downloader.fetch_albums(args.album_id.split(','), output_dir, limit=args.limit, delete=args.delete_missing)
    print('All done')


if __name__ == '__main__':
    run_cli()
