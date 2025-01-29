import flickrapi
import os
import webbrowser

from .load_config import load_config
from flickrapi.auth import FlickrAccessToken


def init_flickr_client(config_file: str) -> flickrapi.FlickrAPI:
    """
    Initialise and return flickr client library using specified config file

    :param config_file:
    :return:
    """

    config = load_config(config_file)['flickr']

    # flickr = flickrapi.FlickrAPI(config['api_key'], config['api_secret'], format='parsed-json',
    #                              token_cache_location='/tmp/ftoken')
    flickr = flickrapi.FlickrAPI(config['api_key'], config['api_secret'], 'parsingphase',
                                 # Can use the output of photoBird: flickrAuth/flickrWhoAmI.ts
                                 token=FlickrAccessToken('72157720831392195-82010ee0ef443803','436693addadf658b', 'read',
                                                        'Richard George', 'parsingphase','13932427@N00'),
                                 format='parsed-json',
                                 token_cache_location='./tmp/ftoken')

    return flickr


def flickr_get_token(flickr, perms='read'):
    """
    Get flickr token via browser, per https://stuvel.eu/flickrapi-doc/3-auth.html
    Args:
        flickr:
        perms:

    Returns:

    """
    if not flickr.token_valid(perms=perms):
        # Get a request token
        flickr.get_request_token(oauth_callback='oob')

        # Open a browser at the authentication URL. Do this however
        # you want, as long as the user visits that URL.
        authorize_url = flickr.auth_url(perms=perms)
        if os.environ['HOME'] == '/root':  # smells like docker
            print('Flickr auth required, please open: \n' + authorize_url)
        else:
            webbrowser.open_new_tab(authorize_url)

        # Get the verifier code from the user. Do this however you
        # want, as long as the user gives the application the code.
        verifier = str(input('Verifier code: '))

        # Trade the request token for an access token
        flickr.get_access_token(verifier)
