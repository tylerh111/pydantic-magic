# Pydantic Magic

[![_](https://img.shields.io/pypi/v/pydantic-magic)](https://pypi.python.org/pypi/pydantic-magic)
[![_](https://img.shields.io/pypi/pyversions/pydantic-magic)](https://github.com/tylerh111/pydantic-magic)
[![_](https://img.shields.io/pypi/l/pydantic-magic)](https://github.com/tylerh111/pydantic-magic/blob/main/LICENSE.md)
[![_](https://img.shields.io/readthedocs/pydantic-magic)](https://pydantic-magic.readthedocs.io)

---
[Pydantic Magic](https://pydantic-magic.readthedocs.io) is a collection of _magical_ utilities for [Pydantic](https://docs.pydantic.dev).
It is available as [`pydantic-magic`](https://pypi.python.org/pypi/pydantic-magic) on PyPI.

```shell
pip install pydantic-magic
```

### Magic Notation

The `pydantic_magic.MagicNotationModel` is a wrapper that allows users to instantiate Pydantic models via "magic" underscore notation (inspired by [Plotly](https://plotly.com)).
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

### Magic Variant

Pydantic can properly validate unions when they are part of a model, but there is no easy way to instantiate them or use them on their own.
Ideally, there would be a common base class from which all subclasses could be instantiated.
It would also be nice if it were possible to "extend" a union, as one could extend a class through inheritance.
The `pydantic_magic.magic_variant` takes smart unions to the next level in this regard.

<table>
<tr>
<th> Using smart unions </th>
<th> Using <code>pydantic_magic.magic_variant</code> </th>
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
# assert Fruit(name="cherry")  #> TypeError
assert Apple().name == "apple"
assert Orange().name == "orange"
# assert Cherry().name == "cherry"  #> NameError
```

</td>
<td>

```python
from typing import Literal
from pydantic import BaseModel, Field
from pydantic_magic import magic_variant

@magic_variant(annotations=Field(discriminator="name"))
class Fruit(BaseModel):
    name: str

class Apple(Fruit):
    name: Literal["apple"] = "apple"

class Orange(Fruit):
    name: Literal["orange"] = "orange"

# later on

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
