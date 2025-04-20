
import pytest

from pydantic_magic import magic_notation


def test_magic_notation_empty():

    assert magic_notation({}) == {}


def test_magic_notation_flat():

    value = {
        "foo": 0,
    }

    assert magic_notation(value) == value

    value = {
        "foo": 0,
        "bar": 1
    }

    assert magic_notation(value) == value


def test_magic_notation_layer_dict():

    value = {
        "foo_bar": 0,
    }

    expected = {
        "foo": {
            "bar": 0
        }
    }

    assert magic_notation(value) == expected


def test_magic_notation_layer_list():

    value = {
        "foo_0": 0,
    }

    expected = {
        "foo": [
            0,
        ]
    }

    assert magic_notation(value) == expected


def test_magic_notation_layer_error():

    value = {
        "foo": 0,
        "foo_bar": 0,
    }

    with pytest.raises(ValueError):
        assert magic_notation(value)

