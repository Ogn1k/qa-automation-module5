$ErrorActionPreference = 'Stop'
$configPath = (Resolve-Path -LiteralPath $PSScriptRoot).Path
docker volume create module5-video
if ($LASTEXITCODE -ne 0) { throw 'Cannot create video volume' }
$videoPath = docker volume inspect module5-video --format '{{.Mountpoint}}'
docker run -d --name module5-selenoid --restart unless-stopped --label project=module5 -p 127.0.0.1:14445:4444 -e DOCKER_API_VERSION=1.44 -e "OVERRIDE_VIDEO_OUTPUT_DIR=$videoPath" -v /var/run/docker.sock:/var/run/docker.sock -v "${configPath}:/etc/selenoid:ro" -v module5-video:/opt/selenoid/video aerokube/selenoid:1.11.3 -limit 2 -timeout 2m -video-output-dir /opt/selenoid/video
if ($LASTEXITCODE -ne 0) { throw 'Cannot start Selenoid; inspect existing module5-selenoid container' }
