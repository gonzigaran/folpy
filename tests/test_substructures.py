from unittest import TestCase
import random

from folpy.examples import lattices, posets
from folpy.utils.methods import (
                                substructures_by_maximals,
                                substructures
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

    def without_iso(self):
        result = True
        for model in random.choices(models, k=5):
            t = len(list(substructures(model, filter_isos=False))) == \
                len(list(substructures_by_maximals(model, filter_isos=False)))
            result = result and t
        return result
