"""Download the newest previous Allure history artifact on this branch."""
import io
import json
import os
from pathlib import Path
import urllib.request
import urllib.parse
import zipfile

repository = os.environ['GITHUB_REPOSITORY']
branch = os.environ.get('GITHUB_HEAD_REF') or os.environ.get('GITHUB_REF_NAME')
headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'module5-allure-history',
           'Authorization': 'Bearer ' + os.environ['GITHUB_TOKEN']}
base = f'https://api.github.com/repos/{repository}'


class ArtifactRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, url):
        if urllib.parse.urlparse(url).scheme != 'https':
            raise RuntimeError('Artifact download redirected outside HTTPS')
        redirected = super().redirect_request(request, response, code, message, headers, url)
        if urllib.parse.urlparse(request.full_url).netloc != urllib.parse.urlparse(url).netloc:
            # Artifact storage uses a signed URL. A GitHub Bearer header both
            # leaks the credential across hosts and overrides its SAS auth.
            redirected.remove_header('Authorization')
        return redirected


opener = urllib.request.build_opener(ArtifactRedirect())


def get(url):
    with opener.open(urllib.request.Request(url, headers=headers), timeout=45) as response:
        return response.read()


artifacts = json.loads(get(base + '/actions/artifacts?name=allure-history&per_page=100'))['artifacts']
previous = [a for a in artifacts if not a['expired']
            and a.get('workflow_run', {}).get('head_branch') == branch
            and str(a.get('workflow_run', {}).get('id')) != os.environ.get('GITHUB_RUN_ID')]
if previous:
    artifact = max(previous, key=lambda a: a['created_at'])
    target = Path('previous-report/history')
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(get(artifact['archive_download_url']))) as archive:
        for name in archive.namelist():
            # History consists only of JSON files; never extract arbitrary paths.
            if Path(name).name == name and name.endswith('.json'):
                (target / name).write_bytes(archive.read(name))
    print('Restored Allure history from run', artifact['workflow_run']['id'])
else:
    print('First run on this branch: no previous history artifact')
