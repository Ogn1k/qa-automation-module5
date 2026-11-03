# Модуль 5 — автоматизация Select Menu

Федорушкин Станислав, ПКТб-23-1. Объект: https://demoqa.com/select-menu.
Основание — 15 разных TC-SM модуля 4; `traceability.json` содержит соответствия.
Unit проверяет собственную учебную модель, API — дополнительный сервис Book Store.

## Установка

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python ci/install_dependencies.py
python -m playwright install chromium firefox
```

Установка использует закрепленный `requirements.lock.txt`, сначала зеркало GitVerse,
при его ошибке — явно указанный PyPI. Журнал: `results/dependency-install.json`.
`pip.ini` позволяет выбрать зеркало вручную через `PIP_CONFIG_FILE`.

## Тесты

```powershell
python -m pytest tests/unit tests/api tests/ui --cov=app --cov-branch --cov-report=json:results/coverage.json --junitxml=results/pytest.xml --alluredir=allure-results
python ci/check_coverage.py results/coverage.json
$env:BROWSER = 'firefox'
python -m pytest tests/ui --junitxml=results/firefox.xml --alluredir=allure-results
$env:BROWSER = 'chromium'
python -m behave --junit --junit-directory results/bdd -f allure_behave.formatter:AllureFormatter -o allure-results -f pretty
```

22 Unit, 6 API (включая создание/токен/авторизацию/чтение/удаление временного пользователя),
18 UI в Chromium, те же 18 в Firefox, 2 BDD. Повторы разных браузеров учитываются
как исполнения, а не дополнительные исходные тест-кейсы. API-пользователь удаляется в `finally`.
Секреты/токены не сохраняются в диагностических вложениях успешного сценария.

## Docker и Selenoid

В конфигурации Docker Engine требуется `registry-mirrors` из `docker-daemon.example.json`.
Существующие параметры следует сохранить; фактический результат проверить через
`docker info --format '{{json .RegistryConfig.Mirrors}}'`.
В Docker Desktop применяется настройка Docker Engine; перезапуск затрагивает контейнеры.

```powershell
docker pull aerokube/selenoid:1.11.3
docker pull selenoid/vnc_chrome:128.0
docker pull selenoid/vnc_firefox:125.0
docker pull selenoid/video-recorder:latest-release
.\selenoid\start.ps1
$env:SELENOID_URL = 'http://127.0.0.1:14445'
python -m pytest tests/selenoid -m selenoid --junitxml=results/selenoid.xml --alluredir=allure-results
```

Linux: `bash selenoid/start.sh`. Контейнер `module5-selenoid`, том `module5-video`,
порт 14445 только на localhost. Docker API version 1.44 обеспечивает совместимость с Docker 29.
Каждая из 10 WebDriver-проверок (5 × Chrome/Firefox) сохраняет PNG, DOM, метаданные сессии и MP4.
`enableVNC` включен; основной диагностический артефакт — видео.
Сохранение видео ожидается опросом HTTP, а не задержками для взаимодействия с UI.
После завершения работы: `docker stop module5-selenoid`; повторный запуск: `docker start module5-selenoid`.
Веб-интерфейс/VNC: `docker pull aerokube/selenoid-ui:1.10.11`, затем
`.\selenoid\start-ui.ps1` (Linux: `bash selenoid/start-ui.sh`). Адрес — http://127.0.0.1:14446.
Повторный запуск существующего интерфейса: `docker start module5-selenoid-ui`.

## История и метрики

Нужен Allure CLI 2.34.1 и Java. Команда выполняет три реальных сопоставимых регресса,
не смешивает сырые результаты разных запусков и переносит только `history`:

```powershell
python ci/run_regression.py --runs 3 --allure allure --selenoid-url http://127.0.0.1:14445
python -m http.server 8000 --bind 127.0.0.1 --directory regression/run-3/allure-report
```

Один полный запуск: 74 pytest-исполнения и 2 BDD = 76 результатов Allure.
Результаты, журналы, покрытие, видео, HTML: `regression/run-N/`.
`regression/runs.json` сохраняет время, статусы и хеш исходников.
Flaky Rate оценивается только по сопоставимым повторам и не гарантирует будущую стабильность.

CI: `.github/workflows/tests.yml`, push/PR/manual, отдельные Unit/API/Chromium/Firefox/BDD/Selenoid.
История берется из последнего артефакта `allure-history` той же ветки и сохраняется снова.
JUnit, диагностика, видео и HTML сохраняются артефактами даже после падения теста.
Предыдущий CI и локальные результаты от 30.10–02.11.2026 относятся к прошлой версии;
они не считаются подтверждением расширенного набора. Актуальные подтверждения — в итоговом отчете.
