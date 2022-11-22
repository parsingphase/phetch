#!/usr/bin/env python
"""
Update machine place tags in a given Flickr album. Selection is hardcoded.
"""
import os
import webbrowser

from gps_tools import (ShapefileLocationFinder,
                       lng_lat_point_from_lat_lng,
                       list_to_punctuated_string,
                       load_custom_gpsvisualizer_polys_from_dir,
                       load_native_lands_polys_from_file,
                       make_openspace_tag, match_openspace_tag,
                       make_lands_tag, match_lands_tag)
from phetch_tools.init_flickr import init_flickr_client
from shapefile_list import shapefiles

SKIP_TO = None
# ALBUM_ID = 72177720295678754  # Massachusetts Wildlife 2022
# ALBUM_ID = 72157717912633238  # Wildlife Showcase 2021
# ALBUM_ID = 72177720295655372  # Massachusetts Birds 2022
ALBUM_ID = 72177720303859319  # Arizona 2022
POLYDIR = 'polyfiles'
NATIVE_LANDS_JSON_FILE = 'data/indigenousTerritories.json'
REPLACE_NATIVE_LANDS_TAG = True


def run_cli() -> None:
    """
    Run script as CLI
    Returns:

    """
    skip_until = SKIP_TO
    flickr = init_flickr_client('./config.yml')

    # oauth needed: https://www.flickr.com/services/api/auth.oauth.html / https://stuvel.eu/flickrapi-doc/3-auth.html
    if flickr.token_valid(perms='write'):
        print('Auth valid')
    else:
        flickr_get_token(flickr, 'write')  # type: ignore

    page = 0
    while True:
        page += 1
        print(f'Fetch page {page}')
        # noinspection PyBroadException
        try:
            album = flickr.photosets.getPhotos(photoset_id=ALBUM_ID, page=page)
            photos = album['photoset']['photo']
        except Exception:
            photos = []

        if len(photos) == 0:
            print('Ran out of photos')
            break

        # photo_ids = [p['id'] for p in photos]
        drawn_polygons = load_custom_gpsvisualizer_polys_from_dir(POLYDIR)
        lands_polygons = load_native_lands_polys_from_file(NATIVE_LANDS_JSON_FILE)

        for photo in photos:
            place = None
            photo_id = photo['id']
            if skip_until and (str(photo_id) != str(skip_until)):
                print('Skip', photo_id, SKIP_TO)
                continue

            skip_until = None

            title = photo['title']
            try:
                gps_data = flickr.photos.geo.getLocation(photo_id=photo_id)
            except Exception:
                print(photo_id, title, 'No GPS')
                continue

            lat_lon = (
                float(gps_data['photo']['location']['latitude']), float(gps_data['photo']['location']['longitude']))

            lng_lat_point = lng_lat_point_from_lat_lng(lat_lon)

            try:
                photo_details = flickr.photos.getInfo(photo_id=photo_id)
            except Exception:
                print(photo_id, title, 'Flickr b0rked')
                break

            tags = photo_details['photo']['tags']['tag']
            tags_raw = [t['raw'] for t in tags]

            openspace_tags = [t for t in tags_raw if match_openspace_tag(t)]
            if len(openspace_tags) > 0:
                print(photo_id, title, 'already tagged by place', openspace_tags)
            else:
                for named_poly in drawn_polygons:
                    if named_poly['polygon'].contains(lng_lat_point):
                        place = named_poly['name']
                        print(f'Found {photo_id} in {place} polyfile')
                        break

                if not place:
                    for shape in shapefiles:
                        finder = ShapefileLocationFinder(shape['filename'], shape['name_field'])
                        place = finder.place_from_lat_lng(lat_lon)
                        if place:
                            break

                print(f'{photo_id}, {title}, {place}')
                if place:
                    place_tag = make_openspace_tag(place)
                    flickr.photos.addTags(photo_id=photo_id, tags=place_tag)

            needs_lands_tag = True
            lands_tag_objects = [t for t in tags if match_lands_tag(t['raw'])]
            if len(lands_tag_objects) > 0:
                print(photo_id, title, 'already tagged by territory', lands_tag_objects)
                if REPLACE_NATIVE_LANDS_TAG:
                    for tag_to_remove in lands_tag_objects:
                        remove_id = tag_to_remove['id']
                        remove_text=tag_to_remove['raw']
                        print(f'Remove native tag {remove_id} / {remove_text}')
                        flickr.photos.removeTag(tag_id=remove_id)
                else:
                    needs_lands_tag = False

            if needs_lands_tag:
                territories = []
                for territory in lands_polygons:
                    name = territory['name']
                    if len(name) > 0 and territory['polygon'].contains(lng_lat_point):
                        # print(f'TN:{name}:')
                        territories.append(name)

                if len(territories) > 0:
                    territories.sort()
                    territories_string = list_to_punctuated_string(territories)
                    print(f'Found {photo_id} in {territories_string} territory')

                    lands_tag = make_lands_tag(territories_string)
                    flickr.photos.addTags(photo_id=photo_id, tags=lands_tag)
                    print(f'Add native tag {lands_tag}')


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


if __name__ == '__main__':
    run_cli()
