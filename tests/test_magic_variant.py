
from abc import abstractmethod
from typing import Literal

import pytest
from pydantic import BaseModel, ValidationError, Field

from pydantic_magic import magic_variant


def test_magic_variant_empty():

    @magic_variant
    class Test(BaseModel):
        pass

    with pytest.raises(ValidationError):
        Test()


def test_magic_variant_annotated_empty():

    @magic_variant(annotations=Field(discriminator="name"))
    class Test(BaseModel):
        pass

    with pytest.raises(ValidationError):
        Test()


def test_magic_variant_one_alternative():

    @magic_variant
    class Test(BaseModel):
        pass

    class TestAlternate(Test):
        foo: int

    value = { "foo": 0 }
    expected = TestAlternate.model_validate(value)
    model = Test(**value)
    assert model == expected


def test_magic_variant_multiple_alternative():

    @magic_variant
    class Test(BaseModel):
        pass

    class TestAlternate1(Test):
        foo: int

    class TestAlternate2(Test):
        bar: int

    value = { "foo": 0 }
    expected = TestAlternate1.model_validate(value)
    model = Test(**value)
    assert model == expected

    value = { "bar": 0 }
    expected = TestAlternate2.model_validate(value)
    model = Test(**value)
    assert model == expected


def test_magic_variant_annotated_multiple_alternative():

    @magic_variant(annotations=Field(discriminator="name"))
    class Test(BaseModel):
        pass

    class TestAlternate1(Test):
        name: Literal["alt_1"] = "alt_1"
        foo: int

    class TestAlternate2(Test):
        name: Literal["alt_2"] = "alt_2"
        bar: int

    value = { "name": "alt_1", "foo": 0 }
    expected = TestAlternate1.model_validate(value)
    model = Test(**value)
    assert model == expected

    value = { "name": "alt_2", "bar": 0 }
    expected = TestAlternate2.model_validate(value)
    model = Test(**value)
    assert model == expected

    with pytest.raises(ValidationError):
        Test(name="alt_0")


def test_magic_variant_abstract():

    @magic_variant(annotations=Field(discriminator="name"))
    class Test(BaseModel):

        @abstractmethod
        def test(self): ...

    class TestAlternate1(Test):
        name: Literal["alt_1"] = "alt_1"
        foo: int

        def test(self):
            assert self.name == "alt_1"
            return self.name

    class TestAlternate2(Test):
        name: Literal["alt_2"] = "alt_2"
        bar: int

        def test(self):
            assert self.name == "alt_2"
            return self.name

    class TestAlternative3(Test):
        name: Literal["alt_3"] = "alt_3"
        baz: int


    value = { "name": "alt_1", "foo": 0 }
    expected = TestAlternate1.model_validate(value)
    model = Test(**value)
    assert model == expected
    assert model.test() == "alt_1"

    value = { "name": "alt_2", "bar": 0 }
    expected = TestAlternate2.model_validate(value)
    model = Test(**value)
    assert model == expected
    assert model.test() == "alt_2"

    with pytest.raises(TypeError):
        TestAlternative3()


def test_magic_variant_annotated_abstract():

    @magic_variant(annotations=Field(discriminator="name"))
    class Test(BaseModel):

        @abstractmethod
        def test(self): ...

    class TestAlternate1(Test):
        name: Literal["alt_1"] = "alt_1"
        foo: int

        def test(self):
            assert self.name == "alt_1"
            return self.name

    class TestAlternate2(Test):
        name: Literal["alt_2"] = "alt_2"
        bar: int

        def test(self):
            assert self.name == "alt_2"
            return self.name

    class TestAlternative3(Test):
        name: Literal["alt_3"] = "alt_3"
        baz: int


    value = { "name": "alt_1", "foo": 0 }
    expected = TestAlternate1.model_validate(value)
    model = Test(**value)
    assert model == expected
    assert model.test() == "alt_1"

    value = { "name": "alt_2", "bar": 0 }
    expected = TestAlternate2.model_validate(value)
    model = Test(**value)
    assert model == expected
    assert model.test() == "alt_2"

    with pytest.raises(TypeError):
        TestAlternative3()



