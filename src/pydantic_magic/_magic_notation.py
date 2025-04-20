"""The magic notation for pydantic models."""

from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

from pydantic import BaseModel, model_validator

if TYPE_CHECKING:
    from typing import Any
    from pydantic import ModelWrapValidatorHandler

    try:
        from typing import Self
    except ImportError:
        from typing_extensions import Self




__all__ = [
    "MagicNotationModel",
    "magic_notation",
]


def _list_setdefault(
    data: list[Any],
    n: int,
    default: Any,
    *,
    missing: Any = None,
) -> Any:
    if n < len(data) and data[n] is not missing:
        return data[n]

    for _ in range(len(data), n+1):
        data.append(missing)

    data[n] = default
    return data[n]


def _magic_notation_assign(
    data: dict[str, Any] | list[Any],
    path: list[str | int],
    val: Any,
    *,
    missing: Any = None,
):
    if len(path) == 0:
        raise ValueError("magic_notation: magic placement must have a path")

    # ensure the last path has `None` so the for loop works completely
    # note, the path always starts with `_` from `magic_notation`
    # because of this, `data` is always a dict
    path = [*path, None]

    # iterate over the path and create a dict or list depending on the next key
    # if `keynext` is a string, a new dictionary is created
    # if `keynext` is an int, a new list is create
    # `curr` is the container (dict / list) at each point in the path
    # `prev` will be the end container by the end (due to the extra `None` at the end of the path)
    # note, if a value (dict or list) is already in placed, then it is skipped
    _next_container = lambda k: {} if isinstance(k, str) else []
    curr = data
    for key, keynext in itertools.pairwise(path):
        prev = curr
        if isinstance(curr, dict):
            curr = curr.setdefault(key, _next_container(keynext))
        elif isinstance(curr, list):
            curr = _list_setdefault(curr, key, _next_container(keynext), missing=missing)
        else:
            raise ValueError(f"magic_notation: path has unexpected value type: {type(curr)}")

    if not isinstance(prev, (dict, list)):
        raise ValueError(f"magic_notation: value already as a value: {path[1:-1]} = {val}")

    prev[key] = val


def _magic_notation_rec(
    __d: Any,
    /,
    *,
    cache: dict[str, Any],
    prefix: list[str] = None,
    sep: str = "_",
    maxsplit: int = -1,
    missing: Any = None,
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

        _magic_notation_assign(
            cache,
            path,
            val,
            missing=missing,
        )

        _magic_notation_rec(
            val,
            cache=cache,
            prefix=path,
            sep=sep,
            missing=missing,
        )

    return cache


def magic_notation(
    __d: dict[str, Any],
    /,
    *,
    prefix: list[str] = None,
    sep: str = "_",
    maxsplit: int = -1,
    missing: Any = None,
) -> dict[str, Any]:
    """Magically expand a flat dictionary into a nested dictionary.

    The magic notation (inspired by [plotly](https://plotly.com/) magic underscores)
    expands a flat dictionary of keys separated by some token (e.g. underscores)
    into a nested dictionary. Complex dictionaries become very simple to read when
    in a flatten form.

    The input dict / list acts a tree, where each node is a new dict or list. A path
    is formed from the top level down to the leaf (the actual value). The keys
    represent the edges between nodes.

    !!! warning

        There are few limitations with the current implementation:

        * The input must be a dictionary.
        * The keys must be strings and indices must be int. No other type is allows.
        * Virtual containers, e.g. `Mapping` or `Sequence` from `collections.abc, are not
            supported, as they are not technically `dict` or `list`.
        * Sets and frozen sets are not supported as replacements for lists.

    Args:
        __d: The dictionary to expand.
        prefix: A prefix path instead of keys specified at the top level.
            Defaults to `None`.
        sep: Separator between keys (used by `str.split`).
            Defaults to "_".
        maxsplit: Max number of splits; in other words, the depth of the tree
            (used by `str.split`). Defaults to `-1`.
        missing: A filler for missing values in lists. Defaults to `None`.

    Returns:
        The magically expanded dictionary.
    """
    prefix = prefix or []
    prefix = ["", *prefix]

    res = _magic_notation_rec(
        __d,
        cache={},
        prefix=prefix,
        sep=sep,
        maxsplit=maxsplit,
        missing=missing,
    )

    return res.get("", res)


class MagicNotationModel(BaseModel):
    """Magic Underscore Pydantic Model.

    Allows model validation via magic underscore syntax.
    The magic notation is used in the validator for the model.
    See [`magic_notation`][pydantic_magic.magic_notation] for more information.

    !!! warning

        There are few limitations with the current implementation:

        * Magic notation expands all dictionaries, including dictionaries meant as fields.
            To be clear, a model that has a field of type `dict`, then that field will
            also be expanded out since `magic_notation` does not have field information.
        * Wrap validators will not be run in the correct order. Specifically, this class
            uses the "wrap" validator to prevent "before" validators from running out of
            order. See [ordering of validators](https://docs.pydantic.dev/latest/concepts/validators/#ordering-of-validators)
            for more information.
    """

    @model_validator(mode="wrap")
    @classmethod
    def magic_model_validator(
        cls,
        v: Any,
        handler: ModelWrapValidatorHandler[Self],
    ) -> Self:
        """Validate a dictionary with magic notation.

        Args:
            v: The value with which to instantiate model.
                Magic notation is only applied if it is of type `dict`.

        Returns:
            The value ready to continue with validation.
        """
        if isinstance(v, dict):
            v = magic_notation(v)
        return handler(v)
