import flickrapi

from .load_config import load_config


def init_flickr_client(config_file: str) -> flickrapi.FlickrAPI:
    """
    Initialise and return flickr client library using specified config file
    :param config_file:
    :return:
    """
    config = load_config(config_file)['flickr']

    flickr = flickrapi.FlickrAPI(config['api_key'], config['api_secret'], format='parsed-json')

    return flickr
