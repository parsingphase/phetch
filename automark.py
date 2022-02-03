#!/usr/bin/env python
"""
Watermark images in a directory. Run with --help for details
"""

import argparse
from pathlib import Path

from image_processors import Watermarker
from phetch_tools import load_config


def parse_cli_args() -> argparse.Namespace:
    """
    Specify and parse command-line arguments

    Returns:
        Namespace of provided arguments
    """
    parser = argparse.ArgumentParser(
        description='Watermark images in a directory, saved to a /watermarks subdirectory',
    )
    parser.add_argument('dir', help='Directory containing files to watermark')
    parser.add_argument('--limit', required=False, help='Max images to process', type=int, default=0)
    parser.add_argument('--resize', required=False, help='Resize to fit box', type=int, dest='max_edge')
    args = parser.parse_args()
    return args


def run_cli() -> None:
    """
    Run the script from the CLI
    :return:
    """
    args = parse_cli_args()
    script_dir = Path(__file__).parent
    config = load_config(str(script_dir / Path('config.yml')))
    watermark = Path(config['watermark']['file'])
    if not watermark.is_absolute():
        watermark = script_dir / watermark
    watermarker = Watermarker(str(watermark))
    if 'opacity' in config['watermark']:
        watermarker.set_watermark_opacity(config['watermark']['opacity'])

    source_dir = Path(args.dir.rstrip('/'))
    output_dir = source_dir / ('watermarked' + ('-' + str(args.max_edge) if args.max_edge else ''))
    if not output_dir.is_dir():
        print(f'Output dir {output_dir} did not exist, creating it')
        output_dir.mkdir(parents=True)

    source_files = list(source_dir.glob('*.jpg')) + list(source_dir.glob('*.jpeg'))
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
