#!/usr/bin/env python

import os
import webbrowser

from gps_tools import (EPSG_DATUM, ShapefileLocationFinder,
                       lng_lat_point_from_lat_lng,
                       load_custom_gpsvisualizer_polys_from_dir,
                       make_openspace_tag, match_openspace_tag)
from phetch_tools.init_flickr import init_flickr_client

SHAPEFILE = 'data/openspace/OPENSPACE_POLY'
SKIP_TO = None
# ALBUM_ID = 72177720295678754  # Massachusetts Wildlife 2022
# ALBUM_ID = 72157717912633238  # Wildlife Showcase 2021
ALBUM_ID = 72177720295655372  # Massachusetts Birds 2022
POLYDIR = 'polyfiles'


def run_cli() -> None:
    skip_until = SKIP_TO
    flickr = init_flickr_client('./config.yml')

    # oauth needed: https://www.flickr.com/services/api/auth.oauth.html / https://stuvel.eu/flickrapi-doc/3-auth.html
    if flickr.token_valid(perms='write'):
        print('Auth valid')
    else:
        if os.environ['HOME'] == '/root':  # smells like docker
            # Get a request token
            flickr.get_request_token(oauth_callback='oob')
            authorize_url = flickr.auth_url(perms='write')
            print('Please open: \n' + authorize_url)
            verifier = str(input('Verifier code: '))
            flickr.get_access_token(verifier)
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
        # photo_ids = [p['id'] for p in photos]
        finder = ShapefileLocationFinder(SHAPEFILE, EPSG_DATUM['NAD83'], 'SITE_NAME')
        polygons = load_custom_gpsvisualizer_polys_from_dir(POLYDIR)

        for photo in photos:
            place = None
            photo_id = photo['id']
            if skip_until and (str(photo_id) != str(skip_until)):
                print('Skip', photo_id, SKIP_TO)
                continue
            else:
                skip_until = None

            title = photo['title']
            try:
                gps_data = flickr.photos.geo.getLocation(photo_id=photo_id)
            except Exception:
                print(photo_id, title, 'No GPS')
                continue

            try:
                photo_details = flickr.photos.getInfo(photo_id=photo_id)
            except Exception:
                print(photo_id, title, 'Flickr b0rked')
                break

            tags = photo_details['photo']['tags']['tag']
            tags_raw = [t['raw'] for t in tags]

            openspace_tags = [t for t in tags_raw if match_openspace_tag(t)]
            if len(openspace_tags) > 0:
                print(photo_id, title, 'already tagged', openspace_tags)
                continue

            lat_lon = (
                float(gps_data['photo']['location']['latitude']), float(gps_data['photo']['location']['longitude']))

            lng_lat_point = lng_lat_point_from_lat_lng(lat_lon)
            for named_poly in polygons:
                if named_poly['polygon'].contains(lng_lat_point):
                    place = named_poly['name']
                    print(f'Found {photo_id} in {place} polyfile')
                    break

            if not place:
                place = finder.place_from_lat_lng(lat_lon)

            print(f'{photo_id}, {title}, {place}')
            if place:
                place_tag = make_openspace_tag(place)
                flickr.photos.addTags(photo_id=photo_id, tags=place_tag)


def flickr_get_token(flickr, perms='read'):
    if not flickr.token_valid(perms=perms):
        # Get a request token
        flickr.get_request_token(oauth_callback='oob')

        # Open a browser at the authentication URL. Do this however
        # you want, as long as the user visits that URL.
        authorize_url = flickr.auth_url(perms=perms)
        webbrowser.open_new_tab(authorize_url)

        # Get the verifier code from the user. Do this however you
        # want, as long as the user gives the application the code.
        verifier = str(input('Verifier code: '))

        # Trade the request token for an access token
        flickr.get_access_token(verifier)


if __name__ == '__main__':
    run_cli()
