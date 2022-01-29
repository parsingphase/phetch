import shapefile
import pyproj
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

photoLatLng = (42.397, -71.145)
shapefilePath = 'tmp/openspace/OPENSPACE_POLY'


def run_cli():
    lat_lon_to_shapefile = pyproj.Transformer.from_crs(4326, 26986, always_xy=True)
    photo_shapefile_coords = lat_lon_to_shapefile.transform(photoLatLng[1], photoLatLng[0])
    photo_point = Point(photo_shapefile_coords)

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
            print(f'{photoLatLng} is in {place}')


if __name__ == '__main__':
    run_cli()
