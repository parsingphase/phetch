#!/usr/bin/env bash

SRC_ROOT="/Users/wechsler/Pictures/"
DEST_ROOT="/Volumes/Hexapod/"
BACKUP_BASE="Archive 2016-2021/"

#YEARS="1999 2000 2016 2020 2021"
YEARS="2021"
MONTHS="01 02 03 04 05 06 07 08 09 10 11 12"

set -e

for YEAR in $YEARS
do
  echo
  echo "SYNC YEAR: $YEAR"
  echo
  for MONTH in $MONTHS
  do
    echo
    echo "SYNC: ${YEAR}/${MONTH}"
    FROM="${SRC_ROOT}${BACKUP_BASE}${YEAR}/${MONTH}/"
    if [[ -d "${FROM}" ]]; then
      echo
      TO="${DEST_ROOT}${BACKUP_BASE}${YEAR}/${MONTH}"
      mkdir -p "$TO"
      echo -n "$YEAR/${MONTH} "
      rsync -av "$FROM" "$TO"
      echo "DONE: ${YEAR}/${MONTH}"
    else
      echo "No source dir ${FROM}"
    fi
  done
  echo "DONE YEAR: $YEAR"
done
echo "ALL DONE"
