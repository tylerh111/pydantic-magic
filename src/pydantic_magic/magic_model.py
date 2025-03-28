"""Defines the Magic Underscore Pydantic Model."""

from __future__ import annotations

import itertools
from numbers import Number
from typing import TYPE_CHECKING, Any, Iterable, Literal, Mapping, Callable

from pydantic import BaseModel, model_validator


__all__ = [
    "MagicModel",
    "magic",
]


def _list_setdefault(data: list[Any], n: int, default: Any, miss: Any = None) -> Any:
    if n < len(data) and data[n] is not miss:
        return data[n]

    for _ in range(len(data), n+1):
        data.append(miss)

    data[n] = default
    return data[n]


def _magic_assign(
    data: dict[str, Any] | list[Any],
    path: list[str | int],
    val: Any,
):
    if len(path) == 0:
        raise ValueError("magic placement must have a path")

    # if not isinstance(path[0], str):
    #     raise TypeError("magic placement must start with a key, not an index")

    _next_container = lambda k: {} if isinstance(k, str) else []

    curr = data
    for key, keynext in itertools.pairwise(path):
        if isinstance(curr, dict):
            curr = curr.setdefault(key, _next_container(keynext))
        else:
            curr = _list_setdefault(curr, key, _next_container(keynext))

    curr[keynext] = val


def _magic_rec(
    __d: Any,
    /,
    *,
    cache: dict[str, Any],
    prefix: list[str] = None,
    sep: str = "_",
    maxsplit: int = -1,
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

        path = [
            int(key) if key.isdigit() else key
            for key in path
        ]

        _magic_assign(
            cache,
            path,
            val,
        )

        _magic_rec(
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
) -> dict[str, Any]:
    prefix = prefix or []
    prefix = ["_", *prefix]

    res = _magic_rec(
        __d,
        cache={},
        prefix=prefix,
        sep=sep,
        maxsplit=maxsplit,
    )

    return res["_"]


class MagicUnderscoreModel(BaseModel):
    """Magic Underscore Pydantic Model.

    Allows model validation via magic underscore syntax.
    """

    @model_validator(mode="before")
    @classmethod
    def magic_model_validator(cls, v: Any):
        print(f"::DEBUG:: {cls} | {type(v)} | {v}")
        return magic(v)
