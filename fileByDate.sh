#!/usr/bin/env bash

# Point to a folder containing a flat export of Lightroom originals

PHOTO_DIR="/Users/wechsler/Pictures/Archive 2016-2021"


SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"


cd "$PHOTO_DIR" || exit 1

function getDateDir () {
  FILE=$1
  DATEDIR=$(exiftool -q -q -d "%Y/%m/%d" -p '$CreateDate' $FILE)
  echo $DATEDIR
}

FILES=$(find -s . -maxdepth 1 -type f -exec echo '{}' \;)

#set -x
OLDIFS=$IFS
IFS=$'\n'
for FILE in $FILES:
do
  echo "Checking ${FILE}"
  BASEFILE=$(basename -- $FILE)
  STEM="${BASEFILE%.*}"
  EXT="${BASEFILE##*.}"
  UEXT=$(echo $EXT | tr '[:lower:]' '[:upper:]')

  if [[ "$UEXT" == "DNG" ]]; then
    echo "    Skip DNG:${BASEFILE}"
    continue
  fi

  if [[ "$UEXT" == "XMP" ]]; then
    echo "    Skip XMP:${BASEFILE}"
    continue
  fi

  NEWDIR=$(getDateDir $FILE)
#  echo $NEWDIR
  if [[ "$NEWDIR" == "" ]]; then
    echo "No data for ${FILE}"
    continue
  fi

  mkdir -p $NEWDIR
  echo "$BASEFILE : $UEXT => $NEWDIR"

  # shouldn't run context script if we don't copy…
  if [[ -f "$NEWDIR/$BASEFILE" ]]; then
    echo "$NEWDIR/$BASEFILE already exists"
  else
    . "${SCRIPT_DIR}/context.sh" "$BASEFILE" -k >> "$NEWDIR/catalog.txt"
    mv -n "$BASEFILE" "${NEWDIR}"
  fi

  if [[ "$UEXT" == "CR2" || "$UEXT" == "CR3" ]]; then
    if [[ -f "$STEM.xmp" ]]; then
      echo "    $STEM.xmp => ${NEWDIR}"
      mv -n "$STEM.xmp" "${NEWDIR}"
    fi
  fi
done
IFS=$OLDIFS
#open .