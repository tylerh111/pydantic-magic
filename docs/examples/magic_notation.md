# Magic Notation

!!! warning

    These are experimental utilities.
    See the warnings in [`magic_notation`][pydantic_magic.magic_notation].

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

!!! warning
    `MagicNotationModel` recursively and aggressively splits on `"_"`.
    Thus, it currently cannot handle fields that have underscores in the name.

    The following will not work with `MagicNotationModel`.

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
    #>   Field required [type=missing, input_value={'my': {'inner': {'my': {'field': 42}}}}, > input_type=dict]
    ```

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

