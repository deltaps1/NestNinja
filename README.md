# NestNinja

NestNinja is a library for quickly manipulating nested JSON data to "ready-to-go" database models. The api of NestNinja is easy and designed to be as much like Pandas as possible. 

## Main concepts
The main concept of NestNinja is the concept of "list of dictionaries". Whenever you have a list of dictionaries then NestNinja is applicable. This is a simple example: 

``` python3
list_of_dictionaries = [
    {"key1": "val1"},
    {"key2": "val2"},
    {"key3": "val3"}
]
```

NestNinja is a library for manipulating list of dictionaries easily. This is primarily done using the `Navigator` object. 

``` python3
from NestNinja import Navigator
list_of_dictionaries = [...] # Some random list of dictionaries
nav = Navigator(list_of_dictionaries)
```

**THIS LIBRARY IS VERY MUCH WORK IN PROCESS**
