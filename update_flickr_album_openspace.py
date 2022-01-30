from phetch_tools.init_flickr import init_flickr_client
from gps_tools import ShapefileLocationFinder, EPSG_DATUM, match_openspace_tag, make_openspace_tag
import webbrowser

SHAPEFILE = 'tmp/openspace/OPENSPACE_POLY'


def run_cli():
    flickr = init_flickr_client('./config.yml')

    # oauth needed: https://www.flickr.com/services/api/auth.oauth.html / https://stuvel.eu/flickrapi-doc/3-auth.html
    if flickr.token_valid(perms='write'):
        print('Auth valid')
    else:
        flickr_get_token(flickr, 'write')

    album = flickr.photosets.getPhotos(photoset_id=72157717912633238)
    photos = album['photoset']['photo']
    # photo_ids = [p['id'] for p in photos]
    finder = ShapefileLocationFinder(SHAPEFILE, EPSG_DATUM['NAD83'], 'SITE_NAME')

    for photo in photos:
        photo_id = photo['id']
        title = photo['title']
        try:
            gps_data = flickr.photos.geo.getLocation(photo_id=photo_id)
        except Exception:
            continue

        photo_details = flickr.photos.getInfo(photo_id=photo_id)
        tags = photo_details['photo']['tags']['tag']
        tags_raw = [t['raw'] for t in tags]

        openspace_tags = [t for t in tags_raw if match_openspace_tag(t)]
        if len(openspace_tags) > 0:
            print(photo_id, title, 'already tagged', openspace_tags)
            continue

        lat_lon = (gps_data['photo']['location']['latitude'], gps_data['photo']['location']['longitude'])
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
