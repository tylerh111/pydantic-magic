# Pydantic Magic

[![_](https://img.shields.io/pypi/v/pydantic-magic)](https://pypi.python.org/pypi/pydantic-magic)
[![_](https://img.shields.io/pypi/pyversions/pydantic-magic)](https://github.com/tylerh111/pydantic-magic)
[![_](https://img.shields.io/pypi/l/pydantic-magic)](https://github.com/tylerh111/pydantic-magic/blob/main/LICENSE.md)
[![_](https://img.shields.io/readthedocs/pydantic-magic)](https://pydantic-magic.readthedocs.io)

---

[Pydantic Magic](https://pydantic-magic.readthedocs.io) is a collection of _magical_ utilities for [Pydantic](https://docs.pydantic.dev).

### **`pydantic_magic.MagicNotationModel`**

`pydantic_magic.MagicNotationModel` is a wrapper that allows users to instantiate Pydantic models via "magic" underscore notation (as used by [Plotly](https://plotly.com/python/creating-and-updating-figures/#magic-underscore-notation)).
This class is wonderful for deeply nested classes.

<table>
<tr>
<th> Using <code>pydantic.BaseModel</code> </th>
<th> Using <code>pydantic_magic.MagicNotationModel</code> </th>
</tr>
<tr>
<td>

```python
from pydantic import BaseModel

class Font(BaseModel):
    name: str
    size: str

class TextBox(BaseModel):
    text: str
    font: Font

box = TextBox.model_validate({
    "text": "Pydantic is Awesome!",
    "font": {
        "name": "consolas",
        "size": "12pt",
    },
})

assert box.text == "Pydantic is Awesome!"
assert box.font.name == "consolas"
assert box.font.size == "12pt"
```

</td>
<td>

```python
from pydantic_magic import MagicNotationModel

class Font(MagicNotationModel):
    name: str
    size: str

class TextBox(MagicNotationModel):
    text: str
    font: Font

box = TextBox.model_validate({
    "text": "Pydantic is Awesome!",
    "font_name": "consolas",
    "font_size": "12pt",
})



assert box.text == "Pydantic is Awesome!"
assert box.font.name == "consolas"
assert box.font.size == "12pt"
```

</td>
</tr>
</table>

### **`pydantic_magic.pydantic_variant`**

Pydantic can properly validate unions when they are part of a model, but there is no easy way to instantiate them or use them on their own.
Ideally, there would be a common base class from which all subclasses could be instantiated.
It would also be nice if it were possible to "extend" a union, as one could extend a class through inheritance.
`pydantic_magic.pydantic_variant` takes smart unions to the next level.

<table>
<tr>
<th> Using smart unions </th>
<th> Using <code>pydantic_magic.pydantic_variant</code> </th>
</tr>
<tr>
<td>

```python
from typing import Annotated, Literal
from pydantic import BaseModel, Field

class Apple(BaseModel):
    name: Literal["apple"] = "apple"

class Orange(BaseModel):
    name: Literal["orange"] = "orange"

# must know all types before declaration
Fruit = Annotated[
    Apple | Orange,
    Field(discriminator="name"),
]


# cannot create `Cherry` class and have
# it participate in `Fruit` union

# assert Fruit(name="apple")  #> TypeError
# assert Fruit(name="orange")  #> TypeError
assert Apple().name == "apple"
assert Orange().name == "orange"
```

</td>
<td>

```python
from typing import Literal
from pydantic import BaseModel, Field
from pydantic_magic import pydantic_variant

@pydantic_variant(annotations=Field(discriminator="name"))
class Fruit(BaseModel):
    name: str

class Apple(Fruit):
    name: Literal["apple"] = "apple"

class Orange(Fruit):
    name: Literal["orange"] = "orange"

class Cherry(Fruit):
    name: Literal["cherry"] = "cherry"

assert isinstance(Fruit(name="apple"), Apple)
assert isinstance(Fruit(name="orange"), Orange)
assert isinstance(Fruit(name="cherry"), Cherry)
assert Apple().name == "apple"
assert Orange().name == "orange"
assert Cherry().name == "cherry"
```

</td>
</tr>
</table>

## Getting Started

### Installation

Pydantic Magic is available as [`pydantic-magic`](https://pypi.python.org/pypi/pydantic-magic) on PyPI.

```shell
pip install pydantic-magic
```

## Usage

### **`MagicNotationModel`**

Pydantic Magic provides the `MagicNotationModel` class that can replace `pydantic.BaseModel`.
Both standard validation and "magic" validation available.

```python
from pydantic_magic import MagicNotationModel

class Font(MagicNotationModel):
    name: str
    size: str

class TextBox(MagicNotationModel):
    text: str
    font: Font

box = TextBox.model_validate({
    "text": "Pydantic is Awesome!",
    "font_name": "consolas",
    "font_size": "12pt",
})
```

> [!WARNING]
> `MagicNotationModel` recursively and aggressively splits on `"_"`.
> Thus, it currently cannot handle fields that have underscores in the name.
>
> The following will not work with `MagicNotationModel`.
>
> ```python
> from pydantic_magic import MagicNotationModel
>
> class Inner(MagicNotationModel):
>     my_field: int
>
> class Outter(MagicNotationModel):
>     my_inner: Inner
>
> my_outter = Outter.model_validate({
>     "my_inner_my_field": 42,
> })
>
> #> ValidationError: 1 validation error for Outter
> #> my_inner
> #>   Field required [type=missing, input_value={'my': {'inner': {'my': {'field': 42}}}}, > input_type=dict]
> ```

### **`magic_notation`**

Under the hood, the `MagicNotationModel` uses a function called `magic_notation`.
It is the code that expands a dictionary of keys separated by an underscore into many dictionaries and lists.
The function could be useful for other applications and so it is exported from `pydantic_magic`.

```python
# magic with both
from pydantic_magic import magic_notation

todo = magic_notation({
    "0_todo": "Wake up",
    "1_todo": "Get shower",
    "2_todo": "Brush teeth",
})

print(todo)
#> [
#>     {'todo': 'Wake up'},
#>     {'todo': 'Get shower'},
#>     {'todo': 'Brush teeth'},
#> ]
```

### **`pydantic_variant`**

An abstract union class is an abstract class that reference all subclasses.
It itself cannot be instantiated, but it can instantiate any and all of its subclasses.
Unlike unions, they can be used as a normal class.

The `pydantic_variant` decorates an abstract class making it an abstract union class.
Any subclasses can take advantage of both pydantic's validation (and serialization) as well as be used in a polymorphic setting.
Using this design pattern, it allows the base class to be extended.

In the example below, a `Shape` class is the abstract union class.
This class is able to instantiate any of the concrete subclasses.

```python
import math
from abc import abstractmethod
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator
from pydantic_magic import pydantic_variant

@pydantic_variant(annotations=Field(discriminator="type"))
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

> [!WARNING]
> `pydantic_variant` overwrites the `__new__` and `__init_subclass__` special member functions.
> It is currently not designed to work with models that implement these methods.
