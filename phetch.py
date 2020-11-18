#!/usr/bin/env python
"""
Fetch one or more Flickr albums. Run with --help for details
"""

import argparse
import sys
from pathlib import Path
from time import sleep

import flickrapi
import requests
from pathvalidate import sanitize_filename
from yaml import BaseLoader
from yaml import load as yload


def parse_cli_args():
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
    args = parser.parse_args()
    return args


def init_flickr_client(config_file):
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

    def __init__(self, flickr_client):
        self.flickr = flickr_client

    def fetch_albums(self, albums, output):
        """
        Fetch albums from an array of IDs to a shared output directory
        :param albums:
        :param output:
        :return:
        """
        for album in albums:
            self.fetch_album(album, output)

    def fetch_album(self, album_id, output_dir):
        """
        Fetch single album to output directory
        :param album_id:
        :param output_dir:
        :return:
        """
        album_response = self.flickr.photosets.getInfo(photoset_id=album_id)
        album_title = album_response['photoset']['title']['_content']
        print(f'Fetching album {album_title} ({album_id})')

        page = 1
        photoset_response = self.fetch_photoset_photos(album_id, page)
        pages = int(photoset_response['photoset']['pages'])

        i = 1

        while page <= pages:
            photos = photoset_response['photoset']['photo']
            for photo in photos:
                outfile = self.local_filename_for_photo(photo, output_dir)
                if not Path(outfile).exists():
                    print(f'Downloading: {i}: ', end='')
                    self.fetch_image(photo["url_o"], outfile)
                    sleep(2)
                    i += 1

            page += 1
            if page <= pages:
                print(f' Fetch page {page}/{pages}')
                photoset_response = self.fetch_photoset_photos(album_id, page)

        print(" Album done")

    def local_filename_for_photo(self, photo, output_dir):
        """
        Create a local filename for a photo API object
        :param photo:
        :param output_dir:
        :return:
        """
        photo_title = photo['title']
        photo_slug = self.make_title_slug(photo_title)
        outfile = f'{output_dir}/{photo_slug}{photo["id"]}.jpg'
        return outfile

    @staticmethod
    def make_title_slug(photo_title):
        """
        Convert title string to filename-safe slug
        :param photo_title:
        :return:
        """
        photo_slug = sanitize_filename(photo_title) + '_' if photo_title else ''
        return photo_slug.lower().replace(' ', '_')

    @staticmethod
    def fetch_image(url, outfile, verbose=False):
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

    def fetch_photoset_photos(self, album_id, page=1, verbose=False):
        """
        Fetch info about photos in a given photoset
        :param album_id:
        :param page:
        :param verbose:
        :return:
        """
        if verbose:
            print(f'Fetching {album_id}, page {page}')
        photoset_response = self.flickr.photosets.getPhotos(photoset_id=album_id, extras="url_k,url_o", page=page)
        print(photoset_response)
        return photoset_response


def run_cli():
    """
    Run the script from the CLI
    :return:
    """
    args = parse_cli_args()
    downloader = Downloader(init_flickr_client('./flickr.yml'))
    downloader.fetch_albums(args.album_id.split(','), args.output)
    print('All done')


if __name__ == '__main__':
    run_cli()
