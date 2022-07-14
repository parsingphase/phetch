#!/usr/bin/env python

import json

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon


def main():
    # read file
    data_file = 'data/indigenousTerritories.json'
    with open(data_file, 'r') as myfile:
        text = myfile.read()

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
        #  offshore:
        [44.268744, -68.038325],
        [42.263140, -70.182542],
        [42.755152, -70.802262],  # Parker River NWR…
        [42.77285, -70.80860],  # Parker River NWR…
        [42.50083, -71.30917],
    ]

    data = json.loads(text)

    for lat_lng in points:
        territories = []
        point = Point(lat_lng[1], lat_lng[0])

        # parse file

        for feature in data['features']:
            if 'Name' in feature['properties']:
                name = feature['properties']['Name']
                boundaries = feature['geometry']['coordinates']  # points are lng, lat
                # print(name, feature['properties']['description'], boundaries)
                for boundary in boundaries:
                    if len(boundary) >= 3:
                        polygon = Polygon(boundary)
                        if polygon.contains(point):
                            territories.append(name)
                            break

        territories.sort()
        territory_list = list_to_punctuated_string(territories)

        print(lat_lng, territory_list + ' native land' if territory_list else '')


def list_to_punctuated_string(territories):
    territory_list = ''
    if len(territories) > 1:
        territory_list = ', '.join(territories[0:-1]) + ' & ' + territories[-1]
    return territory_list


main()
