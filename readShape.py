import shapefile
import pyproj

sf = shapefile.Reader("tmp/openspace/OPENSPACE_POLY")
print(sf)
print(sf.bbox)
# print(sf.fields)
shapes = sf.shapes()
# # print(len(shapes))
shape1 = sf.shape(1)
print(shape1.points)  # units such as (230255.15420000255, 904192.4510000013)!
print(shape1.__geo_interface__)
# print(sf.record(1))
print(sf.record(1)['SITE_NAME'])

# for i in range(1, len(shapes)-1):
#     shape = sf.shape(i)
#     record = sf.record(i)
#     print(record['SITE_NAME'], shape.points, shape.__geo_interface__)
# https://www.mass.gov/info-details/overview-of-massgis-data
# The EPSG (European Petroleum Survey Group) code for this coordinate system is 26986.

shapefileToLatLon = pyproj.Transformer.from_crs(26986, 4326, always_xy=True)
print(shapefileToLatLon.transform(230255.15420000255, 904192.4510000013))

latLonToShapefile = pyproj.Transformer.from_crs(4326, 26986, always_xy=True)

print(latLonToShapefile.transform(-71, 42))

from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

polygon = Polygon(sf.shape(1).points)  # create polygon
point = Point(230255.15420000255, 904192.4510000013)  # create point
print(polygon.contains(point))  # check if polygon contains point
print(point.within(polygon))  # check if a point is in the polygon
