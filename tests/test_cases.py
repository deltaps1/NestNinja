from NestNinja import Navigator
from test_utils import get_test_data 


def get_nav_base():
    """Setup the basis `Navigation` object"""
    data = get_test_data()
    nav_base = Navigator(data)
    return nav_base

BASE_OBJECT = get_nav_base()

def get_copy_of_base_object():
    """Creates a copy of the base object"""
    return BASE_OBJECT.copy()

def test_copy1():
    """Test that the copy functionality returns a new instance"""
    base = get_copy_of_base_object()
    new = base.copy()
    assert id(base.data) != id(new.data)
    
def test_copy2():
    """Test that the copy functionality returns a new instance"""
    base = get_copy_of_base_object()
    new = base.copy()
    assert id(base.data[0]) != id(new.data[0])

def test_getitem_method_int():
    """Gets one dictionary from the list of dictionaries and asserts it is a dictionary."""
    nav_base = get_copy_of_base_object()
    assert isinstance(nav_base[0], dict)


def test_navigation():
    """The test case navigatese through the JSON-object. 
    A check is performed to see if an expected value is in the final object.
    """
    nav_base = get_copy_of_base_object()
    nav = (
        nav_base
        .nav("hits")
        .nav("hits")
        .nav("_source")
        .nav("Vrvirksomhed")
    )
    assert len(nav["cvrNummer"]) > 0
    return nav

def test_promote():
    """Checks that promotion functions. Promotes a key from the test data
    and asserts that a given key is in newly created `Navigator`.
    """
    base = get_nav_base()
    promoted = base.promote('virksomhedMetadata', "meta_")
    promoted_anaysed = promoted.analyse()
    assert "meta_nyesteNavn" in promoted_anaysed.data

if __name__ == "__main__": 
    testobj = test_navigation()
    print(testobj)
