"""The magic variant decorator for creating abstract union classes."""

from __future__ import annotations

import inspect
import logging
from types import NoneType
from typing import Any, Annotated, ClassVar, Literal, Union, get_args, get_origin

from pydantic import RootModel, BaseModel, Discriminator
from pydantic.fields import FieldInfo


__all__ = [
    "magic_variant",
]


def _variant_prepend_new_type(cls, alternatives):
    # keep non-subclass types from entering the variant
    # initially, the variant is None (or annotated None) which is removed initially
    # relies on union of one type collapse to that type
    # relies on union of unions to collapse to a single, flat union type
    if alternatives and alternatives is not NoneType:
        return Union[cls, alternatives]
    return Union[cls]


def magic_variant(
    __cls: type[BaseModel] | None = None,
    /,
    annotations: list | Any | None = None,
) -> BaseModel | function:
    """Magically decorate an pydantic model to make it an abstract union class.

    An abstract union class is a design pattern where the abstract base class
    can instantiate any of its concrete derived members. Derived classes that
    are abstract or do not have a discriminator (if one is specified), it will
    be ignored.

    The union that contains the alternatives for the abstract union class are
    stored in the class variable `model_variant`. If annotations are provided,
    it will be of type `Annotated` instead of `Union`. If there is only one
    concrete derived class, then it will that type (with annotations). If there
    are no concrete derived classes, then it will be `None` (or annotated `None`).

    !!! warning
        There are a few limitations with the current implementation.

        * The `pydantic.Discriminator` annotation is not supported.
        * The decorator redefines `__new__` and `__init_subclasses__`.
        * The base model cannot be instantiated with `model_validate`.
        * Base classes that are not abstract nor discrimatory cannot be instantiated
            as they do not themself participate in the variant.

    Args:
        __cls: The class to inject with magic variant functions. Defaults to None.
        annotations: Annotations to include on the union base type.
            it is recommended to use discriminators. Defaults to None.

    Raises:
        TypeError: Annotations contain a functional discriminator.

    Returns:
        The Pydantic abstract union class.
    """

    annotations = annotations if annotations is not None else []
    annotations = annotations if isinstance(annotations, list) else [annotations]

    # find discriminator field in the annotation
    # classes that do not have the discriminator field will be considered "abstract"
    # only considering static discriminators (no `pydantic.Discriminator`)
    # also only considering first annotation that is a `pydantic.fields.FieldInfo`
    discriminator = next((a for a in annotations if isinstance(a, FieldInfo)), None)
    discriminator = discriminator.discriminator if discriminator is not None else None
    if isinstance(discriminator, Discriminator):
        raise TypeError("magic_variant: functional discriminators are not supported")

    def inject(__cls: type[BaseModel]) -> BaseModel:

        def magic_variant_new(cls: type[BaseModel], *args, **kwargs):
            # use root model to instantiate the variant (union or annotated union)
            # alternatively, recursive call the super class constructo of `cls`
            # the recursive base case is when it reach the abstract union class constructor
            if cls is __cls:
                return RootModel[__cls.model_variant](*args, **kwargs).root
            return super(__cls, cls).__new__(cls, *args, **kwargs)

        @classmethod
        def magic_variant_init_subclass(cls: type[BaseModel], *args, **kwargs):

            # ignore abstract classes as they cannot be instantiated anyways
            if inspect.isabstract(cls):
                logging.debug(f"magic_variant: skipping {cls} - class is abstract")
                return super(cls).__init_subclass__(*args, **kwargs)

            # ignore classes that do not have the discriminator field
            # note, this check is skipped when no discriminator is provided
            if (
                discriminator is not None
                and get_origin(cls.__annotations__.get(discriminator)) is not Literal
            ):
                logging.debug(f"magic_variant: skipping {cls} - class has no discriminator field")
                return super(cls).__init_subclass__(*args, **kwargs)

            logging.debug(f"magic_variant: registering new class for {__cls} - {cls}")

            # class is approved for participation in the model variant
            # most of this code is ensuring class is added to the model variant correctly
            if get_origin(__cls.model_variant) is Annotated:
                alternatives = get_args(__cls.model_variant)[0]
                variant = _variant_prepend_new_type(cls, alternatives)
                __cls.model_variant = Annotated[(variant, *annotations)]
            elif get_origin(__cls.model_variant) is Union:
                variant = _variant_prepend_new_type(cls, __cls.model_variant)
                __cls.model_variant = variant
            else:
                alternatives = __cls.model_variant
                variant = _variant_prepend_new_type(cls, alternatives)
                __cls.model_variant = variant

            return super(cls).__init_subclass__(*args, **kwargs)

        # !!!WARNING!!!
        # overriding `__new__` and `__init_subclass__`
        # the decorator must override the instantiation methods to inject the new variant code
        # a possible fix for this is to call the original methods
        # however, a custom `__new__` and `__init_subclass__` loses meaning at the abstract level
        # temporary solution is to decorate a more abstract class instead
        __cls.__annotations__["model_variant"] = ClassVar
        __cls.__new__ = magic_variant_new
        __cls.__init_subclass__ = magic_variant_init_subclass

        # note, this decorator cannot instantiate the base class, so it must be abstract
        # this is due to need root model to validate the variant in the base case
        # we purposefully leave out the base class in the variant to prevent this
        # alternatives will only ever have subclasses of `__cls` (and `NoneType`)
        if annotations:
            __cls.model_variant = Annotated[(None, *annotations)]
        else:
            __cls.model_variant = None

        return __cls

    if __cls is None:
        return inject

    return inject(__cls)
