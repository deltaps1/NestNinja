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

besk = (
    nav
    .detach("erstMaanedsbeskaeftigelse")
)

meta = (
    nav
    .detach("virksomhedMetadata", index_name="cvrNummer")
)

print("nav \n", nav.parent_obj )
print("hb  \n", hb.parent_obj  )
print("delt\n", delt.parent_obj)
print("besk\n", besk.parent_obj)
print("meta\n", meta.parent_obj)

ids_test = [
    id(nav            ),
    id(hb.parent_obj  ),
    id(delt.parent_obj),
    id(besk.parent_obj),
    id(meta.parent_obj),
]
assert len(set(ids_test)) == 1


