from NestNinja import Navigator
from test_utils import get_test_data 

def test_getitem_method_int():
    """Gets one dictionary from the list of dictionaries and asserts it is a dictionary."""
    nav_base = get_nav_base()
    assert isinstance(nav_base[0], dict)
    ...

def test_navigation():
    """The test case navigatese through the JSON-object. 
    A check is performed to see if an expected value is in the final object.
    """
    nav_base = get_nav_base()
    nav = (
        nav_base
        .nav("hits")
        .nav("hits")
        .nav("_source")
        .nav("Vrvirksomhed")
    )
    assert len(nav["cvrNummer"]) > 0


def get_nav_base():
    data = get_test_data()
    nav_base = Navigator(data)
    return nav_base
