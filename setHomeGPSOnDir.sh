#!/bin/bash

DIR=$1
echo "Updating *.jpg in ${DIR}"
cd $DIR
ls -1 *.jpg | xargs -tIz exiftool z -gpslatitude=42.503  -gpslongitude=71.0534 -gpslatituderef=N -gpslongituderef=W
