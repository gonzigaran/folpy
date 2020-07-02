#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
Modulo con ejemplos de posets
"""

from ..semantics import Model
from ..syntax.types import Type
from ..semantics.modelfunctions import Relation, Relation_decorator


poset_type = Type({}, {"<=": 2})

rhombus = Model(
    poset_type,
    list(range(4)),
    {},
    {'<=': Relation({
        (0, 0): 1,
        (0, 1): 1,
        (0, 2): 1,
        (0, 3): 1,
        (1, 0): 0,
        (1, 1): 1,
        (1, 2): 0,
        (1, 3): 0,
        (2, 0): 0,
        (2, 1): 1,
        (2, 2): 1,
        (2, 3): 0,
        (3, 0): 0,
        (3, 1): 1,
        (3, 2): 0,
        (3, 3): 1
        }, d_universe=list(range(4)))},
    name="Rhombus Poset"
)

M3 = Model(
    poset_type,
    list(range(5)),
    {},
    {"<=": Relation({
        (0, 0): 1,
        (0, 1): 1,
        (0, 2): 1,
        (0, 3): 1,
        (0, 4): 1,
        (1, 0): 0,
        (1, 1): 1,
        (1, 2): 0,
        (1, 3): 0,
        (1, 4): 0,
        (2, 0): 0,
        (2, 1): 1,
        (2, 2): 1,
        (2, 3): 0,
        (2, 4): 0,
        (3, 0): 0,
        (3, 1): 1,
        (3, 2): 0,
        (3, 3): 1,
        (3, 4): 0,
        (4, 0): 0,
        (4, 1): 1,
        (4, 2): 0,
        (4, 3): 0,
        (4, 4): 1
        }, d_universe=list(range(5)))},
    name="M3 Poset"
)


def gen_chain(n):
    universe = list(range(n))

    @Relation_decorator(universe)
    def gt(x, y):
        return x <= y

    relations = {"<=": gt}

    return Model(poset_type,
                 universe,
                 {},
                 relations,
                 name="Chain Poset %s" % n)
