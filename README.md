# Pydantic Magic

[![_](https://img.shields.io/pypi/v/pydantic-magic)](https://pypi.python.org/pypi/pydantic-magic)
[![_](https://img.shields.io/pypi/pyversions/pydantic-magic)](https://github.com/tylerh111/pydantic-magic)
[![_](https://img.shields.io/pypi/l/pydantic-magic)](https://github.com/tylerh111/pydantic-magic/blob/main/LICENSE.md)
[![_](https://img.shields.io/readthedocs/pydantic-magic)](https://pydantic-magic.readthedocs.io)

---

[Pydantic Magic](https://pydantic-magic.readthedocs.io) is a collection of _magical_ utilities for [Pydantic](https://docs.pydantic.dev).


### **`pydantic_magic.MagicNotationModel`**

`pydantic_magic.MagicNotationModel` is a wrapper that allows users to instantiate [Pydantic](https://docs.pydantic.dev) models via "magic" underscore syntax (as used by [Plotly](https://plotly.com/python/creating-and-updating-figures/#magic-underscore-notation)).


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


## Getting Started

### Installation

Pydantic Magic is available as [`pydantic-magic`](https://pypi.python.org/pypi/pydantic-magic) on PyPI.

```shell
pip install pydantic-magic
```

## Usage

#### **`MagicNotationModel`**

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

```python
from pydantic_magic import MagicNotationModel

class Inner(MagicNotationModel):
    my_field: int

class Outter(MagicNotationModel):
    my_inner: Inner

my_outter = Outter.model_validate({
    "my_inner_my_field": 42,
})

#> ValidationError: 1 validation error for Outter
#> my_inner
#>   Field required [type=missing, input_value={'my': {'inner': {'my': {'field': 42}}}}, input_type=dict]
```

#### **`magic`**

Under the hood, the `MagicNotationModel` uses a function called `magic`.
It is the code that expands a dictionary of keys separated by an underscore into many dictionaries and lists.
The function could be useful for other applications and so it is exported from `pydantic_magic`.

```python
# magic with both
from pydantic_magic import magic

todo = magic({
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
