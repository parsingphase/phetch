#!/usr/bin/env python
"""
Fetch one or more Flickr albums. Run with --help for details
"""

import argparse
import sys
from pathlib import Path

import flickrapi

from pictools import Downloader, Watermarker, load_config


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
    parser.add_argument('--watermark-opacity', required=False, help='Set watermark opacity, 0-1', type=float)
    parser.add_argument('--limit', required=False, help='Max images to download', type=int, default=0)
    parser.add_argument('--delete-missing', help='Delete images not found in album', action="store_true")
    parser.add_argument('--sort-order', help='One of ', choices=Downloader.get_sort_keys(), default='natural')
    parser.add_argument('--sort-reverse', help='Reverse sort order', action='store_true')
    args = parser.parse_args()
    if args.watermark_opacity and not args.watermark_file:
        print('--watermark-opacity is invalid without --apply-watermark')
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
    downloader = Downloader(init_flickr_client('./config.yml'))
    if args.suffix:
        downloader.set_preferred_size_suffix(args.suffix)

    if args.watermark_file:
        watermarker = Watermarker(args.watermark_file)
        if args.watermark_opacity:
            watermarker.set_watermark_opacity(args.watermark_opacity)
        downloader.set_post_download_callback(watermarker.mark_in_place)

    output_dir = args.output.rstrip('/')
    if not Path(output_dir).is_dir():
        print(f'Output dir {output_dir} did not exist, creating it')
        Path(output_dir).mkdir(parents=True)

    downloader.fetch_albums(
        args.album_id.split(','),
        output_dir,
        limit=args.limit,
        sort=args.sort_order,
        reverse=args.sort_reverse,
        delete=args.delete_missing
    )
    print('All done')


if __name__ == '__main__':
    run_cli()
