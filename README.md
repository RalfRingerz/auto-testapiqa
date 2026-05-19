## pet-project автотестов на E-comm сайт testapiqa

Тестовый репо с pytest + Playwright: гоняю публичный стенд **https://www.testapiqa.com** (витрина + свой REST на том же домене). Задумка была взять реальный UI и реальные JSON ручки, а не моканный Flask backend, который ни с кем не синхронизирован.

API у площадки без нормальной открытой спеки, поэтому контракт собран по тому, что дергает фронт (`/api/signup`, `/api/login`, `/api/orders`). На это стоит ориентироваться, если что то поменяют на сайте, то тесты могут начать падать, и это нормально (т.к. это внешний сторонний SUT).

## Внутри:

- API: регистрация, логин, заказы (создать), список по email, удалить, плюс негативные кейсы. Клиент в `fixtures/api_client.py`, ответы валидируются через Pydantic. Тесты помечены `@pytest.mark.api` и `smoke` / `regression`.
- UI: логин и ошибка по кредам, страница `/signup`, поиск в каталоге, `/orders` — My Orders (гость vs логин), сценарии корзины (гость, добавление/удаление с выбором размера), один cross-layer — заказ через API, в браузере проверяется "My Orders". Page Objects: в том числе `CartPage`, `ProductPage`, `SignupPage`. Часть кейсов завязана на фикстуру `registered_account`, это отдельный пользователь через signup API на каждый тест
- Инфраструктура: в `pytest.ini` включены `--strict-markers` и маркеры `smoke`, `regression`, `api`, `ui`. В `conftest.py` общие URL (`TESTAPI_BASE_URL` / `TESTAPI_UI_BASE_URL`), сессионный `api_client`, Chromium + `page` с единым таймаутом контекста, хук на падение UI, в Allure уходит скрин и URL страницы. Для pyright в корне `pyrightconfig.json`, заглушки Allure `stubs/allure.pyi`

Стек: Python 3.11+ (локально у меня бывает и 3.13), pytest, pytest-xdist, requests, Playwright (в CI образ совпадает с `playwright==1.49.1`), Pydantic, allure-pytest, линтеры ruff и mypy. В CI зашит Python 3.11, см. `.gitlab-ci.yml`

## Структура каталогов:

```
pet-project/
├── README.md
├── requirements.txt
├── pytest.ini
├── pyrightconfig.json
├── conftest.py
├── .gitlab-ci.yml
├── stubs/
│   └── allure.pyi
├── pages/
│   ├── base_page.py
│   ├── login_page.py
│   ├── signup_page.py
│   ├── catalog_page.py
│   ├── product_page.py
│   ├── cart_page.py
│   └── orders_page.py
├── fixtures/
│   ├── api_client.py
│   └── test_data.py
└── tests/
    ├── api/
    │   ├── test_auth.py
    │   ├── test_registration.py
    │   ├── test_orders_crud.py
    │   └── test_orders_negative.py
    └── ui/
        ├── test_login.py
        ├── test_catalog_search.py
        ├── test_dashboard.py
        └── test_cart_flow.py
```

## Локальный запуск, основные команды

```bash
cd pet-project
python3 -m venv venv
source venv/bin/activate 
pip install -r requirements.txt
playwright install chromium

pytest -v --alluredir=allure-results
pytest tests/api/ -v
pytest tests/ui/ -v --headed

allure serve allure-results
rm -rf allure-results
```

Выборки по маркерам (как ориентир для CI): только smoke API `pytest tests/api/ -m "smoke"`, smoke UI `pytest tests/ui/ -m "smoke"`, полный API как в пайплайне `pytest tests/api/ -m "smoke or regression"`.

Параллельный прогон, если подключён pytest-xdist: `pytest -n 4`

По умолчанию база берётся из `conftest.py` (`https://www.testapiqa.com`). Если понадобится другой хост (например, зеркало), можно выставить переменные окружения `TESTAPI_BASE_URL` и при необходимости `TESTAPI_UI_BASE_URL` их читает `conftest.py`.

Allure после прогона: `allure serve allure-results` (для просмотра нужна установленная CLI allure). Очистка результатов отчёта: `rm -rf allure-results`.

В GitLab на ветке `master` джоба `pages` собирает статический Allure из артефактов `api-tests` и `ui-tests` и выкладывает как Pages (см. `.gitlab-ci.yml`).
# TODO поднять хост для крассивой презентации Allure отчёта / развернуть отчётность с историей прогонов  на GitHub Pages

## CI:

В GitLab: `ruff check .`, `mypy --ignore-missing-imports` по `pages/` и `fixtures/`. Отдельно API-джоба (`pytest tests/api/ … -m "smoke or regression"`) и UI на образе Playwright с установкой Chromium (`pytest tests/ui/ … -m "smoke"`). Артефакты с `allure-results`, генерация отчёта для Pages в том же файле.

## Возможные ограничения:

Публичный сайт: лимиты, сброс данных, внезапная смена вёрстки. Это может влиять на стабильность. Чисто для портфолио.

В `test_cart_flow.py` есть `xfail` на известное расхождение поведения кнопки "−" в корзине, если починят на стороне сайта, маркер придётся снять.
