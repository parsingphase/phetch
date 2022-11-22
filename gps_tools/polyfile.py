from pathlib import Path
from typing import List, Tuple, TypedDict
import json

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

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


def load_custom_gpsvisualizer_polys_from_dir(dir: str) -> List[Polygon]:
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


def load_native_lands_polys_from_file(data_file: str) -> List[Polygon]:
    """
    Load text files from a directory as Polygons with the name of the file
    Args:
        dir:

    Returns:

    """
    polys = []

    with open(data_file, 'r') as myfile:
        text = myfile.read()

    data = json.loads(text)

    for feature in data['features']:
        if 'Name' in feature['properties']:
            name = feature['properties']['Name']
            boundaries = feature['geometry']['coordinates']  # points are lng, lat
            # print(name, feature['properties']['description'], boundaries)
            for boundary in boundaries:
                if len(boundary) >= 3:
                    try:
                        boundary_2d = [pt[0:2] for pt in boundary]
                        polygon = Polygon(boundary_2d)  # Normalize to 2D (some 3d pts can exist!)
                        polys.append({'name': name, 'polygon': polygon})
                    except Exception as e:
                        print(boundary)
                        print(boundary_2d)
                        print(e)
                        raise e

    return polys


def lng_lat_point_from_lat_lng(lat_lng: Tuple) -> Point:
    """
    Generate a lng-lat Point from a lat-lng Tuple
    Args:
        lat_lng:

    Returns:

    """
    return Point(lat_lng[::-1]) if lat_lng else None


def list_to_punctuated_string(list) -> str:
    punctuated_string = list[0] if len(list) > 0 else ''
    if len(list) > 1:
        punctuated_string = ', '.join(list[0:-1]) + ' & ' + list[-1]
    return punctuated_string


def run_cli() -> None:
    # poly = read_polygon_from_gpsvisualizer_txt('polyfiles/Fresh Pond Reservation.txt')
    # point = Point(-71.150795, 42.389045)
    poly = load_custom_gpsvisualizer_polys_from_dir('polyfiles')[0]['polygon']
    point = Point(-71.154606, 42.383119)
    # point = Point(-71.131440, 42.387016)
    print('IN' if poly.contains(point) else 'OUT')


if __name__ == '__main__':
    run_cli()
