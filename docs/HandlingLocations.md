# Useful info for managing GPS data

## Drawing polyfiles: 

https://www.gpsvisualizer.com/draw/

## ArgGIS, shapefiles & datums:

 * US Standard: WGS84
 * MA openspace: NAD83
 * NPS: 3857 (!?!) - WGS_1984_Web_Mercator_Auxiliary_Sphere - https://wiki.openstreetmap.org/wiki/EPSG:3857
 * OSM: 3857?

### Finding datum in NPS ArcGIS:

eg on https://public-nps.opendata.arcgis.com/datasets/nps::nps-boundary-1/about
or https://public-nps.opendata.arcgis.com/datasets/nps::nps-boundary-1/explore?location=12.437250%2C-12.497900%2C2.88

View Data Source => Extent => Spatial Reference: 102100 (3857)
