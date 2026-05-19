"""API тесты регистрации POST /api/signup 

Кейсы:
    test_signup_happy_path — smoke: уникальный signup_payload, id больше 0 и совпадение email
    test_signup_duplicate_email_rejected — regression: повторная регистрация - SignupConflictError с 400
Зависимости: PracticeApiClient, signup_payload из fixtures
"""

import pytest
import allure

from fixtures.api_client import PracticeApiClient, SignupConflictError
from fixtures.test_data import signup_payload


@allure.feature("API регистрация")
@allure.story("Успешная регистрация")
@allure.severity("blocker")
@pytest.mark.api
@pytest.mark.smoke
def test_signup_happy_path(api_client: PracticeApiClient):
    payload = signup_payload()
    with allure.step("POST /api/signup"):
        user = api_client.register(payload)
    assert user.email == payload["email"]
    assert user.id > 0


@allure.feature("API регистрация")
@allure.story("Дубликат email")
@pytest.mark.api
@pytest.mark.regression
def test_signup_duplicate_email_rejected(api_client: PracticeApiClient):
    payload = signup_payload()
    api_client.register(payload)
    with allure.step("Повторная регистрация на тот же email"):
        with pytest.raises(SignupConflictError) as exc:
            api_client.register(payload)
    assert exc.value.status_code == 400
