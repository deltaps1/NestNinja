from __future__ import annotations
from collections import defaultdict
from typing import Any, Callable, DefaultDict, Literal
from test_utils import get_test_data
from pprint import pprint


class Navigator:
    def __init__(
            self, 
            data: list | dict,
            index_name: str = '',
            _debug_msg: str = '',
            _prevent_index_creation: bool = False
        ):
        if _debug_msg:
            print(f"Navigator initialised. Message: {_debug_msg}")
            print(f"Index name: {index_name}")

        self.data: list = _put_dicts_in_lists(data)
        self.index_name = index_name
        if index_name: 
            self.index_name = index_name
        elif _prevent_index_creation: ... # Don't do anything
        else: 
            self.index_name = "_idx"
            self.create_index()

    def _looper(
            self, 
            func: Callable, 
            post_call: Callable | Literal[False] = False,
            include_errors: bool = True,
            navigator_kwargs: dict = {}
        ) -> Navigator:
        data: list = [x for x in self.data]
        result = []
        for datum in data:
            try: result.append(func(datum))
            except Exception as error: 
                if include_errors:
                    datum.setdefault("_error", [])
                    datum["_error"].append(_error_handler(error, func))
                    result.append(datum)
        if post_call: result = post_call(result)
        return Navigator(result, **navigator_kwargs)

    def set_index(self, index_name: str, keep_old: bool = False):
        if not keep_old:
            res = self.delete(key=self.index_name, _index_name=index_name)
            res.index_name = index_name
        else: res = Navigator(self.data, index_name=index_name)
        return res

    def create_index(self):
        for i, datum in enumerate(self.data):
            datum[self.index_name] = i

    def promote(self, key: str | list, prefix: str = "") -> Navigator:
        def promote_inner(datum: dict):
            res = {k:v for k,v in datum.items() if k != key}
            for k, v in datum[key].items(): res[prefix + k] = v
            return res
        return self._looper(promote_inner) 

    def demote(self, demoted_key: str, demotion_location: str, delete: bool = True) -> Navigator: 
        def demote_inner(datum: dict): 
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
        return self._looper(demote_inner) # post_call=post_call) 

    def rename(self, old_name: str, new_name: str) -> Navigator | list:
        def rename_inner(datum: dict):
            datum[new_name] = datum[old_name]
            del(datum[old_name])
            return datum
        return self._looper(rename_inner)

    def split(self, key: str, func: Callable) -> Navigator | list:
        def split_inner(datum: dict):
            eval_res = func(datum[key]) # Check if the function is True
            new_key = key + ("_true" if eval_res else "_false")
            datum[new_key] = datum[key]
            return datum 
        return self._looper(split_inner)

    def nav(self, key: str, _prevent_index_creation: bool = False) -> Navigator:
        def nav_inner(datum: dict): 
            subdata = datum[key] 
            if not isinstance(subdata, list): subdata = [subdata]
            return subdata
        if _prevent_index_creation: navigator_kwargs = {"_prevent_index_creation": True}
        else: navigator_kwargs = {}
        post_call = lambda result: [x for y in result for x in y]
        return self._looper(
            nav_inner, 
            post_call=post_call, 
            include_errors=False,
            navigator_kwargs=navigator_kwargs
        )

    def delete(self, key: str, _index_name: str = '') -> Navigator:
        def delete_inner(datum: dict): 
            del(datum[key])
            return datum
        if _index_name: navigator_kwargs: dict = {"index_name": _index_name} 
        else: navigator_kwargs: dict = {}
        return self._looper(
            delete_inner, 
            navigator_kwargs=navigator_kwargs
        )

    def detach(self, key: str, index_name: str = '') -> Navigator | list:
        """
        TODO: The new object should link to the previous so it's posible to construct relations
        """
        if not index_name: index_name = self.index_name
        if index_name in self._get_keys_for_sub(key): index_name += "_parent"
        temp: Navigator = self.demote(
            demoted_key=index_name, 
            demotion_location=key,
            delete=False
        )
        result = temp.nav(key)
        return result

    def explode(self, key, prefix: str = '', delete: bool = True) -> Navigator | list:
        """
        TODO: Implement _get_keys/_get_keys_for_sub methods to streamline code. 
        """
        backup_prefix = "_sub"
        def inner_explode(datum: dict):
            if not isinstance(datum[key], list):
                return [datum]
            res = []
            for subdata in datum[key]:
                res_data = {k:v for k, v in datum.items()}
                for subkey, subvalue in subdata.items():
                    used_prefix = prefix + subkey
                    if used_prefix in res_data.keys():
                        used_prefix = backup_prefix + used_prefix
                    res_data[used_prefix] = subvalue
                    if delete: del(res_data[key])
                res.append(res_data)
        post_call = lambda result: [x for y in result for x in y]
        return self._looper(inner_explode, post_call=post_call)

    def _get_keys(self):
        """
        Gets a set with all found keys across the dictionaries in the data list.
        The function ensures all keys are accounted for across posibly varying dictionary objects. 
        """
        return set(self.analyse().data.keys())

    def _get_keys_for_sub(self, key: str):
        """
        Navigates to a subkey in the list of dictionaries and gets all underlying keys. 
        """
        return self.nav(key, _prevent_index_creation=True)._get_keys()

    def __getitem__(self, idx) -> list[dict[str, Any]] | dict[str, Any]:
        if isinstance(idx, int):
            return self.data[idx]
        elif isinstance(idx, str):
            return [x[idx] for x in self.data if idx in x.keys()]
        elif isinstance(idx, tuple):
            return [{k:v for k,v in x.items() if k in idx} for x in self.data]
        else: raise TypeError("__getitem__ only accepts arguments of type(s): int, str, and tuple")

    def analyse(self): # Temporary solution
        return find_types(self.data) 


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


def find_types(data: list[dict]):
    results = DefaultDict(AnalysisHandler)
    for dict_obj in data:
        for k, v in dict_obj.items():
            type_found = type(v)
            results[k].register()
            results[k].add(type_found)
    lenght = len(data)
    return AnalysesCollection(dict(results), lenght)


def _put_dicts_in_lists(data):
    if isinstance(data, dict): return [data]
    elif isinstance(data, list): return data
    else: raise TypeError(f"Data must be of type list or dict." 
                          "{type(data).__name__} provided,")


def _error_handler(exception: Exception, func: Callable):
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

