from os import getenv

import flickrapi

from .load_config import load_config


def init_flickr_client(config_file: str) -> flickrapi.FlickrAPI:
    """
    Initialise and return flickr client library using specified config file

    Will try to act appropriately in an AWS lambda context

    :param lambda_safe:
    :param config_file:
    :return:
    """
    lambda_safe = bool(getenv('AWS_EXECUTION_ENV', False))

    config = load_config(config_file)['flickr']

    flickr = flickrapi.FlickrAPI(config['api_key'], config['api_secret'], format='parsed-json',
                                 token_cache_location='/tmp/ftoken' if lambda_safe else None)

    return flickr
