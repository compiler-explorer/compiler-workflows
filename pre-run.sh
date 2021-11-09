#!/usr/bin/env bash

set -exuo pipefail

BUILD_START_TIME=$(date -u -Iseconds)

echo Build start, environment is:
env | grep -v AWS_

echo BUILD_START_TIME=${BUILD_START_TIME} >> ${GITHUB_ENV}
