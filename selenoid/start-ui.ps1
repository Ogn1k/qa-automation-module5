$ErrorActionPreference = 'Stop'
docker network inspect module5-qa *> $null
if ($LASTEXITCODE -ne 0) { docker network create module5-qa }
$networks = docker inspect module5-selenoid --format '{{json .NetworkSettings.Networks}}' | ConvertFrom-Json
if (-not $networks.PSObject.Properties['module5-qa']) { docker network connect module5-qa module5-selenoid }
docker run -d --name module5-selenoid-ui --restart unless-stopped --network module5-qa --label project=module5 -p 127.0.0.1:14446:8080 aerokube/selenoid-ui:1.10.11 --selenoid-uri http://module5-selenoid:4444
if ($LASTEXITCODE -ne 0) { throw 'Cannot create UI; use docker start module5-selenoid-ui for an existing container' }
