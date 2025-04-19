"""Magical Utilities for Pydantic."""

from __future__ import annotations

try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0"


__all__ = [
    "MagicNotationModel",
    "magic_notation",
    "magic_variant",
]


from ._magic_notation import MagicNotationModel, magic_notation
from ._magic_variant import magic_variant
