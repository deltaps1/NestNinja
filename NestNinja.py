from typing import Callable, Literal
from test_utils import get_test_data

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

    def set_index(self, idx_name: str):
        ...

    def _looper(self, func: Callable):
        result = []
        for datum in self.data:
            try: result.append(func(datum))
            except Exception as error: 
                datum.setdefault("_error", [])
                datum["_error"].append(_error_handler(error, func))
                print(error) # debug print
                result.append(datum)
        self.data = result

    def promote(self, key: str | list, prefix: str = ""):
        def func(datum: dict):
            res = {k:v for k,v in datum.items() if k != key}
            for k, v in datum[key].items(): res[prefix + k] = v
            return res
        self._looper(func) 

    def rename(self, old_name: str, new_name: str):
        def func(datum: dict):
            datum[new_name] = datum[old_name]
            del(datum[old_name])
            return datum
        self._looper(func)

class TypeAnalyser:
    def __init__(self, data: list):
        self.data = data

if __name__ == '__main__':
    data = get_test_data()
    nav = Navigator(data)
