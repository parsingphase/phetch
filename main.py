import flickrapi
from yaml import BaseLoader, load as yload
from pathlib import Path
import requests
from time import sleep
import argparse


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
    configPath = Path(config_file)
    if not configPath.exists():
        print(f'Configfile {config_file} not found')
        exit(1)

    configData = configPath.read_text()
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
        print(f'Fetching {album_id}')
        # album = self.flickr.photosets.getInfo(photoset_id=album_id)
        # print(album)

        photoset_response = self.flickr.photosets.getPhotos(photoset_id=album_id, extras="url_o")
        # urls = [photo['url_o'] for photo in photoset_response['photoset']['photo']]
        # print(urls)
        #
        # print (photoset_response)
        i = 1

        for photo in photoset_response['photoset']['photo']:
            outfile = f'{output_dir}/{photo["id"]}.jpg'
            if not Path(outfile).exists():
                print(f'Downloading: {i}: {photo["url_o"]}:')
                r = requests.get(photo["url_o"])
                open(outfile, 'wb').write(r.content)
                print(' Done')
                sleep(2)
                i += 1

        print("\nAll done")


def run_cli():
    args = parse_cli_args()
    downloader = Downloader(init_flickr_client('./flickr.yml'))
    downloader.fetch_albums(args.album_id.split(','), args.output)


# config eg: {'api_key': 'MYKEY', 'api_secret': 'MYSECRET'}

# test = flickr.test.echo(foo="bar")

# photos = flickr.photos.search(user_id='73509078@N00', per_page='10')

# print(photos)

run_cli()
