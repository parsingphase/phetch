#!/usr/bin/env python

from phetch_tools.social import (ScheduledId,
                                 scan_file_for_coded_filenames)
from typing import Any, Dict, Generator, List, Optional, cast
from pathlib import Path
from phetch_tools.init_flickr import (init_flickr_client, flickr_get_token)
import flickrapi
from csv import reader


def run_cli():
    files_2021: List[ScheduledId] = scan_file_for_coded_filenames(Path('potd_schedules.lnk/2021.txt'))
    photos_2021 = [file['photo_id'] for file in files_2021]

    files_2022: List[ScheduledId] = scan_file_for_coded_filenames(Path('potd_schedules.lnk/2022.txt'))
    photos_2022 = [file['photo_id'] for file in files_2022]

    # source_file = Path('potd_schedules.lnk/2023.csv')
    # contents = source_file.read_text('UTF-8').strip().split('\n')
    photos_2023 = []
    # for row in contents[1:]:
    #     cells = row.split(',')
    #     print(cells[0], cells[7])
    #     if cells[7] != '':
    #         photos_2023.append(cells[0])

    with open('potd_schedules.lnk/2023.csv', 'r') as read_obj:
        # pass the file object to reader() to get the reader object
        csv_reader = reader(read_obj)
        for i, cells in enumerate(csv_reader):
            # row variable is a list that represents a row in csv
            if i > 0:
                include = (cells[7] != '')
                # print(cells[0], cells[7], include)
                if include:
                    photos_2023.append(cells[0])

    # print(photos_2021,photos_2022,photos_2023)
    # print(len(photos_2023))

    # return

    flickr: flickrapi.FlickrAPI = init_flickr_client('./config.yml')

    # oauth needed: https://www.flickr.com/services/api/auth.oauth.html / https://stuvel.eu/flickrapi-doc/3-auth.html
    if flickr.token_valid(perms='write'):
        print('Auth valid')
    else:
        flickr_get_token(flickr, 'write')  # type: ignore

    tag_files(flickr, 'DailyBird2021','BOTD2021', photos_2021)
    tag_files(flickr, 'DailyBird2022','BOTD2022', photos_2022)
    tag_files(flickr, 'DailyBird2023','BOTD2023', photos_2023)


def tag_files(flickr: flickrapi.FlickrAPI, tag: str, remove_tag: str, photo_ids: List[str]):
    for photo_id in photo_ids:
        print(tag, photo_id)
        tries = 3
        while tries > 0:
            try:
                flickr.photos.addTags(photo_id=photo_id, tags=tag)
                flickr.photos.removeTag(photo_id=photo_id, tags=remove_tag)
                break
            except Exception:
                tries -= 1
                print(f' {photo_id}: retry')


if __name__ == '__main__':
    run_cli()
