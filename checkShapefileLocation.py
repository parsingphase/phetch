#!/usr/bin/env python

from gps_tools import ShapefileLocationFinder

from shapefile_list import shapefiles


def run_cli() -> None:
    """
    Run the script from the CLI
    :return:
    """

    points = [
        [42.389022, -71.136443],
        [42.43732, -71.11079],
        [42.435295, -71.094328],
        [41.0257, -83.009584],
        [32.27015, -111.20190],
        [32.28234, -111.42471],
        [32.211458, -110.992641],
        [44.408963, -68.247284],
        [41.256928, -72.554054],
        [41.25075, -72.54492],
        [44.268744, -68.038325]
    ]

    for point in points:
        place = None
        for shape in shapefiles:
            finder = ShapefileLocationFinder(shape['filename'], shape['name_field'])
            place = finder.place_from_lat_lng(point)
            if place:
                print(point, shape['name'], ':', place)
                break
        if not place:
            print(point)


run_cli()
