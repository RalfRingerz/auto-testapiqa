"""Заглушка для анализатора типов (pyright / pylance)
  - подсказка для линтера, чтобы убрать ложные ошибки типов в allure"""

from collections.abc import Callable
from contextlib import AbstractContextManager
from enum import Enum
from typing import Any, TypeVar, overload

_F = TypeVar("_F", bound=Callable[..., Any])

@overload
def step(title: str, /) -> AbstractContextManager[None]: ...
@overload
def step(title: _F, /) -> _F: ...

def feature(*features: str) -> Callable[[_F], _F]: ...
def story(*stories: str) -> Callable[[_F], _F]: ...
def severity(*severities: str) -> Callable[[_F], _F]: ...

def attach(
    body: Any,
    name: str | None = ...,
    attachment_type: Enum | None = ...,
    extension: str | None = ...,
) -> None: ...

class attachment_type(Enum):
    PNG = ...
    TEXT = ...
