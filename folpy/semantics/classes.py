#!/usr/bin/env python
# -*- coding: utf8 -*-

import itertools

from ..syntax import AlgebraicType
from .morphisms import Homomorphism
from .congruences import sup_proj
from .modelfunctions import Operation, Constant
from .algebras import Algebra, AlgebraProduct

import check_isos


class Quasivariety(object):
    """
    Cuasivariedad generada por un conjunto de algebras finitas.
    """

    def __init__(self, generators, name=""):
        self.type = generators[0].type
        for i in range(len(generators)):
            assert generators[i].type == self.type, "Los generadores no tienen\
                 el mismo tipo"
        self.generators = generators
        self.name = name
        self.rsi = False

    def rsi(self):
        """
        Dada un conjunto de álgebras, devuelve el conjunto de álgebras
         relativamente subdirectamente irreducibles para la cuasivariedad
         generada.

        >>> from folpy.examples.lattices import gen_lat
        >>> len(Quasivariety([gen_lat(2), gen_lat(3), gen_lat(4)]]).rsi())
        1
        """

        sub = []
        for a in self.generators:
            suba = a.substructures(a.type)
            for s in suba:
                if len(s[1]) != 1 and not check_isos(s[1], sub, self.type):
                    sub.append(s[1].continous()[0])
        n = len(sub)
        for i in range(n - 1, -1, -1):
            ker = {(x, y) for x in sub[i].universe for y in sub[i].universe}
            mincon = {(x, x) for x in sub[i].universe}
            t = False
            for j in range(0, len(sub)):
                if i != j:
                    for f in sub[i].homomorphisms_to(sub[j], self.type,
                                                     surj=True):
                        ker = ker & {tuple(t) for t in f.kernel().table()}
                        if ker == mincon:
                            sub.pop(i)
                            t = True
                            break
                if t:
                    break
        self.rsi = sub
        return sub

    def contains(self, a):
        """
        Dada un algebra ´a´, se fija si ´a´ pertenece a la cuasivariedad

        >>> from definability.first_order.fotheories import Lat
        >>> from definability.functions.morphisms import Homomorphism
        >>> type(Quasivariety(list(Lat.find_models(5))[0:3])
        ... .contains(list(Lat.find_models(5))[3])) == Homomorphism
        True
        """
        if type(self.rsi) == list:
            rsi = self.rsi
        else:
            rsi = self.rsi()
        if check_isos(a, rsi, self.type):
            return "El álgebra es relativamente subirectamente irreducible"
        else:
            F = set()
            ker = {(x, y) for x in a.universe for y in a.universe}
            mincon = {(x, x) for x in a.universe}
            t = False
            for b in rsi:
                for f in a.homomorphisms_to(b, a.type, surj=True):
                    ker = ker & {tuple(t) for t in f.kernel().table()}
                    F.add(f)
                    if ker == mincon:
                        t = True
                        break
                if t:
                    break
        if t:
            target = AlgebraProduct([f.target for f in F])
            d = {}
            for x in a.universe:
                d[(x,)] = tuple([f(x,) for f in F])
            return Homomorphism(d, a, target, a.type)
        else:
            return False

    def cmi(self, a):
        """
        Dada un algebra ´a´ que pertenece a Q devuelve el conjunto de las
        congruencias completamente meet irreducibles.
        """
        if type(self.rsi) == list:
            rsi = self.rsi
        else:
            rsi = self.rsi()
        f = self.contains(a)
        if type(f) == bool:
            return "El álgebra no pertenece a Q"
        elif type(f) == Homomorphism:
            result = []
            for b in rsi:
                for f in a.homomorphisms_to(b, a.type, surj=True):
                    result.append(f.kernel())
            return list(set(result))
        return [a.mincon()]

    def congruence_lattice(self, a):
        """
        Dada un algebra ´a´ que pertenece a Q devuelve ConQ(a).
        """
        cmi = self.cmi(a)
        if type(cmi) == list:
            subs = []
            univ = [a.maxcon()]
            for n in range(len(cmi) + 1):
                for s in itertools.combinations(cmi, n):
                    subs.append(s)
            for s in subs:
                e = a.maxcon()
                for x in s:
                    e = e & x
                if e not in univ:
                    univ.append(e)
            bound_lat_type = AlgebraicType({"^": 2,
                                            "v": 2,
                                            "Max": 0,
                                            "Min": 0}, {})
            lat = Algebra(bound_lat_type, univ, {
                'Max': Constant(a.maxcon()),
                'Min': Constant(a.mincon()),
                '^': Operation({(x, y): x & y for x in univ for y in univ}),
                'v': Operation(
                    {(x, y): sup_proj(cmi, x, y) for x in univ for y in univ}
                    )}, {})
            return lat
        return "El álgebra no pertenece a Q"


if __name__ == "__main__":
    import doctest
    doctest.testmod()
