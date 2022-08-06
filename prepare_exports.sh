#!/usr/bin/env bash

set -e

SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"

IMAGE_DIR="$1"
if [ "$IMAGE_DIR" = "" ]; then
  echo "Usage: $0 IMAGE_DIR"
  exit 1
fi


if  [ ! -d "$IMAGE_DIR" ]; then
  echo "Cannot find dir '$IMAGE_DIR'"
  exit 1
fi

# realpath is in brew install coreutils
IMAGE_DIR_ABS=$(realpath "$IMAGE_DIR")
echo "Abs image dir: '$IMAGE_DIR_ABS'"

# shellcheck source=..
cd "${SCRIPT_DIR}"

"${SCRIPT_DIR}/introspect.py" --rename "$IMAGE_DIR_ABS"
"${SCRIPT_DIR}/find_photo_openspace.py" "$IMAGE_DIR_ABS"
"${SCRIPT_DIR}/automark.py" --resize 2048 "$IMAGE_DIR_ABS"

echo Creating index "$IMAGE_DIR_ABS/catalog.txt"
echo "Index" > "$IMAGE_DIR_ABS/catalog.txt"
echo >> "$IMAGE_DIR_ABS/catalog.txt"
find "$IMAGE_DIR_ABS" -maxdepth 1 -type f -iname '*.jpg' -exec ${SCRIPT_DIR}/context.sh "{}" \; >> $IMAGE_DIR_ABS/catalog.txt

echo prepare_exports.sh DONE