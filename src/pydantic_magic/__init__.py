"""Pydantic validation for Magic Underscore Syntax."""

from __future__ import annotations

try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0"


__all__ = [
    "MagicModel",
    "magic",
]


from .magic_model import MagicModel, magic
