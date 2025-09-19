
import warnings
from typing import ClassVar, Any, Self, Literal
from pydantic import (
    BaseModel,
    ModelWrapValidatorHandler,
    SerializerFunctionWrapHandler,
    SerializationInfo,
    computed_field,
    model_validator,
    model_serializer,
)
from pydantic_core import PydanticCustomError

__all__ = [
    "MagicBaseModel",
]


_DEFAULT_MAGIC_DISCRIMINATOR = "magic"
_DEFAULT_MAGIC_SERIALIZATION = "short"



def magic_discriminator(cls: type) -> str:
    return cls.__qualname__


def _find_subcls(
    hierarchy: list[type[BaseModel]],
    name: str,
) -> type[BaseModel] | None:
    for subcls in hierarchy:
        if magic_discriminator(subcls) == name:
            return subcls

    return None


class MagicBaseModel(BaseModel):

    _magic_registry: ClassVar[set[str]] = set()
    _magic_discriminator: ClassVar[str] = _DEFAULT_MAGIC_DISCRIMINATOR
    _magic_serialization: ClassVar[Literal["long", "short"]] = _DEFAULT_MAGIC_SERIALIZATION

    def __init_subclass__(cls, **kwargs):
        name = magic_discriminator(cls)
        if name in MagicBaseModel._magic_registry:
            warnings.warn(f"magic model already registered: {name}")
        return super().__init_subclass__(**kwargs)

    @computed_field(repr=False)
    @property
    def magic(self) -> str:
        return magic_discriminator(type(self))

    @model_validator(mode="wrap")
    @classmethod
    def magic_validator(
        cls,
        value: Any,
        handler: ModelWrapValidatorHandler,
    ) -> Self:
        if cls is not MagicBaseModel or not isinstance(value, dict):
            return handler(value)

        if cls._magic_discriminator in value:
            magic_name = value[cls._magic_discriminator]
            magic_def = value
        elif len(value) == 1:
            magic_name, magic_def = next(iter(value.items()))
        else:
            raise PydanticCustomError(
                "pydantic-magic-base-model-missing-name",
                "missing magic name",
            )

        hierarchy = cls.__subclasses__()
        subcls = _find_subcls(hierarchy, magic_name)

        if subcls is None:
            raise PydanticCustomError(
                "pydantic-magic-base-model-unknown-name",
                "unknown magic name: '{name}'",
                {"name": magic_name}
            )

        model = subcls.model_validate(magic_def)
        return model

    @model_serializer(mode="wrap")
    def magic_serializer(
        self,
        handler: SerializerFunctionWrapHandler,
        info: SerializationInfo,
    ):
        dump = handler(self, info)
        if isinstance(dump, dict):
            dump.pop(self._magic_discriminator)

        if self._magic_serialization == "short" or not isinstance(dump, dict):
            return {
                self.magic: dump,
            }
        elif self._magic_serialization == "long":
            return {
                self._magic_discriminator: self.magic,
                **dump,
            }
        else:
            warnings.warn(f"unknown magic serialization mode: {self._magic_serialization}")

        return dump



