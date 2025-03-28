"""Magical Utilities for Pydantic."""

from __future__ import annotations

try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0"


__all__ = [
    "MagicNotationModel",
    "magic_notation",
    "pydantic_variant",
]


from .magic_notation_model import MagicNotationModel, magic_notation
from .variant_decorator import pydantic_variant
