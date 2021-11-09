#!/usr/bin/env bash

set -exuo pipefail

COMPILER="$1"
STATUS="$2"
OUTPUT_PATH="$3"
START_TIME="$4"

BUILD_DURATION=$(( $(date +s) - START_TIME ))
BUILD_COMPLETE_TIME=$(date -u -Iseconds)

echo Build complete, environment is:
env | grep -v AWS_

cat <<EOF > entry.json
{
  "compiler": {"S": "${COMPILER}"},
  "timestamp": {"S": "${BUILD_COMPLETE_TIME}"},
  "duration": {"N": "${BUILD_DURATION}"},
  "status": {"S": "${STATUS}"},
  "path": {"S": "${OUTPUT_PATH}"}
}
EOF
jq -C . entry.json

aws dynamodb put-item \
    --table-name compiler-builds \
    --item file://entry.json

rm entry.json