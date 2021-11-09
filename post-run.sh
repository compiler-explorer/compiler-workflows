#!/usr/bin/env bash

set -exuo pipefail

BUILD_COMPLETE_TIME=$(date -u -Iseconds)

echo Build complete, environment is:
env | grep -v AWS_

cat <<EOF > entry.json
{
  "compiler": {"S": "test-gcc"},
  "timestamp": {"S": "$(date -u -Iseconds)"},
  "duration": {"N": "123"},
  "status": {"S": "SUCCESS"},
  "path": {"S": "s3://something/tar.xz"}
}
EOF
jq -C . entry.json

aws dynamodb put-item \
    --table-name compiler-builds \
    --item file://entry.json

rm entry.json