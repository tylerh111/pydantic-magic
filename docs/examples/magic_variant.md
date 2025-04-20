# Magic Variant

An abstract union class is an abstract class that reference all subclasses.
It itself cannot be instantiated, but it can instantiate any and all of its subclasses.
Unlike unions, they can be used as a normal class.

The `magic_variant` decorates an abstract class making it an abstract union class.
Any subclasses can take advantage of both pydantic's validation (and serialization) as well as be used in a polymorphic setting.
Using this design pattern, it allows the base class to be extended.

In the example below, a `Shape` class is the abstract union class.
This class is able to instantiate any of the concrete subclasses.

```python
import math
from abc import abstractmethod
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator
from pydantic_magic import magic_variant

@magic_variant(annotations=Field(discriminator="type"))
class Shape(BaseModel):
    type: str

    @abstractmethod
    def area(self) -> float: ...

class Polygon(Shape):
    type: Literal["polygon"] = "polygon"
    sides: int

class Quadralateral(Polygon):
    type: Literal["quadralateral"] = "quadralateral"
    sides: Literal[4] = 4

class Rectangle(Quadralateral):
    type: Literal["rectangle"] = "rectangle"
    length: float
    width: float

    def area(self) -> float:
        return self.length * self.width

class Square(Rectangle):
    type: Literal["square"] = "square"

    @model_validator(mode="before")
    def specify_one_length_width(cls, v: Any) -> Any:
        if not isinstance(v, dict):
            return v

        length = v.get("length")
        width = v.get("width")

        if length is not None:
            v["length"] = v["width"] = length
        elif width is not None:
            v["length"] = v["width"] = width
        else:
            raise ValueError("must specify one of 'length' or 'width'")

        return v

class Circle(Shape):
    type: Literal["circle"] = "circle"
    radius: float

    def area(self) -> float:
        return math.pi * self.radius**2


# Shape()
#> ValidationError: Unable to extract tag using discriminator 'type'

# Shape(type="unknown")
#> ValidationError: Discriminator 'unknown' does not match any expected tags: 'circle', 'square', 'rectangle'

# Shape(type="polygon")
#> ValidationError: Discriminator 'polygon' does not match any expected tags: 'circle', 'square', 'rectangle'

# Shape(type="rectangle")
#> ValidationError: Missing `rectangle.length` and `rectangle.width`

rectangle = Shape(type="rectangle", length=1.0, width=2.0)
assert type(rectangle) is Rectangle
assert isinstance(rectangle, Shape)
assert isinstance(rectangle, Polygon)
assert isinstance(rectangle, Rectangle)
assert not isinstance(rectangle, Square)
assert not isinstance(rectangle, Circle)
assert rectangle.area() == 2.0

square = Shape(type="square", length=1.0)
assert type(square) is Square
assert isinstance(square, Shape)
assert isinstance(square, Polygon)
assert isinstance(square, Rectangle)
assert isinstance(square, Square)
assert not isinstance(square, Circle)
assert square.area() == 1.0

circle = Shape(type="circle", radius=1.0)
assert type(circle) is Circle
assert isinstance(circle, Shape)
assert not isinstance(circle, Polygon)
assert not isinstance(circle, Rectangle)
assert not isinstance(circle, Square)
assert isinstance(circle, Circle)
assert round(circle.area(), 2) == 3.14
```

!!! warning
    `magic_variant` overwrites the `__new__` and `__init_subclass__` special member functions.
    It is currently not designed to work with models that implement these methods.
