#!/usr/bin/env bash

set -exuo pipefail

COMPILER="$1"
STATUS="$2"
OUTPUT_PATH="$3"
START_TIME="$4"
AWS=${AWS:-aws}

BUILD_DURATION=$(( $(date +%s) - START_TIME ))
BUILD_COMPLETE_TIME=$(date -u -Iseconds)
TEMP_ENTRY_FILE=$(mktemp --tmpdir entry.XXXXXXXXXX.json)
cleanup() {
    rm -f "${TEMP_ENTRY_FILE}"
}
trap cleanup EXIT

echo Build complete, environment is:
env | grep -v AWS_

cat <<EOF > "${TEMP_ENTRY_FILE}"
{
  "compiler": {"S": "${COMPILER}"},
  "timestamp": {"S": "${BUILD_COMPLETE_TIME}"},
  "duration": {"N": "${BUILD_DURATION}"},
  "status": {"S": "${STATUS}"},
  "path": {"S": "${OUTPUT_PATH}"}
}
EOF
jq -C . "${TEMP_ENTRY_FILE}"

${AWS} dynamodb put-item \
    --table-name compiler-builds \
    --item file://"${TEMP_ENTRY_FILE}"
