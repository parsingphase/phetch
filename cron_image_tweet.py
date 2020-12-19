#!/usr/bin/env python
"""
Script to post an image a day from flickr to twitter

Hardcoded for specific requirements; extend for your own
"""
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Generator, List, Optional, TypedDict, cast

import flickrapi
import pendulum
import twitter
from dateutil.parser import parse

from phetch import init_flickr_client
from pictools import load_config

ScheduledId = TypedDict('ScheduledId', {'photo_id': str, 'date_str': str})
SimpleTweet = TypedDict('SimpleTweet', {'text': str, 'media': str})

# HASHTAG = '#dailybird'
HASHTAG = '#test'


class UniquenessError(Exception):
    """
    Custom error for issues in schedule setup
    """


def parse_cli_args() -> argparse.Namespace:
    """
    Specify and parse command-line arguments

    Returns:
        Namespace of provided arguments
    """
    parser = argparse.ArgumentParser(
        description='Create tweet with image from encoded input',
    )
    parser.add_argument('--source-flickr-download-dir', help='Directory of coded flickr downloads to use as source',
                        required=True)
    parser.add_argument('--dry-run', help="Prepare the tweet but don't send it", action='store_true')
    args = parser.parse_args()

    return args


def scan_path_for_coded_filenames(source_dir: Path) -> List[ScheduledId]:
    """
    Search a directory (provided as a Path) for files set up for posting
    :param source_dir:
    :return:
    """
    pattern = r"^(?P<date_str>\d{8})_.*_(?P<photo_id>\d{11,12})\.jpg$"
    candidates: Generator[Path, None, None] = source_dir.glob("*.jpg")
    schedule: List[ScheduledId] = []
    for candidate in candidates:
        match = re.match(pattern, candidate.name)
        if match:
            schedule.append(cast(ScheduledId, match.groupdict()))

    return schedule


def assert_schedule_unique(schedule: List[ScheduledId]):
    """
    Throw a schedule error if we have two posts on a day or try to post an image twice
    :param schedule:
    :return:
    """
    dates = [item['date_str'] for item in schedule]
    photos = [item['photo_id'] for item in schedule]
    if not len(set(dates)) == len(dates):
        raise UniquenessError('Dates are not unique: ' + ', '.join(dates))
    if not len(set(photos)) == len(photos):
        raise UniquenessError('Photo IDs are not unique')


def get_today_date_str() -> str:
    """
    Get today's date in a format matching our input schedule
    :return:
    """
    return datetime.today().strftime('%Y%m%d')


def get_due_item_from_schedule(schedule: List[ScheduledId]) -> Optional[ScheduledId]:
    """
    Find the item in the schedule that's due to post today
    :param schedule:
    :return:
    """
    today_string = get_today_date_str()
    today_items = [item for item in schedule if item['date_str'] == today_string]
    return today_items.pop()


def build_tweet_by_flickr_photo_id(photo_id: str) -> SimpleTweet:
    """
       - get k-size image URI -
         - https://www.flickr.com/services/api/flickr.photos.getSizes.html
         - UNSIGNED CALL!
       - get title, … : https://www.flickr.com/services/api/flickr.photos.getInfo.html
         - photo.title, photo.dates.taken

    :param photo_id:
    :return:
    """
    flickr = init_flickr_client('./config.yml')

    url = get_photo_url(flickr, photo_id)

    info = flickr.photos.getInfo(photo_id=photo_id)
    when = info['photo']['dates']['taken']
    title = info['photo']['title']['_content']
    when_date = parse(when)
    friendly_date = pendulum.instance(when_date).format('Mo MMMM Y')  # type: ignore

    text = f'{title}, {friendly_date} {HASHTAG}'

    return {
        'text': text,
        'media': url
    }


def get_photo_url(flickr: flickrapi.FlickrAPI, photo_id: str) -> str:
    """
    Get the source URL for an image ID from flickr, ideally the 'k' size
    :param flickr:
    :param photo_id:
    :return:
    """
    size_response = flickr.photos.getSizes(photo_id=photo_id)
    k_urls = [size['source'] for size in size_response['sizes']['size'] if size['label'] == 'Large 2048']
    o_urls = [size['source'] for size in size_response['sizes']['size'] if size['label'] == 'Original']
    url = k_urls[0] if len(k_urls) > 0 else o_urls[0]
    return url


def init_twitter_client(config_file: str) -> twitter.Api:
    """
    Initialize a twitter client from our config file
    :param config_file:
    :return:
    """
    config = load_config(config_file)['twitter']
    api = twitter.Api(consumer_key=config['api_key'],
                      consumer_secret=config['api_secret'],
                      access_token_key=config['access_token_key'],
                      access_token_secret=config['access_token_secret'])

    return api


def run_cli() -> None:
    """
    Run the script at the command line
    :return:
    """
    args = parse_cli_args()
    source_dir = Path(args.source_flickr_download_dir)
    if not source_dir.exists():
        raise FileExistsError(Path.name + 'missing')

    schedule = scan_path_for_coded_filenames(source_dir)

    assert_schedule_unique(schedule)
    due_photo = get_due_item_from_schedule(schedule)

    if due_photo:
        tweet: SimpleTweet = build_tweet_by_flickr_photo_id(due_photo['photo_id'])
        twitter_api = init_twitter_client('./config.yml')
        if args.dry_run:
            print('Dry run: generated ', tweet)
        else:
            status = twitter_api.PostUpdate(status=tweet['text'], media=tweet['media'])
            if status:
                print(f"Posted successfully at {status.created_at_in_seconds}")
                print(status)
            else:
                print("Possible post failure?")
                print(status)
                sys.exit(1)
    else:
        print("No tweet due today")


if __name__ == '__main__':
    run_cli()
