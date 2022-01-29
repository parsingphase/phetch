import shapefile
import pyproj
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


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
