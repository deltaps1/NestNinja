"""
This document is for testing the funtionality of NestNinja on a large dataset
"""
from test_utils import get_test_data
from NestNinja import Navigator

test_data = get_test_data()
nav = (
    Navigator(test_data)
    .nav("hits")
    .nav("hits")
    .nav("_source")
    .nav("Vrvirksomhed", index_name="cvrNummer")
)

hb = (
    nav
    .detach("hovedbranche")
    .promote("periode")
)

delt = (
    nav
    .detach("deltagerRelation")
    .promote("deltager")
    .explode("organisationer")
    .explode("medlemsData")
    .explode("attributter")
    .explode("vaerdier")
    .promote("periode")
)

print(delt_done)
