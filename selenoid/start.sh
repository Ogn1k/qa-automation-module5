#!/usr/bin/env bash
set -euo pipefail
config_path="$(cd "$(dirname "$0")" && pwd)"
docker volume create module5-video
video_path="$(docker volume inspect module5-video --format '{{.Mountpoint}}')"
docker run -d --name module5-selenoid --restart unless-stopped --label project=module5 \
  -p 127.0.0.1:14445:4444 -e DOCKER_API_VERSION=1.44 \
  -e "OVERRIDE_VIDEO_OUTPUT_DIR=$video_path" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$config_path:/etc/selenoid:ro" -v module5-video:/opt/selenoid/video \
  aerokube/selenoid:1.11.3 -limit 2 -timeout 2m -video-output-dir /opt/selenoid/video
