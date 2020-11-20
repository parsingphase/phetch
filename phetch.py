#!/usr/bin/env python
"""
Fetch one or more Flickr albums. Run with --help for details
"""

import argparse
import sys
from pathlib import Path
from time import sleep
from typing import Any, List, Optional

import flickrapi
import requests
from pathvalidate import sanitize_filename
from typing_extensions import TypedDict
from yaml import BaseLoader
from yaml import load as yload

Photo = TypedDict('Photo', {'url': str, 'local_file': str})


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
    parser.add_argument('--prefer-size-suffix', required=False, help='Preferred download size; see README.md')
    parser.add_argument('--limit', required=False, help='Max images to download', type=int, default=0)
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


class Downloader:
    """
    Flickr album downloader
    """
    preferred_size: Optional[str]

    def __init__(self, flickr_client: Any) -> None:
        self.preferred_size = None
        self.flickr = flickr_client

    def fetch_albums(self, albums: List[str], output: str, limit: int = 0) -> None:
        """
        Fetch albums from an array of IDs to a shared output directory
        :param limit:
        :param albums:
        :param output:
        :return:
        """
        photos = self.scan_albums(albums)
        self.fetch_photos(photos, output, limit)

    def scan_albums(self, albums: List[str]) -> List[Photo]:
        """
        Scan albums, given as a range of IDs, for potential dowloads
        :param limit:
        :param albums:
        :param output:
        :return:
        """
        photo_list = []  # List[Photo]

        for album in albums:
            photo_list += self.scan_album(album)

        return photo_list

    def fetch_photos(self, photos: List[Photo], output_dir: str, limit: int = 0):
        """
        Fetch up to a maximum number of images from the calculated list
        :param photos:
        :param output_dir:
        :param limit:
        :return:
        """
        if limit:
            photos = photos[:limit]
        for photo in photos:
            outfile = output_dir + '/' + photo['local_file']
            if not Path(outfile).exists():
                self.fetch_image(photo['url'], outfile, True)
                sleep(0.1)

    def local_filename_for_photo(self, photo, path: str = ""):
        """
        Create a local filename for a photo API object
        :param photo:
        :param path:
        :return:
        """
        photo_title = photo['title']
        photo_slug = self.make_title_slug(photo_title)
        outfile = f'{photo_slug}{photo["id"]}.jpg'
        if path:
            outfile = f'{path}/{outfile}'
        return outfile

    @staticmethod
    def make_title_slug(photo_title: str):
        """
        Convert title string to filename-safe slug
        :param photo_title:
        :return:
        """
        photo_slug = str(sanitize_filename(photo_title)) + '_' if photo_title else ''
        return photo_slug.lower().replace(' ', '_')

    @staticmethod
    def fetch_image(url: str, outfile: str, verbose: bool = False):
        """
        Fetch a single image from URL to local file
        :param verbose:
        :param url:
        :param outfile:
        :return:
        """
        response = requests.get(url)
        open(outfile, 'wb').write(response.content)
        if verbose:
            print(f'{url} => {outfile}')

    def fetch_photoset_photos(self, album_id: str, page: int = 1, verbose: bool = False):
        """
        Fetch info about photos in a given photoset
        :param limit:
        :param album_id:
        :param page:
        :param verbose:
        :return:
        """
        if verbose:
            print(f'Fetching {album_id}, page {page}')
        extras = "url_o" + (",url_" + self.preferred_size if self.preferred_size else "")
        photoset_response = self.flickr.photosets.getPhotos(
            photoset_id=album_id, extras=extras, page=page, media='photos'
        )
        return photoset_response

    def set_preferred_size_suffix(self, suffix: str) -> None:
        """
        Set the preferred size suffix; valid values are listed at https://www.flickr.com/services/api/misc.urls.html
        :param suffix:
        :return:
        """
        self.preferred_size = suffix

    def scan_album(self, album: str) -> List[Photo]:
        """
        Collect Photos data from an album
        :param album:
        :return:
        """
        photos = []  # List[Photo]
        album_response = self.flickr.photosets.getInfo(photoset_id=album)
        album_title = album_response['photoset']['title']['_content']
        print(f'Scanning album {album_title} ({album})')

        page = 1
        photoset_response = self.fetch_photoset_photos(album, page)
        pages = int(photoset_response['photoset']['pages'])

        while page <= pages:
            album_photos = photoset_response['photoset']['photo']
            for album_photo in album_photos:
                filename = self.local_filename_for_photo(album_photo)
                photo_url = album_photo["url_o"]
                if self.preferred_size and "url_" + self.preferred_size in album_photo:
                    photo_url = album_photo["url_" + self.preferred_size]

                photo: Photo = {'url': photo_url, 'local_file': filename}
                photos.append(photo)

            page += 1
            if page <= pages:
                print(f' Fetch page {page}/{pages}')
                photoset_response = self.fetch_photoset_photos(album, page)

        return photos


def run_cli() -> None:
    """
    Run the script from the CLI
    :return:
    """
    args = parse_cli_args()
    downloader = Downloader(init_flickr_client('./flickr.yml'))
    if args.prefer_size_suffix:
        downloader.set_preferred_size_suffix(args.prefer_size_suffix)

    output_dir = args.output.rstrip('/')
    if not Path(output_dir).is_dir():
        print(f'Output dir {output_dir} did not exist, creating it')
        Path(output_dir).mkdir(parents=True)

    downloader.fetch_albums(args.album_id.split(','), output_dir, limit=args.limit)
    print('All done')


if __name__ == '__main__':
    run_cli()
