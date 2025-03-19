# Pydantic Magic

[![_](https://img.shields.io/pypi/v/pydantic-magic)](https://pypi.python.org/pypi/pydantic-magic)
[![_](https://img.shields.io/pypi/pyversions/pydantic-magic)](https://github.com/tylerh111/pydantic-magic)
[![_](https://img.shields.io/pypi/l/pydantic-magic)](https://github.com/tylerh111/pydantic-magic/blob/main/LICENSE.md)
[![_](https://img.shields.io/readthedocs/pydantic-magic)](https://pydantic-magic.readthedocs.io)

---

[Pydantic Magic](https://pydantic-magic.readthedocs.io) provides a wrapper model (called `MagicModel`) that allows users to instantiate [Pydantic](https://docs.pydantic.dev) models via "magic" underscore syntax (as used by [Plotly](https://plotly.com/python/creating-and-updating-figures/#magic-underscore-notation)).


<table>
<tr>
<th> Using <code>pydantic.BaseModel</code> </th>
<th> Using <code>pydantic_magic.MagicModel</code> </th>
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
from pydantic import BaseModel

class Font(BaseModel):
    name: str
    size: str

class TextBox(BaseModel):
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

### Usage

#### **`MagicModel`**

Pydantic Magic provides the `MagicModel` class that can replace `pydantic.BaseModel`.
Both standard validation and "magic" validation available.

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
    "font_name": "consolas",
    "font_size": "12pt",
})
```

> [!WARNING]
> `MagicModel` recursively and aggressively splits on `"_"`.
> Thus, it currently cannot handle fields that have underscores in the name.
>
> The following will not work with `MagicModel`.

```python
from pydantic_magic import MagicModel

class Inner(MagicModel):
    my_field: int

class Outter(MagicModel):
    my_inner: Inner

my_outter = Outter.model_validate({
    "my_inner_my_field": 42,
})

#> ValidationError: 1 validation error for Outter
#> my_inner
#>   Field required [type=missing, input_value={'my': {'inner': {'my': {'field': 42}}}}, input_type=dict]
```

#### **`magic`**

Under the hood, the `MagicModel` uses a function called `magic`.
It is the code that expands a dictionary of keys separated by an underscore into many dictionaries and lists.
The function could be useful for other applications and so it is exported from `pydantic_magic`.

```python
# magic with dictionaries
from pydantic_magic import magic

matrix = magic({
    "a_a_a": 0, "a_a_b": 10, "a_a_c": 100,
    "a_b_a": 1, "a_b_b": 11, "a_b_c": 101,
    "a_c_a": 2, "a_c_b": 12, "a_c_c": 102,
    "b_a_a": 3, "b_a_b": 13, "b_a_c": 103,
    "b_b_a": 4, "b_b_b": 14, "b_b_c": 104,
    "c_a_a": 5, "c_a_b": 15, "c_a_c": 105,
})

print(matrix)
#> {
#>     'a': {
#>         'a': {'a': 0, 'b': 10, 'c': 100},
#>         'b': {'a': 1, 'b': 11, 'c': 101},
#>         'c': {'a': 2, 'b': 12, 'c': 102},
#>     },
#>     'b': {
#>         'a': {'a': 3, 'b': 13, 'c': 103},
#>         'b': {'a': 4, 'b': 14, 'c': 104},
#>     },
#>     'c': {
#>         'a': {'a': 5, 'b': 15, 'c': 105},
#>     },
#> }
```

```python
# magic with lists
from pydantic_magic import magic

coords = magic({
    "0_0": 39.90609119839383,
    "0_1": -75.16645922575229,
    "1_0": 33.527613173438304,
    "1_0": -112.26256811654625,
})

print(coords)
#> [
#>     [39.90609119839383, -75.16645922575229],
#>     [33.527613173438304, -112.26256811654625],
#> ]
```

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

## Example

#### **`MagicModel`**

Below is a comprehensive example of instantiating a class that has inheritance, nesting, and aggregation (lists) with magic underscore syntax.

```python
from pydantic_magic import MagicModel

class Position(MagicModel):
    x: float
    y: float

class Size(MagicModel):
    width: float
    height: float

class Color(MagicModel):
    r: float
    b: float
    g: float
    a: float  # alpha

class Widget(MagicModel):
    pos: Position
    size: Size

class TextWidget(MagicModel):
    type: str
    text: str = ""
    font: str
    size: str
    color: Color
    bgcolor: Color
    bold: bool = False
    underline: bool = False
    strikethrough: bool = False

class TextBoxWidget(Text):
    pass

class Layout(MagicModel):
    widgets: list[Widget]

Layout.model_validate({
    "widgets_0_pos_x": 0,
    "widgets_0_pos_y": 0,
    "widgets_0_size_width": 100,
    "widgets_0_size_height": 20,
    "widgets_0_type": "text",
    "widgets_0_text": "Hello",
    "widgets_0_font": "consolas",
    "widgets_0_size": "12pt",
    "widgets_0_color_r": 0,
    "widgets_0_color_b": 0,
    "widgets_0_color_g": 0,
    "widgets_0_color_a": 100,
    "widgets_0_bgcolor_r": 255,
    "widgets_0_bgcolor_b": 255,
    "widgets_0_bgcolor_g": 255,
    "widgets_0_bgcolor_a": 0,
    "widgets_0_bold": True,
    "widgets_1_pos_x": 110,
    "widgets_1_pos_y": 0,
    "widgets_1_size_width": 100,
    "widgets_1_size_height": 20,
    "widgets_1_type": "text",
    "widgets_1_text": "Hello",
    "widgets_1_font": "consolas",
    "widgets_1_size": "12pt",
    "widgets_1_color_r": 36,
    "widgets_1_color_b": 36,
    "widgets_1_color_g": 209,
    "widgets_1_color_a": 100,
    "widgets_1_bgcolor_r": 255,
    "widgets_1_bgcolor_b": 255,
    "widgets_1_bgcolor_g": 255,
    "widgets_1_bgcolor_a": 0,
    "widgets_1_underline": True,
})

```

#### `magic`

Below is a comprehensive example of using `magic` to apply "magic" syntax to a dictionary.

```python
from pydantic_magic import magic

magic({
    "maps_beavercreek_name": "Battle Creek",
    "maps_beavercreek_location": "Installation 04",
    "maps_beavercreek_terrain": "Canyon with two Forerunner bases",
    "maps_beavercreek_layout": "semi-symmetrical",
    "maps_beavercreek_players_min": 2,
    "maps_beavercreek_players_max": 8,
    "maps_beavercreek_teams": True,
    "maps_beavercreek_gamemodes": [
        "slayer",
        "capture_the_flag",
        "king_of_the_hill",
        "oddball",
    ],
    "maps_bloodgulch_name": "Blood Gulch",
    "maps_bloodgulch_location": "Installation 04",
    "maps_bloodgulch_terrain": "Desert/Canyon",
    "maps_bloodgulch_layout": "semi-symmetrical",
    "maps_bloodgulch_players_min": 4,
    "maps_bloodgulch_players_max": 16,
    "maps_bloodgulch_teams": True,
    "maps_bloodgulch_gamemodes": [
        "slayer",
        "capture_the_flag",
    ],
    "gamemodes_0_type": "slayer",
    "gamemodes_0_name": "Elimination",
    "gamemodes_0_teams": False,
    "gamemodes_0_lives": 1,
    "gamemodes_0_health": 1.0,
    "gamemodes_0_shields": True,
    "gamemodes_0_respawn": 0,
    "gamemodes_1_type": "ctf",
    "gamemodes_1_name": "Capture the Flag",
    "gamemodes_1_teams": True,
    "gamemodes_1_lives": float("inf"),
    "gamemodes_1_health": 1.0,
    "gamemodes_1_shields": True,
    "gamemodes_1_respawn": 5,
})
```
