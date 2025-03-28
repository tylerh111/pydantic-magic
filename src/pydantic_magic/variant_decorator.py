from __future__ import annotations

import inspect
from types import NoneType
from typing import Any, Annotated, ClassVar, Union, get_args, get_origin

from pydantic import RootModel


__all__ = [
    "pydantic_variant",
]


def pydantic_variant(
    __cls = None,
    /,
    annotations: list | Any | None = None,
) -> type | function:

    annotations = annotations if annotations is not None else []
    annotations = annotations if isinstance(annotations, list) else [annotations]

    def inject(__cls):

        def pydantic_variant_new(cls, *args, **kwargs):
            # use root model to instantiate the variant (union or annotated union)
            # alternatively, construct the super class of `cls` which will eventually hit the base class
            # the recursive base case is when it reach the abstract base model
            if cls is __cls:
                return RootModel[__cls.model_variant](*args, **kwargs).root
            return super(__cls, cls).__new__(cls, *args, **kwargs)

        @classmethod
        def pydantic_variant_init_subclass(cls, *args, **kwargs):

            # ignore abstract classes as they cannot be instantiated anyways
            if inspect.isabstract(cls):
                return super(cls).__init_subclass__(*args, **kwargs)

            # get variant keeps non-subclasse types from entering the variant
            # initially, the variant is None (or annotated None) which is removed initially
            # relies on union of one type collapse to that type
            # relies on union of unions to collapse to a single, flat union type
            def get_variant(alternatives):
                if alternatives and alternatives is not NoneType:
                    return Union[cls, alternatives]
                return Union[cls]

            if get_origin(__cls.model_variant) is Annotated:
                alternatives = get_args(__cls.model_variant)[0]
                variant = get_variant(alternatives)
                __cls.model_variant = Annotated[(variant, *annotations)]
            else:
                alternatives = get_args(__cls.model_variant)
                variant = get_variant(alternatives)
                __cls.model_variant = variant

            return super(cls).__init_subclass__(*args, **kwargs)

        __cls.__annotations__ = {"model_variant": ClassVar}
        __cls.__new__ = pydantic_variant_new
        __cls.__init_subclass__ = pydantic_variant_init_subclass

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
