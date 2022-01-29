import shapefile
import pyproj
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

photoLatLng = [
    (42.397, -71.145),
    (42.385180, -71.150311),
    (42.388840, -71.135915),
    (42.369652, -71.144062),
    (42.389045, -71.150795)
]
shapefilePath = 'tmp/openspace/OPENSPACE_POLY'


def run_cli():
    lat_lon_to_shapefile = pyproj.Transformer.from_crs(4326, 26986, always_xy=True)
    photo_points = [{'gps': ll, 'crs': Point(lat_lon_to_shapefile.transform(ll[1], ll[0]))} for ll in photoLatLng]

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

        for photo_point in photo_points:
            if poly.contains(photo_point['crs']):
                print(f'{photo_point["gps"]} is in {place}')


if __name__ == '__main__':
    run_cli()
