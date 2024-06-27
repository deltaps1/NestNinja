from typing import Any, Literal
from pprint import pprint

test_dict =[
    {'ids': 1, 'sub': [1, 2, 3]},                   # list of atomics
    {'ids': 2, 'sub': [{'c': 'd'}, {'e': 'f'}]},    # list of dicts
    {'ids': 3, 'sub': {'a': 'b'}},                  # Just a dict
    {'ids': 4, 'sub': 789},                         # Just an int
    {'ids': 5, 'sub': [                             # a list of lists with dicts
        [{'g': 'g'}, {'h': 'h'}], 
        [{'i': 'i'}, {'j': 'j'}]
    ]},
    {'ids': 6, 'sub': [[4, 5, 6], [7, 8, 9]]},      # a list of lists with atomics
    {'ids': 7}                                      # no values under `sub` key
]

def _add_parents_to_children(parent: dict, child: list|None = None):
    res = []

    # Early exit if `None`
    # `None` means that the key was not found in the list element in the 
    # `handle_list` function. In this case we just return the parent
    if child == None:
        res.append(parent)
        return res

    # We loop through the elements in the child, constructing new child
    # elements containing the parent element.
    for element in child:
        temp = {**parent, **element}
        res.append(temp)
    return res

def _handle_list_recursive(explosion_list: list):
    """This i minimal version of `handle_list` used for recursive calls"""
    res = []
    for list_element in explosion_list:
        if isinstance(list_element, list):
            to_append = _handle_list_recursive(list_element)
        elif isinstance(list_element, dict):
            to_append = [list_element]
        else:
            to_append = [{"_atomic": list_element}]
        res.append(to_append)
    res = [x for y in res for x in y]
    return res

def handle_list(explosion_list: list, key: str|Literal[False] = False) -> list[dict]:
    # We define a return object which will contain the results
    res = []

    # We now loop through the `explosion_list`
    for list_element in explosion_list:
        # First we check whether or not the provided key is in the individual 
        # `list_element`. If not we just append a dictionary only containing 
        # the parent element.
        sub = list_element.pop(key, None)

        # We now perform if/else checks to see if the type is a `list` or `dict`.
        # If the type is not one of these two, we assume that the data is 
        # atomic. If the key is not found we catch this in the first check.
        # If `to_append == None` then `_add_parents_to_children` cathces the case.
        if sub == None: 
            to_append = None
        elif isinstance(sub, list):
            # `_handle_list_recursive` is a minimal implementation of this 
            # function. The two functions are devided to make this function
            # more readable.
            to_append = _handle_list_recursive(sub)
        elif isinstance(sub, dict):
            #  We wrap result in a list to make the types of child elements 
            # consistent across all cases.
            to_append = [sub]
        else:
            # Same as above
            to_append = [{"_atomic": sub}]

        # We now defile the final object that we append to the return object
        to_append = {"parent": list_element, "child": to_append}
        res.append(to_append)

    # We run `_add_parents_to_children` to create new child elements containing
    # all the parent elements. 
    res = [_add_parents_to_children(**x) for x in res]
    # We flatten the list of lists. There will always be one level of nesting
    # and all items of the main list are more lists
    res = [x for y in res for x in y]
    return res

if __name__ == '__main__':
    res = handle_list(test_dict, key="sub")
    pprint(res)
