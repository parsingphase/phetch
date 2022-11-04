#!/usr/bin/env python
"""
Script to post an image a day from flickr to twitter

Hardcoded for specific requirements; extend for your own
"""
import argparse
import re
import sys
from os import getenv
from pathlib import Path
from typing import Any, List

from mastodon_post import post_toot_from_schedule
from phetch_tools.social import (ScheduledId, SimpleTweet,
                                 assert_schedule_unique,
                                 build_tweet_by_flickr_photo_id,
                                 get_due_item_from_schedule,
                                 init_twitter_client,
                                 scan_file_for_coded_filenames,
                                 scan_path_for_coded_filenames)

DEFAULT_HASHTAG = '#DailyBird #BirdPhotography'
DEFAULT_SERVICE = 'twitter'


def parse_cli_args() -> argparse.Namespace:
    """
    Specify and parse command-line arguments

    Returns:
        Namespace of provided arguments
    """
    parser = argparse.ArgumentParser(
        description='Create tweet with image from encoded input',
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--source-flickr-download-dir', help='Directory of coded flickr downloads to use as source')
    group.add_argument('--source-flickr-file-list', help='File containing list of Flickr photo dates/ids')
    parser.add_argument('--dry-run', help="Prepare the tweet but don't send it", action='store_true')
    parser.add_argument('--for-date', help="Generate a tweet for a specific day (YYYYmmdd format)")
    args = parser.parse_args()

    if args.for_date and not re.match(r'^\d{8}$', args.for_date):
        raise Exception("Bad for-date format")

    return args


def run_cli() -> None:
    """
    Run the script at the command line
    :return:
    """
    args = parse_cli_args()
    dry_run = args.dry_run

    if args.source_flickr_download_dir:
        source_dir = Path(args.source_flickr_download_dir)
        if not source_dir.exists():
            raise FileExistsError(str(source_dir) + ' missing')

        schedule = scan_path_for_coded_filenames(source_dir)
    elif args.source_flickr_file_list:
        source_file = Path(args.source_flickr_file_list)
        if not source_file.exists():
            raise FileExistsError(str(source_file) + ' missing')
        schedule = scan_file_for_coded_filenames(source_file)
    else:
        raise NotImplementedError("--source mechanism selected hasn't been coded yet!")

    post_tweet_from_schedule(schedule, DEFAULT_HASHTAG, dry_run, args.for_date)


def post_tweet_from_schedule(
        schedule: List[ScheduledId], hashtag: str = '', dry_run: bool = False,
        for_date: str = None):
    """
    Check for a due tweet, build and post it

    :param hashtag:
    :param schedule:
    :param dry_run: If true, just report on what the tweet would contain
    :param for_date: Generate tweet for this date; default today
    :return:
    """
    assert_schedule_unique(schedule)
    due_photo = get_due_item_from_schedule(schedule, for_date)
    if due_photo:
        tweet: SimpleTweet = build_tweet_by_flickr_photo_id(due_photo['photo_id'], hashtag)
        twitter_api = init_twitter_client('./config.yml')
        if dry_run:
            print('Dry run: generated ', tweet)
        else:
            status = twitter_api.PostUpdate(status=tweet['text'], media=tweet['media'])
            if status:
                print(f"Posted successfully at {status.created_at_in_seconds}: ", tweet)
                print(status)
            else:
                print("Possible post failure?")
                print(status)
                sys.exit(1)
    else:
        print("No tweet due today")


# noinspection PyUnusedLocal
# pylint: disable=unused-argument
def lambda_handler(event: Any, context: Any):
    """
    Entrypoint for AWS lambda
    :param event:
    :param context:
    :return:
    """
    print('event', event)
    service = event['service'] if 'service' in event else DEFAULT_SERVICE

    source_file = getenv('POTD_SCHEDULE_FILE')
    dry_run = bool(getenv('POTD_DRY_RUN'))

    default_lambda_hashtag = getenv('POTD_HASHTAG', '')
    mastodon_hashtag = getenv('POTD_HASHTAG_MASTODON', None)
    twitter_hashtag = getenv('POTD_HASHTAG_TWITTER', None)
    if mastodon_hashtag is None:
        mastodon_hashtag = default_lambda_hashtag
    if twitter_hashtag is None:
        twitter_hashtag = default_lambda_hashtag

    if source_file is None:
        print('POTD_SCHEDULE_FILE environmental variable must be defined')
        sys.exit(1)
    schedule = scan_file_for_coded_filenames(Path(source_file))

    if service == 'mastodon':
        post_toot_from_schedule(schedule, mastodon_hashtag)
    elif service == 'twitter':
        post_tweet_from_schedule(schedule, twitter_hashtag, dry_run)
    else:
        raise Exception(f'Invalid service "{service}" specified')


if __name__ == '__main__':
    if (len(sys.argv) > 1) and sys.argv[1] == '--lambda':
        lambda_handler(None, None)
    else:
        run_cli()
