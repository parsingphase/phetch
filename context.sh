#!/usr/bin/env bash

FILENAME=$1

function ordinal () {
  case "$1" in
    *1[0-9] | *[04-9]) echo "$1"th;;
    *1) echo "$1"st;;
    *2) echo "$1"nd;;
    *3) echo "$1"rd;;
  esac
}

function etf () {
  exiftool -q -q -p "$1" "$2"
}

IMAGE_SETTINGS=$(etf '$Model, $FocalLength, ${ShutterSpeedValue}s, f/$FNumber, ISO $ISO' "$FILENAME"| sed 's/\.0//g' | sed 's/ mm/mm/g')
#    150-600mm F5-6.3 DG OS HSM | Contemporary 015 +2x
# => 150-600mm F5-6.3 DG OS HSM +2x teleconvertor
RAW_LENS=$(etf '$LensModel' "$FILENAME")
LENS=$(etf '$LensModel' "$FILENAME" | sed -E 's/\|[^+]*//' | sed -E 's/\+([0-9.]+)x/with \1x teleconverter/')

if [[ "$RAW_LENS" == *"| Contemporary"* ]]; then
  LENS="Sigma $LENS"
fi

SUBJECT=$(etf '$ObjectName' "$FILENAME")

#Extract day of month separately to call ordinal on it, then pack into more general format
DAY_OF_MONTH=$(ordinal $(exiftool -q -q -d "%-d" -p '$CreateDate' "$FILENAME"))
IMAGE_DATE=$(exiftool -q -q -d "$DAY_OF_MONTH %B %Y" -p '$CreateDate' "$FILENAME")

PLACE=
TERRITORY=
IFS=$'\n';for KEYWORD in $(exiftool -q -q -sep "\n" -sep "\n" -Keywords -b "$FILENAME")
do
  PLAIN_KEYWORD=$(echo $KEYWORD | sed 's/^"\(.*\)"$/\1/')
#  echo $PLAIN_KEYWORD
  if [[ $PLAIN_KEYWORD == geo:place* ]]; then
    PLACE=$(echo $PLAIN_KEYWORD | sed 's/.*=//' )
  fi
  if [[ $PLAIN_KEYWORD == geo:native_territory* ]]; then
    TERRITORY=$(echo $PLAIN_KEYWORD | sed 's/.*=//')
    TERRITORY="$TERRITORY traditional territory"
  fi
done

echo $(basename "$FILENAME")
echo "  $SUBJECT, $IMAGE_DATE, $PLACE"
echo "  $IMAGE_SETTINGS"
echo "  $LENS"
if [[ "$TERRITORY" != "" ]]; then
  echo "  $TERRITORY"
fi

if [[ "$2" == "-k" ]]; then
  KEYWORDS=$(etf '$Keywords' "$FILENAME")
  echo "  $KEYWORDS"
fi
echo