#!/usr/bin/env python
"""
Fetch one or more Flickr albums. Run with --help for details
"""

import argparse
from pathlib import Path

from pictools import Watermarker, load_config


def parse_cli_args() -> argparse.Namespace:
    """
    Specify and parse command-line arguments

    Returns:
        Namespace of provided arguments
    """
    parser = argparse.ArgumentParser(
        description='Download Flickr album images to a directory for use in screensavers, etc',
    )
    parser.add_argument('dir', help='Directory containing files to watermark')
    parser.add_argument('--limit', required=False, help='Max images to download', type=int, default=0)
    parser.add_argument('--resize', required=False, help='Resize to fit box', type=int, dest='max_edge')
    args = parser.parse_args()
    return args


def run_cli() -> None:
    """
    Run the script from the CLI
    :return:
    """
    args = parse_cli_args()
    config = load_config('./config.yml')
    watermarker = Watermarker(config['watermark']['file'])
    if 'opacity' in config['watermark']:
        watermarker.set_watermark_opacity(config['watermark']['opacity'])

    source_dir = Path(args.dir.rstrip('/'))
    output_dir = source_dir / 'watermarked'
    if not output_dir.is_dir():
        print(f'Output dir {output_dir} did not exist, creating it')
        output_dir.mkdir(parents=True)

    source_files = list(source_dir.glob('*.jpg'))
    done = 0
    for image in source_files:
        output = output_dir / image.name
        if output.exists():
            pass
        else:
            print(f"Watermarking {image} => {output}")
            watermarker.copy_with_watermark(str(image), str(output), args.max_edge)
            done += 1
            if args.limit and (done >= args.limit):
                break

    print('All done')


if __name__ == '__main__':
    run_cli()
