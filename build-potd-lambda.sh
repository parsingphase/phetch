#!/usr/bin/env bash

set -e

CONFIG_FILE="config.yml"
SOURCE_FILES="cron_image_tweet.py phetch.py mastodon_post.py phetch_tools potd_schedules/*.txt"
AWSREGION="us-east-1"
LAMBDA_NAME="postBirdOfTheDayTweet"

for arg in "$@"; do
    case ${arg} in
        "--upload")
            DO_UPLOAD=1;;
        "--validate")
            DO_VALIDATE=1;;
        *)
            echo "Invalid argument ${arg}. Valid options are --validate, --upload"
            exit 1
    esac
done

get_script_dir () {
    SOURCE="${BASH_SOURCE[0]}"
    SOURCE_DIR=$( dirname "$SOURCE" )
    SOURCE_DIR=$(cd -P ${SOURCE_DIR} && pwd)
    echo ${SOURCE_DIR}
}

SCRIPT_DIR="$( get_script_dir )"

CACHE_DIR="${SCRIPT_DIR}/cache"
BUILD_DIR="${SCRIPT_DIR}/build"
OUTPUT_DIR="${SCRIPT_DIR}/dist"
TMP_DIR=$(mktemp -d)
START_DIR=`pwd`

cd ${SCRIPT_DIR}

if [[ "${DO_VALIDATE}" == "1" ]]; then
    if [[ ! -f "./venv/bin/flake8" ]]; then
        echo "Validator missing, fetching"
        pipenv install --dev
    fi

    echo "Validating source code…"
    set +e
    make test
    VALIDATE_RESULT="$?"
    set -e
    if [[ "$VALIDATE_RESULT" == "0" ]]; then
        echo " … Validation passed"
    else
        echo " … Validation failed"
        exit 1
    fi
fi

mkdir -p ${OUTPUT_DIR} ${CACHE_DIR}

echo "Building lambda… "
echo " Working in ${TMP_DIR}"

rm -rf "${OUTPUT_DIR}/lambda.zip" "${OUTPUT_DIR}/lambda"

for file in ${SOURCE_FILES}; do
    cp -r ${file} "${TMP_DIR}"
done

if [[ -e "${CONFIG_FILE}" ]]; then
    cp "${CONFIG_FILE}" "${TMP_DIR}"
fi

cp "${BUILD_DIR}/lambda_requirements.txt" "${TMP_DIR}/requirements.txt"

BRANCH="$( git symbolic-ref --short HEAD )"
REVISION="$( git describe --tags HEAD )"
CHANGES=""
set +e # Don't bail on expected return=1
git diff-index --quiet HEAD --
if [[ "$?" == "1" ]]; then
    CHANGES="+"
fi
set -e

GIT_VERSION="version='BOTD $BRANCH $REVISION$CHANGES'"
echo " Building $GIT_VERSION"
echo  ${GIT_VERSION} > "${TMP_DIR}/bot_version.py"

cd "${TMP_DIR}"
echo " Fetching dependencies"
pip install -t . -r requirements.txt > /dev/null 2>&1
rm -rf tests *.dist-info
zip -r "${OUTPUT_DIR}/lambda.zip" * > /dev/null

echo " Lambda file built at '${OUTPUT_DIR}/lambda.zip'"

echo " … Build complete"

if [[ "${DO_UPLOAD}" == "1" ]]; then
    echo "Uploading as ${LAMBDA_NAME} to ${AWSREGION}…"
    aws lambda update-function-code --function-name ${LAMBDA_NAME} --region ${AWSREGION} \
        --zip-file "fileb://${OUTPUT_DIR}/lambda.zip" > /dev/null
    echo " … Upload complete"
fi

cd "${START_DIR}"
echo "All Done"
