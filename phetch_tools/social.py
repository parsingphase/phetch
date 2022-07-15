import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, cast

import flickrapi
import pendulum
import twitter
from dateutil.parser import parse
from typing_extensions import TypedDict

from .init_flickr import init_flickr_client
from .load_config import load_config

ScheduledId = TypedDict('ScheduledId', {'photo_id': str, 'date_str': str})
SimpleTweet = TypedDict('SimpleTweet', {'text': str, 'media': str})


class UniquenessError(Exception):
    """
    Custom error for issues in schedule setup
    """


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


def scan_file_for_coded_filenames(source_file: Path) -> List[ScheduledId]:
    """
    Parse a text file (provided as a Path) for candidates for posting
    :param source_file:
    :return:
    """
    pattern = r"^(?P<date_str>\d{8})_.*_(?P<photo_id>\d{11,12})(\.jpg)?$"
    contents = source_file.read_text('UTF-8').strip()
    candidates = contents.split("\n")
    schedule: List[ScheduledId] = []
    for candidate in candidates:
        match = re.match(pattern, candidate.strip())
        if match:
            matches = match.groupdict()
            schedule.append(cast(ScheduledId, matches))

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


def get_due_item_from_schedule(schedule: List[ScheduledId], for_date: str = None) -> Optional[ScheduledId]:
    """
    Find the item in the schedule that's due to post today
    :param schedule:
    :param for_date:
    :return:
    """
    today_string = for_date if for_date else get_today_date_str()
    today_items = [item for item in schedule if item['date_str'] == today_string]
    return today_items.pop() if len(today_items) > 0 else None


def build_tweet_by_flickr_photo_id(photo_id: str, hashtag: str = '') -> SimpleTweet:
    """
       - get k-size image URI -
         - https://www.flickr.com/services/api/flickr.photos.getSizes.html
         - UNSIGNED CALL!
       - get title, … : https://www.flickr.com/services/api/flickr.photos.getInfo.html
         - photo.title, photo.dates.taken

    :param hashtag:
    :param photo_id:
    :return:
    """
    flickr = init_flickr_client('./config.yml')

    url = get_photo_url(flickr, photo_id)

    info = flickr.photos.getInfo(photo_id=photo_id)
    when = info['photo']['dates']['taken']
    title = read_content(info['photo']['title'])
    when_date = parse(when)
    friendly_date = pendulum.instance(when_date).format('Do MMMM Y')  # type: ignore

    locale = get_photo_location_parts(flickr, photo_id)

    tagged_place = get_tagged_place(info)
    if tagged_place:
        locale[0] = tagged_place

    locale_string = join_locale(locale)
    if len(locale_string) > 0:
        locale_string = '\n' + locale_string

    native_territory = get_tagged_lands(info)
    if native_territory and (len(native_territory) > 0):
        locale_string = locale_string + f'\n{native_territory} traditional territory'

    properties_string = get_photo_properties_string(flickr, photo_id)
    if len(properties_string) > 0:
        properties_string = '\n' + properties_string

    text = f'{title}, {friendly_date}{locale_string}{properties_string}'

    if len(text) + len(hashtag) < 280:
        text = text + f'\n{hashtag}'

    print(f'Text length: {len(text)}')

    return {
        'text': text,
        'media': url
    }


def get_tagged_place(info) -> Optional[str]:
    """
    Find a geo:place tag from image's flickr info

    Args:
        info:

    Returns:

    """
    return get_machine_tag(info, 'geo:place')


def get_tagged_lands(info) -> Optional[str]:
    """
    Find a geo:place tag from image's flickr info

    Args:
        info:

    Returns:

    """
    return get_machine_tag(info, 'geo:native_territory')


def get_machine_tag(info, tag_label):
    tags = info['photo']['tags']['tag']
    matched_tag = [t['raw'] for t in tags if t['raw'].startswith(f'{tag_label}=')]
    tag_value = matched_tag[0].replace(f'{tag_label}=', '') if len(matched_tag) > 0 else None
    return tag_value


def first(values) -> Any:
    """
    Return first element of an array or none
    :param values:
    :return:
    """
    return values[0] if len(values) > 0 else None


def get_photo_properties_string(flickr, photo_id) -> str:
    """
    Get a location string for the given photo from the Flickr API
    :param flickr:
    :param photo_id:
    :return:
    """
    properties_string = ''
    try:
        exif_data = flickr.photos.getExif(photo_id=photo_id)
        properties = exif_data['photo']['exif']
        # print(properties)
        model = first([read_content(p['raw']) for p in properties if p['tag'] == 'Model'])
        exposure = first([read_content(p['raw']) for p in properties if p['tag'] == 'ExposureTime'])
        aperture = first([read_content(p['clean']) for p in properties if p['tag'] == 'FNumber'])
        iso = first([read_content(p['raw']) for p in properties if p['tag'] == 'ISO'])
        focal = first([read_content(p['clean']) for p in properties if p['tag'] == 'FocalLength'])
        # raw: {'model': 'Canon EOS 90D', 'exposure': '1/1600', 'aperture': 'f/7.1', 'iso': '250', 'focal': '600 mm'}
        if exposure:
            exposure = exposure + 's'
        if focal:
            focal = focal.replace(' ', '')
        if iso:
            iso = 'ISO ' + iso
        # print({'model': model, 'exposure': exposure, 'aperture': aperture, 'iso': iso, 'focal': focal})
        properties_string = ', '.join([p for p in [model, focal, exposure, aperture, iso] if p])
        # print(properties_string)
    except flickrapi.exceptions.FlickrError:
        pass
    return properties_string


def get_photo_location_string(flickr, photo_id) -> str:
    """
    Get a location string for the given photo from the Flickr API
    :param flickr:
    :param photo_id:
    :return:
    """
    locale = get_photo_location_parts(flickr, photo_id)
    return join_locale(locale)


def join_locale(locale: List[str]) -> str:
    """
    Join non-empty parts of list with commas
    Args:
        locale:

    Returns:

    """
    locale = [k for k in locale if k]
    locale_string = ', '.join(locale)
    return locale_string


def get_photo_location_parts(flickr, photo_id) -> List[str]:
    """
    Get a List containing whatever location data is available for an image via the flickr API
    Args:
        flickr:
        photo_id:

    Returns:

    """
    locale = []
    try:
        gps_data = flickr.photos.geo.getLocation(photo_id=photo_id)
        location = gps_data['photo']['location']
        neighbourhood = read_content(location['neighbourhood'])
        locality = read_content(location['locality'])
        state = read_content(location['region'])
        country = read_content(location['country'])
        if country in ('United States', 'USA'):
            country = ''  # State (region) is adequate here
        locale = [neighbourhood, locality, state, country]
    except flickrapi.exceptions.FlickrError:
        pass
    return locale


def read_content(element: Optional[Dict[str, str]]) -> str:
    """Return a subfield of _content if present, else '' """
    return element['_content'] if element and element['_content'] else ''


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
