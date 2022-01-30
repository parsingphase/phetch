from phetch_tools.init_flickr import init_flickr_client
from gps_tools import ShapefileLocationFinder, EPSG_DATUM
import re

SHAPEFILE = 'tmp/openspace/OPENSPACE_POLY'


def run_cli():
    flickr = init_flickr_client('./config.yml')

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
        print(tags_raw)
        openspace_tags = [t for t in tags_raw if re.match(r'^geo:ma-openspace=', t)]
        if len(openspace_tags) > 0:
            print(photo_id, ' already tagged', openspace_tags)

        lat_lon = (gps_data['photo']['location']['latitude'], gps_data['photo']['location']['longitude'])
        place = finder.place_from_lat_lng(lat_lon)
        place_tag = f'geo:ma-openspace={place}'
        print(f'{photo_id}, {title}, {place}, {place_tag}')
        # flickr.photos.addTags(photo_id=photo_id, tags=place_tag)
        # oauth needed: https://www.flickr.com/services/api/auth.oauth.html / https://stuvel.eu/flickrapi-doc/3-auth.html
        break


if __name__ == '__main__':
    run_cli()
