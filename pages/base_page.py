"""Базовый Page Object для UI тестов Playwright sync API

Класс BasePage инкапсулирует общие действия:
    navigate — переход по относительному path (base_url из context)
    wait_for_selector — ожидание visible (таймаут из conftest: context.set_default_timeout)
    click_when_ready / fill_input — безопасный клик и ввод после ожидания элемента
Наследуют все page-классы в пакете pages/
"""

from playwright.sync_api import Page, Locator


class BasePage:
    def __init__(self, page: Page) -> None:
        self.page = page

    def navigate(self, path: str = "") -> None:
        self.page.goto(path)

    def wait_for_selector(self, selector: str) -> Locator:
        loc = self.page.locator(selector)
        loc.wait_for(state="visible")
        return loc

    def click_when_ready(self, selector: str) -> None:
        loc = self.wait_for_selector(selector)
        loc.click()

    def fill_input(self, selector: str, value: str) -> None:
        loc = self.wait_for_selector(selector)
        loc.fill(value)
