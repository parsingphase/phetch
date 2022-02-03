#!/usr/bin/env bash

get_script_dir () {
    SOURCE="${BASH_SOURCE[0]}"
    SOURCE_DIR=$( dirname "$SOURCE" )
    SOURCE_DIR=$(cd -P ${SOURCE_DIR} && pwd)
    echo ${SOURCE_DIR}
}

SCRIPT_DIR="$( get_script_dir )"

cd "${SCRIPT_DIR}"

docker build . -t localpython
docker run -it --rm -v ${SCRIPT_DIR}:/root/phetch -v /Users/wechsler/Pictures/Exports:/mnt/photos localpython