#!/usr/bin/env bash

set -e
#set -x

get_script_dir () {
    SOURCE="${BASH_SOURCE[0]}"
    SOURCE_DIR=$( dirname "$SOURCE" )
    SOURCE_DIR=$(cd -P "${SOURCE_DIR}" && pwd)
    echo "${SOURCE_DIR}"
}

BUILD_DIR="$( get_script_dir )"
PROJ_DIR=$(dirname "$BUILD_DIR")
DIST_DIR="${PROJ_DIR}/dist"
#TMP_DIR=$(mktemp -d)
#START_DIR=$(pwd)

DISTRO="${1}"

if [[ "${DISTRO}" == "" ]]; then
  echo "Must specify distro"
  exit 1
fi

DISTRO_FILE="${BUILD_DIR}/fetcher_distro_scripts/${DISTRO}.sh"

if [[ -f "${DISTRO_FILE}" ]]; then
  rm -rf "${DIST_DIR:?}/${DISTRO:?}"
  echo "${DISTRO}.sh exists, building ${DIST_DIR}/${DISTRO}"
else
  echo "No such distro file ${DISTRO} in ${BUILD_DIR}/fetcher_distro_scripts"
  exit 1
fi

LIBDIR="${DIST_DIR}/${DISTRO}/fetcher"

cd "${PROJ_DIR}"
rm -rf "${DIST_DIR:?}/${DISTRO:?}"
rm -rf "${DIST_DIR:?}/${DISTRO:?}.zip"

mkdir -p "${LIBDIR}/phetch_tools"
cp fetch_from_json.py Pipfile "${LIBDIR}"
cp -r phetch_tools "${LIBDIR}"
cp "${DISTRO_FILE}" "${DIST_DIR}/${DISTRO}/FetchNewImages.command"
cp "${BUILD_DIR}/READ ME FIRST.pdf" "${DIST_DIR}/${DISTRO}"
chmod u+x "${DIST_DIR}/${DISTRO}/FetchNewImages.command"
cp "${BUILD_DIR}/fetcher-requirements.txt" "${LIBDIR}/requirements.txt"
cd "${LIBDIR}" && pip install -r requirements.txt -t .
cd "${DIST_DIR}" && zip -r "${DISTRO}.zip" "${DISTRO}"
open "${DIST_DIR}"

echo "Completed successfully, ${DIST_DIR}/${DISTRO}.zip created"