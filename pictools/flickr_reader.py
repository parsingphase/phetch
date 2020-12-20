"""
Class file for FlickrReader
"""
from typing import Any, List, Optional

from pathvalidate import sanitize_filename

from pictools.types import Photo


# Sample Photo response:
# {'id': '50653354368', 'secret': '61b20f2e69', 'server': '65535', 'farm': 66, 'title': 'Red-eared slider',
#  'isprimary': '0', 'ispublic': 1, 'isfriend': 0, 'isfamily': 0, 'datetaken': '2020-11-27 12:39:13',
#  'datetakengranularity': '0', 'datetakenunknown': '0',
#  'url_o': 'https://live.staticflickr.com/65535/50653354368_f94bcc957f_o.jpg', 'height_o': 4640, 'width_o': 6960,
#  'url_k': 'https://live.staticflickr.com/65535/50653354368_6b9562a359_k.jpg', 'height_k': 1365, 'width_k': 2048}


class FlickrReader:
    """
    Flickr album downloader
    """
    preferred_size: Optional[str]

    def __init__(self, flickr_client: Any) -> None:
        self.preferred_size = None
        self.flickr = flickr_client
        self.silent = False

    def set_silent(self, silent):
        """
        Mute informational output
        :param silent:
        :return:
        """
        self.silent = silent

    def set_preferred_size_suffix(self, suffix: str) -> 'FlickrReader':
        """
        Set the preferred size suffix; valid values are listed at https://www.flickr.com/services/api/misc.urls.html
        :param suffix:
        :return:
        """
        self.preferred_size = suffix
        return self

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

    def fetch_photoset_photos(self, album_id: str, page: int = 1):
        """
        Fetch info about photos in a given photoset
        :param limit:
        :param album_id:
        :param page:
        :param verbose:
        :return:
        """
        if not self.silent:
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
        if not self.silent:
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
                if not self.silent:
                    print(f' Fetch page {page}/{pages}')
                photoset_response = self.fetch_photoset_photos(album, page)

        return photos
