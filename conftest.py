"""Корневой conftest pytest: общая инфраструктура API и UI тестов.

Стенд по умолчанию: https://www.testapiqa.com (переопределяется через env)
Фикстуры:
    api_base_url / ui_base_url — базовые URL для REST и Playwright
    api_client - сессионный PracticeApiClient
    browser / page — Chromium в headless. для context задан set_default_timeout(PLAYWRIGHT_TIMEOUT)
    registered_account — изолированный пользователь (signup через API на каждый тест)
Хуки:
    pytest_runtest_makereport — при падении UIтеста прикрепляет скриншот и URL в Allure
"""

import os

import allure
import pytest
from playwright.sync_api import Browser, sync_playwright

from fixtures.api_client import PracticeApiClient
from fixtures.test_data import signup_payload

DEFAULT_BASE = "https://www.testapiqa.com"

# Единый таймаут на UI тесты для context: auto-waiting, actions, expect(). См. browser_context.set_default_timeout
PLAYWRIGHT_TIMEOUT = 10_000


@pytest.fixture(scope="session")
def api_base_url() -> str:
    return os.environ.get("TESTAPI_BASE_URL", DEFAULT_BASE).rstrip("/")


@pytest.fixture(scope="session")
def ui_base_url() -> str:
    return os.environ.get("TESTAPI_UI_BASE_URL", DEFAULT_BASE).rstrip("/")


@pytest.fixture(scope="session")
def api_client(api_base_url: str) -> PracticeApiClient:
    return PracticeApiClient(base_url=api_base_url, timeout=15)


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        yield browser
        browser.close()


@pytest.fixture
def page(browser: Browser, ui_base_url: str):
    """yield фикстура с teardown, после yield"""
    context = browser.new_context(base_url=ui_base_url)
    context.set_default_timeout(PLAYWRIGHT_TIMEOUT)
    page = context.new_page()
    yield page
    context.close()


@pytest.fixture
def registered_account(api_client: PracticeApiClient) -> dict[str, str]:
    """Новый пользователь на каждый тест для изоляции кейсов"""
    payload = signup_payload()
    api_client.register(payload)
    return {"email": payload["email"], "password": payload["password"]}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):  # noqa: ARG001
    """Allure attachment в failure делает скрин и URL страницы"""
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        page = item.funcargs.get("page")
        if page is not None:
            allure.attach(
                page.screenshot(),
                name="screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
            allure.attach(page.url, name="url", attachment_type=allure.attachment_type.TEXT)
