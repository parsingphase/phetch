from typing import List, Optional

import pyproj
import shapefile
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from .datum import EPSG_DATUM


def find_lat_lng_shapefile_place(photoLatLng, shapefilePath):
    finder = ShapefileLocationFinder(shapefilePath, EPSG_DATUM['NAD83'], 'SITE_NAME')
    return finder.place_from_lat_lng(photoLatLng)
    #
    # lat_lon_to_shapefile = pyproj.Transformer.from_crs(EPSG_WGS84, EPSG_NAD83, always_xy=True)
    # photo_point = Point(lat_lon_to_shapefile.transform(photoLatLng[1], photoLatLng[0]))
    # sf = shapefile.Reader(shapefilePath)
    # shapes = sf.shapes()
    # for i in range(1, len(shapes)):
    #     shape = sf.shape(i)
    #     place = sf.record(i)['SITE_NAME']
    #
    #     if len(shape.points) < 3:
    #         continue
    #
    #     try:
    #         poly = Polygon(shape.points)
    #     except Exception as e:
    #         print(shape.points)
    #         print(e)
    #         break
    #
    #     if poly.contains(photo_point):
    #         return place
    #
    # return None


def make_poly_from_bbox(box: List[float]):
    return Polygon([(box[0], box[1]), (box[0], box[3]), (box[2], box[3]), (box[2], box[1])])


class ShapefileLocationFinder:
    """
    Tool to locate points in shapefiles
    """
    shapefile: shapefile.Reader
    datum: int
    place_name_field: str
    gps_point_transformer: pyproj.transformer.Transformer
    bounding_polygon: Polygon

    def __init__(self, shapefile_path: str, shapefile_datum: int, place_name_field: str) -> None:
        super().__init__()
        self.shapefile = shapefile.Reader(shapefile_path)
        self.datum = shapefile_datum
        self.place_name_field = place_name_field
        self.gps_point_transformer = pyproj.Transformer.from_crs(EPSG_DATUM['WGS84'], shapefile_datum, always_xy=True)
        self.bounding_polygon = make_poly_from_bbox(self.shapefile.bbox)

    def place_from_lat_lng(self, lat_lng) -> Optional[str]:
        point = Point(self.gps_point_transformer.transform(lat_lng[1], lat_lng[0]))
        if not self.bounding_polygon.contains(point):
            print('Point not in shapefile bbox')
            return None

        shapes = self.shapefile.shapes()
        for i in range(1, len(shapes)):
            shape = self.shapefile.shape(i)

            if len(shape.points) < 3:
                continue

            try:
                poly = Polygon(shape.points)
                if poly.contains(point):
                    return self.shapefile.record(i)[self.place_name_field]
            except Exception:
                continue

        return None

    def lat_lng_is_in_bbox(self, lat_lng):
        point = Point(self.gps_point_transformer.transform(lat_lng[1], lat_lng[0]))
        return self.bounding_polygon.contains(point)
