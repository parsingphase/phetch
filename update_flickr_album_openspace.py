from phetch_tools.init_flickr import init_flickr_client
from gps_tools import ShapefileLocationFinder, EPSG_DATUM, match_openspace_tag, \
    make_openspace_tag, load_custom_gpsvisualizer_polys_from_dir, lng_lat_point_from_lat_lng
import webbrowser

SHAPEFILE = 'tmp/openspace/OPENSPACE_POLY'
SKIP_TO = None
# ALBUM_ID = 72177720295678754  # Massachusetts Wildlife 2022
ALBUM_ID = 72157717912633238  # Wildlife Showcase 2021
# ALBUM_ID = 72177720295655372  # Massachusetts Birds 2022
POLYDIR = 'polyfiles'


def run_cli():
    skip_until = SKIP_TO
    flickr = init_flickr_client('./config.yml')

    # oauth needed: https://www.flickr.com/services/api/auth.oauth.html / https://stuvel.eu/flickrapi-doc/3-auth.html
    if flickr.token_valid(perms='write'):
        print('Auth valid')
    else:
        flickr_get_token(flickr, 'write')

    album = flickr.photosets.getPhotos(photoset_id=ALBUM_ID)
    photos = album['photoset']['photo']
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

        lat_lon = (float(gps_data['photo']['location']['latitude']), float(gps_data['photo']['location']['longitude']))

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
