"""
Test cases implemented: 
- Simple copy on object level (`test_copy1`)
- Simple copy on sublevel (`test_copy1`)
- Get item method for dictionaries in lists (`test_getitem_method_int`)
- Navigation to a subkey (`test_navigation`) 
- Promotion of a subkey (`test_promote`)

Test cases not implemented:
- Splits (not implemented yet)
- Demotions
- Renaming 
- Index setting
- Index creation
- Deletion 
- Detachments 
- Explosions
"""

from NestNinja import Navigator
from test_utils import get_test_data 


TEST_DATA = get_test_data()
BASE_OBJECT = Navigator(TEST_DATA)


def get_copy_of_base_object():
    """Creates a copy of the base object"""
    return BASE_OBJECT.copy()


def navigate_to_actual_data():
    """Navigates through the data structure to the interesting part of the data"""
    nav_base = get_copy_of_base_object()
    nav = (
        nav_base
        .nav("hits")
        .nav("hits")
        .nav("_source")
        .nav("Vrvirksomhed")
    )
    return nav


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
    nav = navigate_to_actual_data()
    assert len(nav["cvrNummer"]) > 0


def test_promote():
    """Checks that promotion functions. Promotes a key from the test data
    and asserts that a given key is in newly created `Navigator`.
    """
    base = navigate_to_actual_data()
    promoted = base.promote('virksomhedMetadata', "meta_")
    promoted_anaysed = promoted.analyse()
    assert "meta_nyesteNavn" in promoted_anaysed.data


if __name__ == "__main__": 
    testobj = test_navigation()
    print(testobj)
