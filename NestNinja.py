from __future__ import annotations
from typing import Any, Callable, DefaultDict, Literal
from test_utils import get_test_data
from pprint import pprint
from explosion import handle_list
import copy


class Navigator:
    def __init__(
            self,
            data: list | dict,
            index_name: str = '',
            _debug_msg: str = '',
            _prevent_index_creation: bool = False,
            _parent_obj: Navigator | bool = False
        ):
        if _debug_msg:
            print(f"Navigator initialised. Message: {_debug_msg}")
            print(f"Index name: {index_name}")

        self.data: list = _put_dicts_in_lists(data)
        self.index_name = index_name
        # If a index name is provided then that should be the default.
        if index_name: 
            self.index_name = index_name
        # TODO: Why should it be allowed to not do anything?
        elif _prevent_index_creation: ... # Don't do anything
        else: 
            self.index_name = "_idx"
            self.create_index()

        self.parent_obj = _parent_obj
        
    def _looper(
            self, 
            func: Callable, 
            post_call: Callable | Literal[False] = False,
            include_errors: bool = True,
            navigator_kwargs: dict = {}
        ) -> Navigator:
        """The looper function takes a callable that accepts a subvalue and loops through 
        all objects in the main list defined in self.data. This is very similar to `map`. 
        However `self._looper` also handles errors and instantiates a new `Navigator` object
        with a list of the results from the provided callable.

        TODO: Rewrite the error handler to make it more versatile.
        TODO: Make a more easy to understand description (the concept is somewhat hard to explain).
        """
        data: list = [x for x in self.data]
        result = []
        for datum in data:
            try: result.append(func(datum))
            except Exception as error: 
                if include_errors:
                    datum.setdefault("_error", [])
                    datum["_error"].append(_error_handler(error, func))
                    result.append(datum)
        if post_call: 
            result = post_call(result)
        navigator_kwargs = {
            **{"_parent_obj": self.parent_obj},
            **navigator_kwargs
        }
        return Navigator(result, **navigator_kwargs)

    def set_index(self, index_name: str, keep_old: bool = True):
        """Sets a new index key and deletes the old if `keep_old = False`"""
        if not keep_old:
            res = self.delete(key=self.index_name, _index_name=index_name)
            res.index_name = index_name
        else: res = Navigator(self.data, index_name=index_name)
        return res

    def create_index(self):
        """Creates an index by enumerating over the list of dictionaries
        TODO: Is this really just a number? That seems weird...
        """
        for i, datum in enumerate(self.data):
            datum[self.index_name] = i

    def promote(self, key: str, prefix: str = "", delete: bool = True) -> Navigator:
        """Promotion is when values from a subdict is lifted up one level.
        A prefix can be used to provide context to the key which stored the key previously.
        TODO: Test deletion keyword
        """
        def promote_inner(datum: dict):
            res = {k:v for k, v in datum.items()}
            if delete: del(res[key])
            for k, v in datum[key].items(): res[prefix + k] = v
            return res

        navigator_kwargs = {}
        navigator_kwargs["index_name"] = self.index_name
        return self._looper(
            promote_inner, 
            navigator_kwargs=navigator_kwargs
        ) 

    def demote(
        self, 
        demoted_key: str, 
        demotion_location: str, 
        delete: bool = True,
        _parent_obj = False
    ) -> Navigator: 
        """Demotion is when a key-value pair is put into a subdict."""
        def demote_inner(datum: dict): 
            # datum = {k: v for k, v in datum.items()}
            # Why do I do this?
            demotion_data = _put_dicts_in_lists(datum[demotion_location])
            res = []
            for demotion_sub in demotion_data:
                res_data = {k:v for k,v in demotion_sub.items()}
                res_data[demoted_key] = datum[demoted_key]
                res.append(res_data)
            datum[demotion_location] = res
            if delete: del(datum[demoted_key])
            return datum

        # post_call = lambda result: [x for y in result for x in y]
        temp = self.copy()
        if _parent_obj:
            navigator_kwargs = {"_parent_obj": self}
        else: navigator_kwargs = {}
        return temp._looper(demote_inner, navigator_kwargs=navigator_kwargs) # post_call=post_call) 

    def rename(self, old_name: str, new_name: str) -> Navigator | list:
        """Renames a key"""
        def rename_inner(datum: dict):
            datum[new_name] = datum[old_name]
            del(datum[old_name])
            return datum
        temp = self.copy()
        return temp._looper(rename_inner)

    def split(self, key: str, func: Callable) -> Navigator | list:
        """
        TODO: This doesn't work and it's not good and intuitive. Maybe more `pd.DataFrame.assign`-like?
        """
        def split_inner(datum: dict):
            eval_res = func(datum[key]) # Check if the function is True
            new_key = key + ("_true" if eval_res else "_false")
            datum[new_key] = datum[key]
            return datum 
        return self._looper(split_inner)

    def nav(self, key: str, index_name: str = '', 
            _prevent_index_creation: bool = False) -> Navigator:
        """Navigates to a a subkey and creates a new `Navigator` instance.
        It's only posible to navigate to subkeys were the related subvalue is a list or a dict. 
        """
        def nav_inner(datum: dict): 
            subdata = datum[key] 
            if isinstance(subdata, dict): subdata = [subdata]
            elif isinstance(subdata, list): ... # Do nothing
            else: raise TypeError(
                "Can only navigate to key/value pairs if the value is a list or dict")
            return subdata

        navigator_kwargs = {}
        navigator_kwargs["_prevent_index_creation"] = _prevent_index_creation
        navigator_kwargs["index_name"] = index_name
        post_call = lambda result: [x for y in result for x in y]
        return self._looper(
            nav_inner, 
            post_call=post_call, 
            include_errors=False,
            navigator_kwargs=navigator_kwargs
        )

    def delete(self, key: str, _index_name: str = '') -> Navigator:
        """Deletes a key-value pair from the list of dictionaries."""
        def delete_inner(datum: dict): 
            del(datum[key])
            return datum
        if _index_name: navigator_kwargs: dict = {"index_name": _index_name} 
        else: navigator_kwargs: dict = {}
        return self._looper(
            delete_inner, 
            navigator_kwargs=navigator_kwargs
        )

    def detach(self, key: str, index_name: str = '') -> Navigator:
        """
        TODO: The new object should link to the previous so it's posible to construct relations
        """
        if not index_name: index_name = self.index_name
        if index_name in self._get_keys_for_sub(key): index_name += "_parent"
        temp: Navigator = self.demote(
            demoted_key=index_name, 
            demotion_location=key,
            delete=False,
        )
        result = temp.nav(key, index_name=index_name)
        result.parent_obj = self
        return result

    def explode(self, key) -> Navigator:
        """Takes all key-value pairs in the top level and demotes them to all subordinate
        elements in a list of dictionaries found under the provided key.
        """
        # copied_data = copy.deepcopy(self.data)
        copied_data = self.data
        new_data = handle_list(copied_data, key)
        return Navigator(
            new_data, 
            index_name=self.index_name,
            _parent_obj=self.parent_obj
        )


    def copy(self) -> Navigator:
        """Returns a new instance of the object using list and dictionary comprehension. 
        This method is an attempt to implement a copy method that is safe from changes to the 
        seperate objects (changes in the original object doesn't influence the copy) without having
        to use expensive deepcopy methods. 
        """
        data = [{k:v for k, v in x.items()} for x in self.data]
        return Navigator(data, index_name=self.index_name, _parent_obj=self.parent_obj)

    def _get_keys(self):
        """Gets a set with all found keys across the dictionaries in the data list.
        The function ensures all keys are accounted for across posibly varying dictionary objects. 
        """
        return set(self.analyse().data.keys())

    def _get_keys_for_sub(self, key: str):
        """Navigates to a subkey in the list of dictionaries and gets all underlying keys."""
        return self.nav(key, _prevent_index_creation=True)._get_keys()

    def __getitem__(self, idx: int | str | tuple) -> list[dict[str, Any]] | dict[str, Any]:
        """The __getitem__ method allow for three diferent methods to return data. 
        If a string is used (e.g. self["somevalue"]) then a list of the key-value pair is 
        returned from self.data as a dictionary. If an integer is used (e.g. self[0]) then the 
        dictionary at X positon from the list of dictionaries at self.data is returned. You can 
        also use a tuple (e.g. self["somevalue", "othervalue", "thirdvalue"]) to select multiple
        key-values from self.data (like the string method which only returns a single instance). 
        """
        if isinstance(idx, int):
            return self.data[idx]
        elif isinstance(idx, str):
            return [x[idx] for x in self.data if idx in x.keys()]
        elif isinstance(idx, tuple):
            return [{k:v for k,v in x.items() if k in idx} for x in self.data]
        else: raise TypeError("__getitem__ only accepts arguments of type(s): int, str, and tuple")

    def analyse(self): # Temporary solution?
        return find_types(self.data) 


    def __repr__(self):
        pprint(self.analyse())
        return ""

