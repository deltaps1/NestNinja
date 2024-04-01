from __future__ import annotations
from collections import defaultdict
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
            post_call: Callable | Literal[False] = False,
            include_errors: bool = True
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
        return Navigator(result)

    def create_index(self):
        ...

    def promote(self, key: str | list, prefix: str = "") -> Navigator:
        def promote_inner(datum: dict):
            res = {k:v for k,v in datum.items() if k != key}
            for k, v in datum[key].items(): res[prefix + k] = v
            return res
        return self._looper(promote_inner) 

    def demote(self, demoted_key: str, demotion_location: str, delete: bool = True): 
        def demote_inner(datum: dict): 
            demotion_data = datum[demotion_location]
            if not isinstance(demotion_data, (list, dict)): 
                return []
            if isinstance(demotion_data, dict): demotion_data = [demotion_data]
            demotion_data = [x for x in demotion_data]

            res = []
            for demotion_sub in demotion_data:
                demotion_sub[demoted_key] = datum[demoted_key]
                res.append(demotion_sub)
                if isinstance(demotion_sub, str): print(demotion_sub)
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

    def nav(self, key: str) -> Navigator:
        def nav_inner(datum: dict): 
            subdata = datum[key] 
            if not isinstance(subdata, list): subdata = [subdata]
            return subdata
        post_call = lambda result: [x for y in result for x in y]
        return self._looper(nav_inner, post_call=post_call, include_errors=False)

    def delete(self, key: str) -> Navigator:
        def delete_inner(datum: dict): del(datum[key])
        return self._looper(delete_inner)

    def detach(self) -> Navigator | list:
        ...

    def explode(self) -> Navigator | list:
        ...

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self.data[idx]
        elif isinstance(idx, str):
            return [x[idx] for x in self.data if idx in x.keys()]
        elif isinstance(idx, tuple):
            print(idx)
            return [{k:v for k,v in x.items() if k in idx} for x in self.data]

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
        self.types = defaultdict(int)
        self.types_all = set()

    def add(self, type_found: type):
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

if __name__ == '__main__':
    data = get_test_data()
    nav: Navigator = Navigator(data)
    res = find_types(nav.data)
    pprint(res)
    new = (
        nav
        .nav("hits")
        .nav("hits")
        .nav("_source")
        .nav("Vrvirksomhed")
        .promote("virksomhedMetadata", "meta_")
    )
    res = find_types(new.data)
    pprint(res)
    demoted = new.demote("cvrNummer", "hovedbranche", delete=False)
    hb_nav = demoted.nav("hovedbranche")
