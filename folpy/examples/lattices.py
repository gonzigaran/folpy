#!/usr/bin/env python
# -*- coding: utf8 -*-

"""
Modulo con ejemplos de reticulados
"""

from ..semantics import Algebra
from ..syntax.types import AlgebraicType
from ..semantics.modelfunctions import Operation, Operation_decorator


ret_type = AlgebraicType({"^": 2, "v": 2})

rhombus = Algebra(
    ret_type,
    list(range(4)),
    {
        "^": Operation({(0, 0): 0,
                        (0, 1): 1,
                        (0, 2): 2,
                        (0, 3): 3,
                        (1, 0): 1,
                        (1, 1): 1,
                        (1, 2): 3,
                        (1, 3): 3,
                        (2, 0): 2,
                        (2, 1): 3,
                        (2, 2): 2,
                        (2, 3): 3,
                        (3, 0): 3,
                        (3, 1): 3,
                        (3, 2): 3,
                        (3, 3): 3}),
        "v": Operation({(0, 0): 0,
                        (0, 1): 0,
                        (0, 2): 0,
                        (0, 3): 0,
                        (1, 0): 0,
                        (1, 1): 1,
                        (1, 2): 0,
                        (1, 3): 1,
                        (2, 0): 0,
                        (2, 1): 0,
                        (2, 2): 2,
                        (2, 3): 2,
                        (3, 0): 0,
                        (3, 1): 1,
                        (3, 2): 2,
                        (3, 3): 3})
    },
    name="Rhombus Lattice 4"
)

M3 = Algebra(
    ret_type,
    list(range(5)),
    {
        "^": Operation({(0, 0): 0,
                        (0, 1): 1,
                        (0, 2): 2,
                        (0, 3): 3,
                        (0, 4): 4,
                        (1, 0): 1,
                        (1, 1): 1,
                        (1, 2): 4,
                        (1, 3): 4,
                        (1, 4): 4,
                        (2, 0): 2,
                        (2, 1): 4,
                        (2, 2): 2,
                        (2, 3): 4,
                        (2, 4): 4,
                        (3, 0): 3,
                        (3, 1): 4,
                        (3, 2): 4,
                        (3, 3): 3,
                        (3, 4): 4,
                        (4, 0): 4,
                        (4, 1): 4,
                        (4, 2): 4,
                        (4, 3): 4,
                        (4, 4): 4}),
        "v": Operation({(0, 0): 0,
                        (0, 1): 0,
                        (0, 2): 0,
                        (0, 3): 0,
                        (0, 4): 0,
                        (1, 0): 0,
                        (1, 1): 1,
                        (1, 2): 0,
                        (1, 3): 0,
                        (1, 4): 1,
                        (2, 0): 0,
                        (2, 1): 0,
                        (2, 2): 2,
                        (2, 3): 0,
                        (2, 4): 2,
                        (3, 0): 0,
                        (3, 1): 0,
                        (3, 2): 0,
                        (3, 3): 3,
                        (3, 4): 4,
                        (4, 0): 0,
                        (4, 1): 1,
                        (4, 2): 2,
                        (4, 3): 3,
                        (4, 4): 4}),
    },
    name="Lattice M3"
)

M5 = Algebra(
    ret_type,
    list(range(5)),
    {
        "^": Operation({(0, 0): 0,
                        (0, 1): 1,
                        (0, 2): 2,
                        (0, 3): 3,
                        (0, 4): 4,
                        (1, 0): 1,
                        (1, 1): 1,
                        (1, 2): 2,
                        (1, 3): 4,
                        (1, 4): 4,
                        (2, 0): 2,
                        (2, 1): 2,
                        (2, 2): 2,
                        (2, 3): 4,
                        (2, 4): 4,
                        (3, 0): 3,
                        (3, 1): 4,
                        (3, 2): 4,
                        (3, 3): 3,
                        (3, 4): 4,
                        (4, 0): 4,
                        (4, 1): 4,
                        (4, 2): 4,
                        (4, 3): 4,
                        (4, 4): 4}),
        "v": Operation({(0, 0): 0,
                        (0, 1): 0,
                        (0, 2): 0,
                        (0, 3): 0,
                        (0, 4): 0,
                        (1, 0): 0,
                        (1, 1): 1,
                        (1, 2): 1,
                        (1, 3): 0,
                        (1, 4): 1,
                        (2, 0): 0,
                        (2, 1): 1,
                        (2, 2): 2,
                        (2, 3): 0,
                        (2, 4): 2,
                        (3, 0): 0,
                        (3, 1): 0,
                        (3, 2): 0,
                        (3, 3): 3,
                        (3, 4): 4,
                        (4, 0): 0,
                        (4, 1): 1,
                        (4, 2): 2,
                        (4, 3): 3,
                        (4, 4): 4}),
    },
    name="Lattice N5"
)


def gen_chain(n):
    universe = list(range(n))

    @Operation_decorator(universe)
    def sup(x, y):
        return max(x, y)

    @Operation_decorator(universe)
    def inf(x, y):
        return min(x, y)

    operations = {"^": sup, "v": inf}

    return Algebra(ret_type,
                   universe,
                   operations,
                   name="Chain Lattice %s" % n)
