from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
from typing import TypedDict, List, Tuple
from pathlib import Path

# NOTE: Points & polys here are LON-LAT, as per ESRI files
NamedPolygon = TypedDict('NamedPolygon', {'name': str, 'polygon': Polygon})


def read_polygon_from_gpsvisualizer_txt(filename: str) -> Polygon:
    """
    Generate a single Polygon from a single-TRACK text file
    created at https://www.gpsvisualizer.com/draw/
    Be sure to use OSM view to avoid incorporating external commercial IP

    Args:
        filename:

    Returns:

    """
    with open(filename) as f:
        contents = f.readlines()

    points = []
    for row in contents:
        parts = row.strip().split('\t')
        if parts[0] == 'T' and len(parts) > 2:
            point = (float(parts[2]), float(parts[1]))  # ln-lat!
            points.append(point)

    poly = Polygon(points)
    return poly


def load_custom_gpsvisualizer_polys_from_dir(dir: str) -> List[NamedPolygon]:
    """
    Load text files from a directory as Polygons with the name of the file
    Args:
        dir:

    Returns:

    """
    source_dir = Path(dir.rstrip('/'))
    source_files = list(source_dir.glob('*.txt'))
    polys = []
    for source_file in source_files:
        filename = source_file.stem
        poly = read_polygon_from_gpsvisualizer_txt(str(source_file))
        polys.append({'name': filename, 'polygon': poly})

    return polys


def lng_lat_point_from_lat_lng(lat_lng: Tuple) -> Point:
    """
    Generate a lng-lat Point from a lat-lng Tuple
    Args:
        lat_lng:

    Returns:

    """
    return Point(lat_lng[::-1]) if lat_lng else None


def run_cli():
    # poly = read_polygon_from_gpsvisualizer_txt('polyfiles/Fresh Pond Reservation.txt')
    # point = Point(-71.150795, 42.389045)
    poly = load_custom_gpsvisualizer_polys_from_dir('polyfiles')[0]['polygon']
    point = Point(-71.154606, 42.383119)
    # point = Point(-71.131440, 42.387016)
    print('IN' if poly.contains(point) else 'OUT')


if __name__ == '__main__':
    run_cli()
