"""
Class file for PhotoListFetcher
"""
import os
from pathlib import Path
from random import sample
from time import sleep
from typing import Callable, List, Optional

import piexif
import requests

from .types import Photo, PhotoKey


# Sample Photo response:
# {'id': '50653354368', 'secret': '61b20f2e69', 'server': '65535', 'farm': 66, 'title': 'Red-eared slider',
#  'isprimary': '0', 'ispublic': 1, 'isfriend': 0, 'isfamily': 0, 'datetaken': '2020-11-27 12:39:13',
#  'datetakengranularity': '0', 'datetakenunknown': '0',
#  'url_o': 'https://live.staticflickr.com/65535/50653354368_f94bcc957f_o.jpg', 'height_o': 4640, 'width_o': 6960,
#  'url_k': 'https://live.staticflickr.com/65535/50653354368_6b9562a359_k.jpg', 'height_k': 1365, 'width_k': 2048}


# Set of "sort" functions; these actually subsample the list of fetched photos in a defined way
def sort_natural(photos: List[Photo], limit: Optional[int] = None, reverse: bool = False) -> List[Photo]:
    """
    Don't actually sort, just use whatever order the Flickr API returned
    :param reverse:
    :param photos:
    :param limit:
    :return:
    """
    if reverse:
        photos = photos[::-1]
    return photos if limit is None else photos[:limit]


def sort_random(photos: List[Photo], limit: Optional[int] = None, reverse: bool = False) -> List[Photo]:
    """
    Get a random selection of photos from the list
    :param reverse:
    :param photos:
    :param limit:
    :return:
    """
    photos = sample(photos, limit if limit is not None else len(photos))
    if reverse:
        photos = photos[::-1]  # nonsensical with random, but if they ask…
    return photos


def sort_by_key(
        photos: List[Photo], key: PhotoKey, limit: Optional[int] = None, reverse: bool = False) -> List[Photo]:
    """
    Helper to sort photos by a given dict key
    :param photos:
    :param key:
    :param limit:
    :param reverse:
    :return:
    """
    photos = sorted(photos, key=lambda d: d[key], reverse=reverse)
    if limit is not None:
        photos = photos[:limit]
    return photos


def sort_title(photos: List[Photo], limit: Optional[int] = None, reverse: bool = False) -> List[Photo]:
    """
    Sort photos by title
    :param photos:
    :param limit:
    :param reverse:
    :return:
    """
    return sort_by_key(photos, key='title', limit=limit, reverse=reverse)


def sort_taken(photos: List[Photo], limit: Optional[int] = None, reverse: bool = False) -> List[Photo]:
    """
    Sort photos by date taken
    :param photos:
    :param limit:
    :param reverse:
    :return:
    """
    return sort_by_key(photos, key='taken', limit=limit, reverse=reverse)


class PhotoListFetcher:
    """
    Download from a list of Photo objects
    """
    sort_funcs = {
        'natural': sort_natural,
        'random': sort_random,
        'alphabetical': sort_title,
        'taken': sort_taken,
    }
    post_download_callback: Optional[Callable[[str, Photo], None]]

    def __init__(self) -> None:
        self.preferred_size = None
        self.post_download_callback = None

    def set_post_download_callback(self, callback: Optional[Callable[[str], None]]) -> 'PhotoListFetcher':
        """
        Set a callback to be used after each download
        :param callback:
        :return:
        """
        self.post_download_callback = callback
        return self

    def order_photo_list(self, photos: List[Photo], sort: str, reverse: bool, limit) -> List[Photo]:
        """
        Order a provided photo list according to the required algorithm and constraints
        :param photos:
        :param sort:
        :param reverse:
        :param limit:
        :return:
        """
        if sort not in self.sort_funcs:
            raise KeyError(f"No such sort function: {sort}")
        if limit == 0:
            limit = None
        selected_photos = self.sort_funcs[sort](photos, limit, reverse)
        return selected_photos

    def fetch_photos(self, photos: List[Photo], output_dir: str):
        """
        Fetch up to a maximum number of images from the calculated list
        :param photos:
        :param output_dir:
        :param limit:
        :return:
        """
        for photo in photos:
            outfile = output_dir + '/' + photo['local_file']
            if not Path(outfile).exists():
                self.download_image(photo, outfile, True)
                sleep(0.1)

    def download_image(self, photo: Photo, outfile: str, verbose: bool = False):
        """
        Fetch a single image from URL to local file
        :param verbose:
        :param url:
        :param outfile:
        :return:
        """
        suffix = Path(outfile).suffix.lower()
        if suffix not in ['.jpg', '.jpeg', '.gif', '.png']:
            raise ValueError(f"Non-JPG filename '{outfile}' ({suffix}) found, aborting as a precaution")
        url = photo['url']
        response = requests.get(url)
        content_type = response.headers['Content-Type'].split(';')[0]
        if content_type.split('/')[0].lower() != 'image':
            raise ValueError(f"Non-image type ({content_type}) declared by server, aborting as a precaution")
        open(outfile, 'wb').write(response.content)
        if verbose:
            print(f'{url} => {outfile}')
        title = photo['title']
        os.system(f'exiftool -overwrite_original -iptc:ObjectName="{title}" "{outfile}"')
        if self.post_download_callback:
            self.post_download_callback(outfile, photo)

    @staticmethod
    def remove_local_without_remote(photos: List[Photo], local_dir: str):
        """
        Remove any local file not present in a list of photos
        :param photos:
        :param local_dir:
        :return:
        """
        local_files = Path(local_dir).glob('*.jpg')  # assume only jpgs for now
        remote_filenames = [photo['local_file'] for photo in photos]
        to_remove = [file for file in local_files if file.name not in remote_filenames]
        for file in to_remove:
            print("Remove " + file.name + ", not found in photo list")
            file.unlink()

    @classmethod
    def get_sort_keys(cls) -> List[str]:
        """
        Report the available sort functions
        :return:
        """
        return list(cls.sort_funcs.keys())