class AnalysesCollection:
    def __init__(self, data: dict[str, AnalysisHandler], lenght: int) -> None:
        self.data = data
        self.lenght = lenght
        self.lk = self._find_longest_key()

    def _find_longest_key(self):
        return max([len(x) for x in self.data.keys()])

    def __repr__(self):
        result_string = ""
        for k, v in self.data.items():
            spaces = " "*(self.lk-len(k))
            result_string += f"{k} {spaces} l:{v.count}, t:{v.types_all}\n"

        return result_string
    

class AnalysisHandler:
    def __init__(self):
        self.count = 0
        self.types = {}
        self.types_all = set()

    def add(self, type_found: type):
        self.types.setdefault(type_found, 0)
        self.types[type_found] += 1
        self.types_all.add(type_found)

    def register(self): 
        self.count += 1

    def __repr__(self):
        return f"<AnalysisHandler types = {str(self.types)}, count = {self.count}>"


class ErrorLog:
    """
    Description of the desired functionality: 

    This class should handle errors and create a sort of collection of all the different errors
    that is encountered during data wrangling. 
    The class should be able to write data to a database that is easy to merge with the seperate
    tables created in the data wrangling process.
    The ErrorLog uses the Errors object as a basis of logging errors.

    Also, there should be some read functionality so it's possible to load a generated ErrorLog table
    in a database and analyse the errors in a simple maner. 
    """ 
    def __init__(self) -> None: 
        self.errors = []


