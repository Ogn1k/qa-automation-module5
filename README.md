# Модуль 5 — Select Menu, Федорушкин Станислав, ПКТб-23-1

Основание: готовый отчет модуля 4, раздел Widgets → Select Menu.
UI: 15 уникальных TC-SM (01–13, 15, 16), 18 исполняемых вариантов с четырьмя строками TC-SM-12.
Unit: собственная модель выбора из псевдокода модуля 4, не код DemoQA.
API: дополнительный Book Store API DemoQA; у Select Menu публичный серверный API не установлен.
API и Unit не выдаются за перенос TC-SM; связь UI с первоисточником — traceability.json.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
$env:PIP_CONFIG_FILE = "$PWD\pip.ini"
python -m pip install -r requirements.txt
python -m playwright install chromium
python -m pytest --cov=app --cov-branch --cov-report=json:results/coverage.json --cov-report=html:results/htmlcov --junitxml=results/pytest.xml --alluredir=allure-results
python -m behave --junit --junit-directory results/bdd
allure generate allure-results --clean -o allure-report
```

Edge: BROWSER_CHANNEL=msedge; Chrome: BROWSER_CHANNEL=chrome; другие движки: BROWSER=firefox (сначала установить).
По умолчанию Chromium headless, отдельный контекст 1912×966 CSS px, deviceScaleFactor=1.
При падении UI хук сохраняет PNG и DOM в Allure; отчет Word содержит только пометки и подписи.
Allure CLI устанавливается отдельно. HTML уже сформирован в allure-report:
`python -m http.server 8000 --bind 127.0.0.1 --directory allure-report` → http://127.0.0.1:8000.
Для истории скопировать allure-report/history в новые allure-results/history перед генерацией.
CI: GitHub Actions, файл `.github/workflows/tests.yml`. Docker/Selenoid не запускались.
Удаленный репозиторий: https://github.com/Ogn1k/qa-automation-module5.
Отдельные задания запускают Unit, API, UI и Behave; результаты JUnit и Allure
сохраняются даже при падении проверки. Подробности и снимки для отчета — `CI_GITHUB.md`.
docker-daemon.example.json — пример настройки зеркала, не доказательство работающего Docker.
Диагностические/предыдущие результаты Droppable в этот проект и итоговый Allure не включены.

## Подтвержденный прогон 30.10.2026

45 pytest-вариантов: 44 passed, 1 failed (Login: HTTP 200 вместо ожидаемого 400).
Unit 22/22, API 4/5, UI 18/18; 15 разных исходных TC-SM модуля 4.
Полный JUnit: results/pytest-final.xml; окружение: results/environment.json.
Behave: 2 passed, 8 steps passed; results/bdd-final/.
Итоговый Allure: allure-results-final/ и allure-report/.
Начальная диагностическая попытка исключена из сдаваемого архива.
