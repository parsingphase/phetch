#!/usr/bin/env python
import csv


def placemark(site, latlng: str, color: str = 'ffaaaaaa'):
    point = latlng.split(',')
    point.reverse()
    lnglat = ','.join(point)
    return f"""<Placemark>
                <Style>
                <IconStyle>
                    <scale>1</scale>
                    <color>{color}</color>
                    <Icon>
                        <href>http://maps.google.com/mapfiles/kml/paddle/wht-blank.png</href>
                    </Icon>
                </IconStyle>
            </Style>
    <name>{site}</name>
    <Point>
      <coordinates>{lnglat},0</coordinates>
    </Point>
  </Placemark>
"""


input = 'data/Birding locations/Sheet 1-Locations.csv'

placemarks = []

with open(input, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        owner = row['Ownership / type']
        if owner == 'DCR':
            color = 'ff4974a4'  # brown
        elif owner == 'Mass Audubon':
            color = 'ffdd7777'  # blue
        elif owner == 'Trustees':
            color = 'ff77dd77'  # green
        elif owner == 'NWR':
            color = 'ff77dddd'  # yellow
        else:
            color = 'ffaaaaaa'  # gray

        placemarks.append(placemark(row['Site'], row['Lat-Lng'], color))

placemarks_xml = ''.join(placemarks)
print(f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"><Document>{placemarks_xml}</Document></kml>""")
