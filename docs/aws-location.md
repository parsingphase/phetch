

Fresh Pond: 42.385180, -71.150311
Alewife Brook: 42.397, -71.145 

https://awscli.amazonaws.com/v2/documentation/api/latest/reference/location/index.html

https://console.aws.amazon.com/location/places/home?region=us-east-1#/describe/explore.place

    aws location list-place-indexes
    aws location search-place-index-for-position --position "[-71.145,42.397]" --index-name explore.place
    aws location search-place-index-for-position --position "[-71.1503,42.3852]" --index-name explore.place


- https://stackoverflow.com/questions/43892459/check-if-geo-point-is-inside-or-outside-of-polygon

- https://pypi.org/project/turfpy/
- https://gis.stackexchange.com/questions/250172/finding-out-if-coordinate-is-within-shapefile-shp-using-pyshp
- https://www.mass.gov/info-details/massgis-data-protected-and-recreational-openspace#downloads-