class Errors: 
    def __init__(
            self, 
            exception: Exception, 
            argument_provided_to_func: Any,
            index_name: str,
            object_ref: Navigator | None = None,
            func: Callable | None = None
        ): 
        self.exception = exception
        if isinstance(func, Callable):
            self.func_name = func.__name__
        else: self.func_name = "NoneType"
        self.object_ref = object_ref
        self.index_name = index_name
        self.argument_provided_to_func = argument_provided_to_func
        self.index_value = argument_provided_to_func[index_name]

def find_types(data: list[dict]):
    """Generates a AnalysesCollaction-object after analysing a list of dictionaries. The
    function returns a AnalysesCollection object which can visually represent the results.
    """
    results = DefaultDict(AnalysisHandler)
    for dict_obj in data:
        for k, v in dict_obj.items():
            type_found = type(v)
            results[k].register()
            results[k].add(type_found)
    lenght = len(data)
    return AnalysesCollection(dict(results), lenght)


def _put_dicts_in_lists(data) -> list:
    """This is a helper function that puts a single dict input in a list"""
    if isinstance(data, dict): return [data]
    elif isinstance(data, list): return data
    else: raise TypeError(f"Data must be of type list or dict." 
                          "{type(data).__name__} provided,")


def _error_handler(exception: Exception, func: Callable):
    """Creates and returns the default error reporting format"""
    return {
            "error_name": type(exception).__name__, 
            "obj": exception,
            "func_name": func.__name__
    }


if __name__ == '__main__':
    data = get_test_data()
    nav_base: Navigator = Navigator(data)
    res = find_types(nav_base.data)
    nav = (
        nav_base
        .nav("hits")
        .nav("hits")
        .nav("_source")
        .nav("Vrvirksomhed")
    )
    prom = nav.promote("virksomhedMetadata", "meta_")
    prom = prom.set_index("cvrNummer")
    res = find_types(prom.data)
    pprint(res)
    demoted = nav.demote("cvrNummer", "hovedbranche", delete=False)
    hb_nav = demoted.nav("hovedbranche")

