import argparse
from pathlib import Path
from time import sleep

import flickrapi
import requests
from yaml import BaseLoader
from yaml import load as yload
from pathvalidate import sanitize_filename


# album_id = '72157714145527936' # birds
# album_id = '72157714807457311'  # wildlife
# output_dir = './download'


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
    config_path = Path(config_file)
    if not config_path.exists():
        print(f'Configfile {config_file} not found')
        exit(1)

    configData = config_path.read_text()
    config = yload(configData, Loader=BaseLoader)
    # print(config)

    flickr = flickrapi.FlickrAPI(config['api_key'], config['api_secret'], format='parsed-json')

    return flickr


class Downloader:

    def __init__(self, flickr_client):
        self.flickr = flickr_client

    def fetch_albums(self, albums, output):
        for album in albums:
            self.fetch_album(album, output)

    def fetch_album(self, album_id, output_dir):
        album_response = self.flickr.photosets.getInfo(photoset_id=album_id)
        album_title = album_response['photoset']['title']['_content']
        print(f'Fetching album {album_title} ({album_id})')

        page = 1
        photoset_response = self.fetch_album_page(album_id, page)
        # print(photoset_response)
        # exit(1)
        pages = int(photoset_response['photoset']['pages'])

        i = 1

        while page <= pages:
            photos = photoset_response['photoset']['photo']
            for photo in photos:
                sizes = self.flickr.photos.getSizes(photo_id=photo['id'])
                # print(sizes)
                exit(1)
                outfile = self.local_filename_for_photo(photo, output_dir)
                if not Path(outfile).exists():
                    print(f'Downloading: {i}: ', end='')
                    self.fetch_image(photo["url_o"], outfile)
                    sleep(2)
                    i += 1

            page += 1
            if page <= pages:
                print(f' Fetch page {page}/{pages}')
                photoset_response = self.fetch_album_page(album_id, page)

        print(" Album done")

    def local_filename_for_photo(self, photo, output_dir):
        photo_title = photo['title']
        photo_slug = self.make_title_slug(photo_title)
        outfile = f'{output_dir}/{photo_slug}{photo["id"]}.jpg'
        return outfile

    @staticmethod
    def make_title_slug(photo_title):
        photo_slug = sanitize_filename(photo_title) + '_' if photo_title else ''
        return photo_slug.lower().replace(' ','_')

    @staticmethod
    def fetch_image(url, outfile):
        r = requests.get(url)
        open(outfile, 'wb').write(r.content)
        print(f'{url} => {outfile}')

    def fetch_album_page(self, album_id, page=1, verbose=False):
        if verbose:
            print(f'Fetching {album_id}, page {page}')
        photoset_response = self.flickr.photosets.getPhotos(photoset_id=album_id, extras="url_k,url_o", page=page)
        print(photoset_response)
        return photoset_response


def run_cli():
    args = parse_cli_args()
    downloader = Downloader(init_flickr_client('./flickr.yml'))
    downloader.fetch_albums(args.album_id.split(','), args.output)
    print('All done')


# config eg: {'api_key': 'MYKEY', 'api_secret': 'MYSECRET'}

# test = flickr.test.echo(foo="bar")

# photos = flickr.photos.search(user_id='73509078@N00', per_page='10')

# print(photos)

run_cli()
