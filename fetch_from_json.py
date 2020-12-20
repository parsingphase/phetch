#!/usr/bin/env python
"""
Fetch list of images according to remote JSON file
"""

import argparse
import json
import re
from pathlib import Path

import requests

from phetch_tools import PhotoListFetcher


def parse_cli_args() -> argparse.Namespace:
    """
    Specify and parse command-line arguments

    Returns:
        Namespace of provided arguments
    """
    parser = argparse.ArgumentParser(
        description='Download list of images specified in a JSON file',
    )
    parser.add_argument('json', help='Path or URI of JSON file')
    parser.add_argument('output', help='Directory to save files to')
    parser.add_argument('--limit', required=False, help='Max images to download', type=int, default=0)
    args = parser.parse_args()
    return args


def run_cli() -> None:
    """
    Execute CLI app
    :return:
    """
    args = parse_cli_args()
    if re.match(r"^http(s?)://", args.json):
        # Assume URL
        content = requests.get(args.json).content
        photos = json.loads(content)
    else:
        # Assume file
        with open(args.json) as content_fp:
            photos = json.load(content_fp)

    downloader = PhotoListFetcher()
    Path(args.output).mkdir(exist_ok=True, parents=True)
    if args.limit:
        photos = photos[:args.limit]
    downloader.fetch_photos(photos, args.output)


if __name__ == '__main__':
    run_cli()
