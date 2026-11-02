# Успешный CI после исправления — 02.11.2026

Запуск: https://github.com/Ogn1k/qa-automation-module5/actions/runs/41400186908
Коммит исправления: 5ea9f6dcaa7cbc896950c04f1e80ee628d477d42
Общий статус: success. Все задания success.
Unit 22/22, API 5/5, UI 18/18; 45 pytest passed, 0 failed, Pass Rate 100%.
BDD: 2 сценария, 8 шагов passed. Allure HTML сформирован.
Начало: 02.11.2026 11:29:09; завершение: 02.11.2026 11:30:23, Екатеринбург.

Исправлена причина падения: Login из методички отсутствует в текущем Swagger.
Негативный сценарий перенесен на POST /Account/v1/Authorized.
Проверяются HTTP 400, JSON Content-Type, code=1200 и сообщение обязательных полей.
Статус 200 не принимается. Skip/xfail/continue-on-error не применяются.
Контракт и объяснение: docs/API_FIX.md, docs/demoqa-swagger-2026-11-02.json.
Предыдущий неуспешный запуск сохранен в CI_RUN_2026-11-02.md как история.
