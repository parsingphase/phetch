from pprint import pprint
from typing import List, Optional
from pathlib import PurePath

import pyproj
import shapefile
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

from .datum import EPSG_DATUM


# def find_lat_lng_shapefile_place(photoLatLng, shapefilePath):
#     finder = ShapefileLocationFinder(shapefilePath, EPSG_DATUM['NAD83'], 'SITE_NAME')
#     return finder.place_from_lat_lng(photoLatLng)


def make_poly_from_bbox(box: List[float]):
    return Polygon([(box[0], box[1]), (box[0], box[3]), (box[2], box[3]), (box[2], box[1])])


def record_matches(record, field, match):
    record_dict = record.as_dict()
    return field in record_dict and match in record_dict[field]


class ShapefileLocationFinder:
    """
    Tool to locate points in shapefiles
    """
    shapefile: shapefile.Reader
    coord_reference: pyproj.crs.CRS
    place_name_field: str
    gps_point_transformer: pyproj.transformer.Transformer
    bounding_polygon: Polygon

    def __init__(self, shapefile_path: str, place_name_field: str) -> None:
        super().__init__()
        self.shapefile = shapefile.Reader(shapefile_path)
        prj_file = PurePath(shapefile_path).with_suffix('.prj')

        with open(prj_file) as f:
            prj_file_data = f.read()
            self.coord_reference = pyproj.crs.CRS.from_user_input(prj_file_data)

        self.place_name_field = place_name_field

        self.gps_point_transformer = pyproj.Transformer.from_crs(EPSG_DATUM['WGS84'], self.coord_reference,
                                                                 always_xy=True)
        self.bounding_polygon = make_poly_from_bbox(self.shapefile.bbox)

    def place_from_lat_lng(self, lat_lng) -> Optional[str]:
        point = Point(self.gps_point_transformer.transform(lat_lng[1], lat_lng[0]))
        if not self.bounding_polygon.contains(point):
            # print('Point not in shapefile bbox', self.bounding_polygon, point)
            return None

        fallback = None

        shapes = self.shapefile.shapes()
        for i in range(1, len(shapes)):
            shape = self.shapefile.shape(i)

            if len(shape.points) < 3:
                continue

            try:
                poly = Polygon(shape.points)
                if poly.contains(point):
                    record = self.shapefile.record(i)
                    # Can be multiple hits in "Georgia GIS Clearinghouse (data.georgiaspatial.org)" which may just show interest, not ownership
                    if record_matches(record, 'GIS_Src', 'data.georgiaspatial.org') or \
                            record_matches(record, 'Loc_Nm', 'FLAP') or \
                            record_matches(record, 'Loc_Nm', 'State Trust Land') or \
                            record_matches(record, 'Unit_Nm', 'Field Office') or \
                            record_matches(record, 'Des_Tp', 'MIL') or \
                            record[self.place_name_field] == 'Park':
                        # record_matches(record, 'Own_Name', 'OTHS') or \
                        continue
                    elif record_matches(record, 'FeatClass', 'Proclamation'):
                        fallback = record[self.place_name_field]
                    else:
                        # pprint(record.as_dict())
                        # fallback = record[self.place_name_field]
                        return record[self.place_name_field]

            except Exception:
                continue

        return fallback

    def lat_lng_is_in_bbox(self, lat_lng):
        point = Point(self.gps_point_transformer.transform(lat_lng[1], lat_lng[0]))
        return self.bounding_polygon.contains(point)
