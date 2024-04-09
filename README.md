# NestNinja

NestNinja is a library for quickly manipulating nested JSON data to "ready-to-go" database models. The api of NestNinja is easy and designed to be as much like Pandas as possible. 

## Main concepts
The main concept of NestNinja is the concept of "list of dictionaries". Whenever you have a list of dictionaries then NestNinja is applicable. This is a simple example: 

``` python3
list_of_dictionaries = [
    {"key": "val1"},
    {"key": "val2"},
    {"key": "val3"}
]
```

The example above has a "flat" layout and is pretty easy to deal with using existing data wrangling tools like pandas. For example we can pretty easily read the list of dictionaries using the method `pandas.DataFrame.from_dict()`. 

However, when you have nested JSON/dictionary structures it often poses a challenge - specially when these structures are deeply nested. In simple cases pandas can handle these cases out of the box. Let's take the following example: 

```python3
>>> import pandas as pd
>>> dictionary = {
...    "key": {
...        "subkey": [
...            {"subsubkey": 1},
...            {"subsubkey": 2},
...            {"subsubkey": 3}
...        ]
...    }
... }
>>> list_of_dictionaries = [dictionary for x in range(10_000)
>>> pd.DataFrame.from_dict(list_of_dictionaries).tail()
                                                    key
9995  {'subkey': [{'subsubkey': 1}, {'subsubkey': 2}...
9996  {'subkey': [{'subsubkey': 1}, {'subsubkey': 2}...
9997  {'subkey': [{'subsubkey': 1}, {'subsubkey': 2}...
9998  {'subkey': [{'subsubkey': 1}, {'subsubkey': 2}...
9999  {'subkey': [{'subsubkey': 1}, {'subsubkey': 2}...
```

In the above example pandas only handles the first key and all of the underlying dictionary just becomes a cell value in the dictionary. This challenge could easily be overcomed by manipulation the `list_of_dictionary` object before sending it to `pandas.DataFrame.from_dict`.

However, when the nesting of the JSON structure becomes very deep and complex or the number of fields in the objects makes the task of writing loops for cleaning the structure very tedious, what do we do then? 

**We use NestNinja to ease our struggles!**


## Ussage
NestNinja is a library for manipulating list of dictionaries easily. This is primarily done using the `Navigator` object. 

``` python3
from NestNinja import Navigator
list_of_dictionaries = [...] # Some random list of dictionaries
nav = Navigator(list_of_dictionaries)
```

**THIS LIBRARY IS VERY MUCH WORK IN PROCESS**
