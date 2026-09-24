#!/usr/bin/env bash
set -e

##
# Script to easily run HA in a local container, passing the local libraries to
# the Python environment.

HA_VERSION="${1:-latest}"

docker run \
    --rm \
    --pull=always \
    --restart=no \
    --name home-assistant \
    --env "TZ=Europe/Vienna" \
    --publish="80:8123/tcp" \
    --publish="80:8123/udp" \
    --volume ./docker/config:/config \
    --volume ./custom_components:/config/custom_components \
    --volume .venv/lib/python3.14/site-packages/homeassistant/:/usr/src/homeassistant/homeassistant/ \
    ghcr.io/home-assistant/home-assistant:$HA_VERSION
