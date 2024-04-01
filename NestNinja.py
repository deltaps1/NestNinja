from __future__ import annotations
from typing import Any, Callable, DefaultDict, Literal
from test_utils import get_test_data
from pprint import pprint

def _error_handler(exception: Exception, func: Callable):
    return {
            "error_name": type(exception).__name__, 
            "obj": exception,
            "func_name": func.__name__
    }

class Navigator:
    def __init__(
            self, 
            data: list | dict,
            index: str | Literal[False] = False
        ):
        self.data: list = self._base_clean_data(data)
        self.index_name: str = "_idx" if not index else index

    @staticmethod
    def _base_clean_data(data: list | dict):
        return [data] if isinstance(data, dict) else data

    def set_index(self, idx_name: str, keep_old: bool = False):
        ...

    def _looper(
            self, 
            func: Callable, 
            post_call: Callable | Literal[False] = False
        ) -> Navigator:
        data: list = [x for x in self.data]
        result = []
        for datum in data:
            try: result.append(func(datum))
            except Exception as error: 
                datum.setdefault("_error", [])
                datum["_error"].append(_error_handler(error, func))
                result.append(datum)
        if post_call: result = post_call(result)
        return Navigator(result)

    def create_index(self):
        ...

    def promote(self, key: str | list, prefix: str = "") -> Navigator:
        def func(datum: dict):
            res = {k:v for k,v in datum.items() if k != key}
            for k, v in datum[key].items(): res[prefix + k] = v
            return res
        return self._looper(func) 

    def demote(self, demoted_key: str, demotion_location: str, delete: bool = True): 
        def func(datum: dict): 
            datum[demotion_location][demoted_key] = datum[demoted_key]
            if delete: del(datum[demoted_key])

    def rename(self, old_name: str, new_name: str) -> Navigator | list:
        def func(datum: dict):
            datum[new_name] = datum[old_name]
            del(datum[old_name])
            return datum
        return self._looper(func)

    def split(self, key: str, func: Callable) -> Navigator | list:
        def _func(datum: dict):
            eval_res = func(datum[key]) # Check if the function is True
            new_key = key + ("_true" if eval_res else "_false")
            datum[new_key] = datum[key]
            return datum 
        return self._looper(_func)

    def nav(self, key: str) -> Navigator:
        def func(datum: dict): 
            subdata = datum[key] 
            if not isinstance(subdata, list): subdata = [subdata]
            return subdata
        post_call = lambda result: [x for y in result for x in y]
        return self._looper(func, post_call=post_call)

    def delete(self, key: str) -> Navigator:
        def func(datum: dict): del(datum[key])
        return self._looper(func)

    def detach(self) -> Navigator | list:
        ...

    def explode(self) -> Navigator | list:
        ...

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self.data[idx]
        elif isinstance(idx, str):
            selection = [x for x in self.data if idx in x.keys()]

class AnalysisHandler:
    def __init__(self):
        self.count = 0
        self.types = set()

    def add(self, type_found: type):
        self.types.add(type_found)

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
    return dict(results), lenght

if __name__ == '__main__':
    data = get_test_data()
    nav: Navigator = Navigator(data)
    res, lenght = find_types(nav.data)
    pprint(res)
    new = (
            nav
            .nav("hits")
            .nav("hits")
            .nav("_source")
            .nav("Vrvirksomhed")
    )
    res, _ = find_types(new.data)
    prom = new.promote("virksomhedMetadata", "meta_")
    res, _ = find_types(prom.data)
    pprint(res)
