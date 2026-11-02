# Исправление API-теста по актуальной Swagger-спецификации

Дата: 02.11.2026.
Источник: https://demoqa.com/swagger/swagger-ui-init.js (встроенный объект swaggerDoc).
UI спецификации: https://demoqa.com/swagger/.
Снимок контракта сохранен в demoqa-swagger-2026-11-02.json.

## Причина падения

Методический пример использует POST /Account/v1/Login с ожиданием HTTP 400.
В актуальной опубликованной спецификации пути /Account/v1/Login нет.
Для проверки авторизации документирован POST /Account/v1/Authorized:
при успехе 200 с boolean, ошибки представлены статусами 400/404 и MessageModal.
Поведение недокументированного Login не подтверждает корректную валидацию
учетных данных. Предыдущий CI действительно завершился failure на этом ожидании.

## Исправление

Вместо test_login_empty выполняется test_authorized_empty_credentials:
POST /Account/v1/Authorized, {"userName":"", "password":""}.
Проверяются HTTP 400, Content-Type application/json, code=1200 и сообщение
"UserName and Password required.". Этот ответ фактически получен при проверке.
Статус 200 не принимается как допустимый для пустых данных.
Skip, xfail, continue-on-error и подавление exit code не применяются.
Число API-вариантов осталось 5; Unit/UI/BDD не изменены.

Исправлен тестовый сценарий, а не сервер DemoQA. Негативная проверка авторизации
сохранена и перенесена на документированный endpoint. Успешный вход с валидными
данными не заявляется. Результат нового CI фиксируется отдельно после запуска.

## Подтвержденное завершение

Локально: 5 API passed за 8,36 с.
Удаленный полный запуск https://github.com/Ogn1k/qa-automation-module5/actions/runs/41400186908: success.
Unit 22/22, API 5/5, UI 18/18, BDD 2/2; Allure сформирован.
