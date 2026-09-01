#!/usr/bin/env bash
set -e

docker run \
    --rm \
    --restart=no \
    --name home-assistant \
    --env "TZ=Europe/Vienna" \
    --publish="80:8123/tcp" \
    --publish="80:8123/udp" \
    --volume ./config:/config \
    --volume ./custom_components:/config/custom_components \
    ghcr.io/home-assistant/home-assistant:stable
