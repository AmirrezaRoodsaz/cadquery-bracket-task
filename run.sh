#!/bin/sh
# Build the image and run the task end to end. Exit 0 means the part meets the spec.
set -e
cd "$(dirname "$0")"
docker build -t cadquery-bracket-task .
docker run --rm cadquery-bracket-task
