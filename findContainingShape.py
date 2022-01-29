import shapefile
import pyproj
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

photoLatLngs = [
    (42.397, -71.145),
    (42.385180, -71.150311),
    (42.388840, -71.135915),
    (42.369652, -71.144062),
    (42.389045, -71.150795)
]


def run_cli():
    shapefilePath = 'tmp/openspace/OPENSPACE_POLY'
    photoLatLng = photoLatLngs[0]
    photo_place = find_lat_lng_shapefile_place(photoLatLng, shapefilePath)

    print(photo_place)


def find_lat_lng_shapefile_place(photoLatLng, shapefilePath):
    lat_lon_to_shapefile = pyproj.Transformer.from_crs(4326, 26986, always_xy=True)
    photo_point = Point(lat_lon_to_shapefile.transform(photoLatLng[1], photoLatLng[0]))
    sf = shapefile.Reader(shapefilePath)
    shapes = sf.shapes()
    for i in range(1, len(shapes)):
        shape = sf.shape(i)
        place = sf.record(i)['SITE_NAME']

        if len(shape.points) < 3:
            continue

        try:
            poly = Polygon(shape.points)
        except Exception as e:
            print(shape.points)
            print(e)
            break

        if poly.contains(photo_point):
            return place

    return None


if __name__ == '__main__':
    run_cli()
