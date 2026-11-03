#!/usr/bin/env bash
set -euo pipefail
docker network inspect module5-qa >/dev/null 2>&1 || docker network create module5-qa
if ! docker inspect module5-selenoid --format '{{json .NetworkSettings.Networks}}' | grep -q 'module5-qa'; then
  docker network connect module5-qa module5-selenoid
fi
docker run -d --name module5-selenoid-ui --restart unless-stopped \
  --network module5-qa --label project=module5 -p 127.0.0.1:14446:8080 \
  aerokube/selenoid-ui:1.10.11 --selenoid-uri http://module5-selenoid:4444
