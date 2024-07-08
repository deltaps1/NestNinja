

def get_type_suggestion(set_of_types):
    set_of_types = set(set_of_types)
    if str in set_of_types:
        return str
    elif {float, int} == set_of_types:
        return float
    elif {dict} == set_of_types or\
         {list} == set_of_types:
        return list(set_of_types)[0] 
    else: return str

