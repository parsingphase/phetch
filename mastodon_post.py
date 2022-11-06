#!/usr/bin/env python
"""
Script to post images to Mastodon
"""
import re
import sys
from os.path import exists
from pathlib import Path
from typing import List

import requests
from mastodon import Mastodon

from phetch_tools import load_config
from phetch_tools.social import (ScheduledId, SimpleTweet,
                                 build_tweet_by_flickr_photo_id,
                                 get_due_item_from_schedule,
                                 scan_file_for_coded_filenames)

DEFAULT_HASHTAG = '#DailyBird'


def init_mastodon_client(config_file) -> Mastodon:
    """
    Initialize client from provided config file

    Args:
        config_file:

    Returns:

    """
    mastodon_config = load_config(config_file)['mastodon']

    mastodon = Mastodon(
        client_id=mastodon_config['client_id'],
        client_secret=mastodon_config['client_secret'],
        api_base_url=mastodon_config['api_base_url']
    )

    mastodon.log_in(
        mastodon_config['user_email'],
        mastodon_config['user_password'],
        scopes=['write']
    )

    print('Mastodon version: ' + mastodon.retrieve_mastodon_version() + ' on ' + mastodon.api_base_url)

    return mastodon


def run_cli() -> None:
    """
    Run script as CLI
    Returns:

    """
    source_file = 'data/2022.txt'
    post_toot_from_schedule_file(source_file)


def post_toot_from_schedule_file(source_file) -> None:
    """
    Post toot from specified schedule file

    Args:
        source_file:

    Returns:

    """
    schedule = scan_file_for_coded_filenames(Path(source_file))
    post_toot_from_schedule(schedule)


def post_toot_from_schedule(schedule: List[ScheduledId], hashtag: str = '') -> None:
    """
    Check for a due toot, build and post it
    Compare post_tweet_from_schedule

    :param hashtag:
    :param schedule:
    :return:
    """
    due_photo = get_due_item_from_schedule(schedule)
    if not due_photo:
        print('No tweet scheduled')
        sys.exit(1)
    tweet: SimpleTweet = build_tweet_by_flickr_photo_id(due_photo['photo_id'], hashtag)
    mastodon = init_mastodon_client('./config.yml')
    post_image_status(mastodon, tweet['media'], tweet['text'], tweet['description'])
    print('Tooted', tweet)


def post_image_status(mastodon, image, text, description=None) -> None:
    """
    Post an image and text as a toot

    Args:
        description:
        mastodon:
        image:
        text:

    Returns:

    """
    if re.match('^http(s?):', image):
        response = requests.get(image, allow_redirects=True)
        content_type = response.headers['Content-Type']
        file_content = response.content
        media = mastodon.media_post(file_content, mime_type=content_type, description=description)
    elif exists(image):
        media = mastodon.media_post(image)
    else:
        raise Exception(f'File or URL {image} not found')
    mastodon.status_post(text, media_ids=[media['id']])


if __name__ == '__main__':
    run_cli()
