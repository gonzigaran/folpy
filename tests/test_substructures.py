from unittest import TestCase
import random

from folpy.examples import lattices, posets
from folpy.utils.methods import (
                                substructures_updown,
                                substructures_downup,
                                substructures_by_maximals
                            )

models = [
    lattices.gen_chain(2),
    lattices.gen_chain(3),
    lattices.gen_chain(4),
    lattices.gen_chain(5),
    lattices.gen_chain(2)*lattices.gen_chain(3),
    lattices.rhombus,
    lattices.M3,
    lattices.N5,
    posets.gen_chain(2),
    posets.gen_chain(3),
    posets.gen_chain(4),
    posets.gen_chain(5),
    posets.gen_chain(2)*posets.gen_chain(3),
    posets.rhombus,
    posets.M3
]


class SubstructuresTest(TestCase):
    def test_always_passes(self):
        self.assertTrue(
            self.without_iso(),
            msg="error in substructure without isomorphism"
            )
        self.assertTrue(
            self.with_iso(),
            msg="error in substructure with isomorphism"
            )

    def without_iso(self):
        result = True
        for model in random.choices(models, k=5):
            t = len(list(substructures_downup(model, filter_isos=False))) == \
                len(list(substructures_updown(model, filter_isos=False)))
            result = result and t
        for model in random.choices(models, k=5):
            t = len(list(substructures_updown(model, filter_isos=False))) == \
                len(list(substructures_by_maximals(model, filter_isos=False)))
            result = result and t
        return result

    def with_iso(self):
        result = True
        for model in random.choices(models, k=5):
            t = len(list(substructures_updown(model, filter_isos=True))) == \
                len(list(substructures_by_maximals(model, filter_isos=True)))
            result = result and t
        return result
