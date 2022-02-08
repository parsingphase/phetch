import pyproj
import shapefile
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

photoLatLng = (42.332508, -71.020932)


def run_cli() -> None:
    shapefilePath = 'tmp/openspace/OPENSPACE_POLY'
    photo_place = find_lat_lng_shapefile_place(photoLatLng, shapefilePath)

    print(photo_place)


def find_lat_lng_shapefile_place(photoLatLng, shapefilePath) -> str:
    lat_lon_to_shapefile = pyproj.Transformer.from_crs(4326, 26986, always_xy=True)
    photo_point = Point(lat_lon_to_shapefile.transform(photoLatLng[1], photoLatLng[0]))
    sf = shapefile.Reader(shapefilePath)
    shapes = sf.shapes()
    places = []

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
            places.append(place)

    return ' / '.join(places)


if __name__ == '__main__':
    run_cli()
