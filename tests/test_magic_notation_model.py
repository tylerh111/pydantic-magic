
import pytest
from pydantic import BaseModel, ValidationError, model_validator

from pydantic_magic import MagicNotationModel


def test_magic_notation_empty():

    class Test(MagicNotationModel):
        pass

    model = Test()
    assert model.model_dump() == {}


def test_magic_notation_flat():

    class Test(MagicNotationModel):
        foo: int

    value = {
        "foo": 0,
    }

    model = Test.model_validate(value)
    assert model.model_dump() == value

    class Test(MagicNotationModel):
        foo: int
        bar: int

    value = {
        "foo": 0,
        "bar": 0,
    }

    model = Test.model_validate(value)
    assert model.model_dump() == value


def test_magic_notation_layer_dict():

    class TestNested(BaseModel):
        bar: int

    class Test(MagicNotationModel):
        foo: TestNested

    value = {
        "foo_bar": 0,
    }

    expected = {
        "foo": {
            "bar": 0
        }
    }

    model = Test.model_validate(value)
    assert model.model_dump() == expected


def test_magic_notation_layer_list():

    class Test(MagicNotationModel):
        foo: list

    value = {
        "foo_0": 0,
    }

    expected = {
        "foo": [
            0,
        ]
    }

    model = Test.model_validate(value)
    assert model.model_dump() == expected


def test_magic_notation_layer_error():

    class Test(MagicNotationModel):
        foo: int

    value = {
        "foo": 0,
        "foo_bar": 0,
    }

    with pytest.raises(ValidationError):
        assert Test.model_validate(value)


def test_magic_notation_layer_model_validator():

    class TestNested(BaseModel):
        bar: int

        @model_validator(mode="before")
        def validate(cls, v):
            assert "bar" in v
            return v

    class Test(MagicNotationModel):
        foo: TestNested

        @model_validator(mode="before")
        def validate(cls, v):
            assert "foo" in v
            return v


    value = {
        "foo_bar": 0,
    }

    expected = {
        "foo": {
            "bar": 0
        }
    }

    model = Test.model_validate(value)
    assert model.model_dump() == expected

