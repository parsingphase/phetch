from .datum import EPSG_DATUM
from .gps import GPS
from .polyfile import (NamedPolygon, lng_lat_point_from_lat_lng,
                       load_custom_gpsvisualizer_polys_from_dir,
                       read_polygon_from_gpsvisualizer_txt)
# from .shapefile import ShapefileLocationFinder, find_lat_lng_shapefile_place
from .shapefile import ShapefileLocationFinder
from .tags import make_openspace_tag, match_openspace_tag

__all__ = [
    'GPS',
    'ShapefileLocationFinder',
    'EPSG_DATUM',
    'make_openspace_tag',
    'match_openspace_tag',
    'load_custom_gpsvisualizer_polys_from_dir',
    'read_polygon_from_gpsvisualizer_txt',
    'NamedPolygon',
    'lng_lat_point_from_lat_lng'
]
