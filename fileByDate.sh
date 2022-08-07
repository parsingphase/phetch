#!/usr/bin/env bash


SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"

DIR="/Users/wechsler/Pictures/Lightroom Export 2020-2021"

cd "$DIR" || exit 1

function getDateDir () {
  FILE=$1
  DIR=$(exiftool -q -q -d "%Y/%m/%d" -p '$CreateDate' $FILE)
  echo $DIR
}

FILES=$(find . -maxdepth 1 -type f -exec echo '{}' \;)

for FILE in $FILES:
do
  BASEFILE=$(basename -- $FILE)
  STEM="${BASEFILE%.*}"
  EXT="${BASEFILE##*.}"
  UEXT=$(echo $EXT | tr '[:lower:]' '[:upper:]')
  if [[ "$UEXT" == "XMP" ]]; then
    echo "Skip XMP:${BASEFILE}"
    continue
  fi

  NEWDIR=$(getDateDir $FILE)
  mkdir -p $NEWDIR
  echo "$BASEFILE : $UEXT => $NEWDIR"
  if [[ "$UEXT" == "CR2" || "$UEXT" == "CR3" ]]; then
    if [[ -f "$STEM.xmp" ]]; then
      echo cp "$STEM.xmp" "${NEWDIR}"
    fi
  fi
  echo cp "$BASEFILE" "${NEWDIR}"
  . "${SCRIPT_DIR}/context.sh" "$BASEFILE" -k >> "$NEWDIR/catalog.txt"
done

open .