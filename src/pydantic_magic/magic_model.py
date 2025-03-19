"""Defines the Pydantic `pint.Quantity`."""

from __future__ import annotations

import itertools
from numbers import Number
from typing import TYPE_CHECKING, Any, Iterable, Literal, Mapping, Callable

from pydantic import BaseModel, model_validator


__all__ = [
    "MagicModel",
    "magic",
]


def _magic_dict_assign(
    data: dict[str, Any],
    path: list[str],
    value: Any,
    *,
    default_factor: Callable[[], dict] = dict,
):
    if len(path) == 0:
        raise ValueError("magic placement must have a path")

    d_curr = data
    for key in itertools.islice(path, len(path) - 1):
        d_curr = d_curr.setdefault(key, default_factor())

    d_curr[path[-1]] = value


def _magic_with_cache(
    __d: Any,
    /,
    *,
    cache: dict[str, Any],
    prefix: list[str] = None,
    sep: str = "_",
    maxsplit: int = -1,
    default_factor: Callable[[], dict] = dict,
) -> dict[str, Any]:
    prefix = prefix or []

    if (
        not isinstance(__d, dict) or
        not all(isinstance(k, str) for k in __d)
    ):
        return __d

    d: dict[str, Any] = __d
    for key, val in d.items():
        path = [
            *prefix,
            *key.split(sep=sep, maxsplit=maxsplit),
        ]

        _magic_dict_assign(
            cache,
            path,
            val,
            default_factor=default_factor,
        )

        _magic_with_cache(
            val,
            cache=cache,
            prefix=path,
            sep=sep,
        )

    return cache


def magic(
    __d: dict[str, Any],
    /,
    *,
    prefix: list[str] = None,
    sep: str = "_",
    maxsplit: int = -1,
    default_factor: Callable[[], dict] = dict,
) -> dict[str, Any]:
    return _magic_with_cache(
        __d,
        cache={},
        prefix=prefix,
        sep=sep,
        maxsplit=maxsplit,
        default_factor=default_factor,
    )


class MagicModel(BaseModel):
    """Magic Pydantic Model.

    Allows model validation via magic underscore syntax.
    """

    @model_validator(mode="before")
    @classmethod
    def magic_model_validator(cls, v: Any):
        print(f"::DEBUG:: {cls} | {type(v)} | {v}")
        return magic(v)
