#!/usr/bin/env python
import re
from os.path import exists
from pathlib import Path

import requests
from mastodon import Mastodon

from cron_image_tweet import (SimpleTweet, build_tweet_by_flickr_photo_id,
                              get_due_item_from_schedule,
                              scan_file_for_coded_filenames)
from phetch_tools import load_config

DEFAULT_HASHTAG = '#DailyBird'

def init_mastodon_client(config_file):
    mastodon_config = load_config(config_file)['mastodon']

    mastodon = Mastodon(
        client_id=mastodon_config['client_id'],
        client_secret=mastodon_config['client_secret'],
        api_base_url=mastodon_config['api_base_url']
    )

    mastodon.log_in(
        mastodon_config['user_email'],
        mastodon_config['user_password'],
        to_file='tmp/pytooter_usercred.secret',
        scopes=['write']
    )

    print('Mastodon version: ' + mastodon.retrieve_mastodon_version() + ' on ' + mastodon.api_base_url)

    return mastodon


def main():
    source_file = 'data/2022.txt'
    schedule = scan_file_for_coded_filenames(Path(source_file))
    due_photo = get_due_item_from_schedule(schedule)

    if not due_photo:
        print('No tweet scheduled')
        exit(1)

    tweet: SimpleTweet = build_tweet_by_flickr_photo_id(due_photo['photo_id'], DEFAULT_HASHTAG)
    # print(tweet)

    mastodon = init_mastodon_client('./config.yml')
    #
    # image = 'data/dove.jpg'
    # image = 'https://live.staticflickr.com/65535/52030791295_e46c7f9dbe_k_d.jpg'
    # text = '#dailybird client development test'
    post_image_status(mastodon, tweet['media'], tweet['text'])

    # url = 'https://live.staticflickr.com/65535/52030402433_1c98d509c0_k_d.jpg'
    # response = requests.get(url, allow_redirects=True)
    # print(response.headers)
    # content_type = response.headers['Content-Type']
    # file_content = response.content


def post_image_status(mastodon, image, text):
    if re.match('^http(s?):', image):
        response = requests.get(image, allow_redirects=True)
        # print(response.headers)
        content_type = response.headers['Content-Type']
        file_content = response.content
        media = mastodon.media_post(file_content, mime_type=content_type)
    elif exists(image):
        media = mastodon.media_post(image)
    else:
        raise f'File or URL {image} not found'

    # print(media)
    # {'id': 108206266800599344, 'type': 'image', 'url': 'https://files.mastodon.social/media_attachments/files/108/206/266/800/599/344/original/4b19b949463832ea.jpg', 'preview_url': 'https://files.mastodon.social/media_attachments/files/108/206/266/800/599/344/small/4b19b949463832ea.jpg', 'remote_url': None, 'preview_remote_url': None, 'text_url': None, 'meta': {'original': {'width': 1763, 'height': 1176, 'size': '1763x1176', 'aspect': 1.4991496598639455}, 'small': {'width': 490, 'height': 327, 'size': '490x327', 'aspect': 1.4984709480122325}}, 'description': None, 'blurhash': 'USKK4u~W-pxa4ot7t7RkMyIoNHxuRPM{smNH'}
    mastodon.status_post(text, media_ids=[media['id']])


if __name__ == '__main__':
    main()
