"""
Class file for Downloader
"""
from pathlib import Path
from random import sample
from time import sleep
from typing import Any, Callable, List, Optional

import requests
from pathvalidate import sanitize_filename
from typing_extensions import Literal, TypedDict

Photo = TypedDict('Photo', {'url': str, 'local_file': str, 'title': str, 'taken': str})
PhotoKey = Literal['url', 'local_file', 'title', 'taken']


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


class Downloader:
    """
    Flickr album downloader
    """
    sort_funcs = {
        'natural': sort_natural,
        'random': sort_random,
        'alphabetical': sort_title,
        'taken': sort_taken,
    }
    preferred_size: Optional[str]
    post_download_callback: Optional[Callable[[str], None]]

    def __init__(self, flickr_client: Any) -> None:
        self.preferred_size = None
        self.flickr = flickr_client
        self.post_download_callback = None

    def set_preferred_size_suffix(self, suffix: str) -> 'Downloader':
        """
        Set the preferred size suffix; valid values are listed at https://www.flickr.com/services/api/misc.urls.html
        :param suffix:
        :return:
        """
        self.preferred_size = suffix
        return self

    def set_post_download_callback(self, callback: Optional[Callable[[str], None]]) -> 'Downloader':
        """
        Set a callback to be used after each download
        :param callback:
        :return:
        """
        self.post_download_callback = callback
        return self

    # FIXME consider making some of these instance settings
    # pylint: disable=too-many-arguments
    def fetch_albums(
            self,
            albums: List[str],
            output: str,
            sort: str = 'natural',
            reverse: bool = False,
            limit: Optional[int] = None,
            delete: bool = False
    ) -> None:
        """
        Fetch albums from an array of IDs to a shared output directory
        :param reverse:
        :param sort:
        :param delete: Remove local files with no remote equivalent
        :param limit: Download at most this many new images
        :param albums:
        :param output:
        :return:
        """
        photos = self.scan_albums(albums)
        if limit == 0:
            limit = None
        selected_photos = self.sort_funcs[sort](photos, limit, reverse)
        self.fetch_photos(selected_photos, output)
        if delete:
            self.remove_local_without_remote(photos, local_dir=output)

    def scan_albums(self, albums: List[str]) -> List[Photo]:
        """
        Scan albums, given as a range of IDs, for potential dowloads
        :param limit:
        :param albums:
        :param output:
        :return:
        """
        photo_list = []  # List[Photo]

        for album in albums:
            photo_list += self.scan_album(album)

        return photo_list

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
                self.download_image(photo['url'], outfile, True)
                sleep(0.1)

    def local_filename_for_photo(self, photo, path: str = ""):
        """
        Create a local filename for a photo API object
        :param photo:
        :param path:
        :return:
        """
        photo_title = photo['title']
        photo_slug = self.make_title_slug(photo_title)
        outfile = f'{photo_slug}{photo["id"]}.jpg'
        if path:
            outfile = f'{path}/{outfile}'
        return outfile

    @staticmethod
    def make_title_slug(photo_title: str):
        """
        Convert title string to filename-safe slug
        :param photo_title:
        :return:
        """
        photo_slug = str(sanitize_filename(photo_title)) + '_' if photo_title else ''
        return photo_slug.lower().replace(' ', '_')

    def download_image(self, url: str, outfile: str, verbose: bool = False):
        """
        Fetch a single image from URL to local file
        :param verbose:
        :param url:
        :param outfile:
        :return:
        """
        response = requests.get(url)
        open(outfile, 'wb').write(response.content)
        if verbose:
            print(f'{url} => {outfile}')
        if self.post_download_callback:
            self.post_download_callback(outfile)

    def fetch_photoset_photos(self, album_id: str, page: int = 1, verbose: bool = False):
        """
        Fetch info about photos in a given photoset
        :param limit:
        :param album_id:
        :param page:
        :param verbose:
        :return:
        """
        if verbose:
            print(f'Fetching {album_id}, page {page}')
        extras = "date_taken,url_o" + (",url_" + self.preferred_size if self.preferred_size else "")
        photoset_response = self.flickr.photosets.getPhotos(
            photoset_id=album_id, extras=extras, page=page, media='photos'
        )
        return photoset_response

    def scan_album(self, album: str) -> List[Photo]:
        """
        Collect Photos data from an album
        :param album:
        :return:
        """
        photos = []  # List[Photo]
        album_response = self.flickr.photosets.getInfo(photoset_id=album)
        album_title = album_response['photoset']['title']['_content']
        print(f'Scanning album {album_title} ({album})')

        page = 1
        photoset_response = self.fetch_photoset_photos(album, page)
        pages = int(photoset_response['photoset']['pages'])

        while page <= pages:
            album_photos = photoset_response['photoset']['photo']
            for album_photo in album_photos:
                filename = self.local_filename_for_photo(album_photo)
                photo_url = album_photo["url_o"]
                if self.preferred_size and "url_" + self.preferred_size in album_photo:
                    photo_url = album_photo["url_" + self.preferred_size]

                photo: Photo = {
                    'url': photo_url,
                    'local_file': filename,
                    'title': album_photo['title'],
                    'taken': album_photo['datetaken']
                }
                photos.append(photo)

            page += 1
            if page <= pages:
                print(f' Fetch page {page}/{pages}')
                photoset_response = self.fetch_photoset_photos(album, page)

        return photos

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
