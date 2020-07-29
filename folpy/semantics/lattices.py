#!/usr/bin/env python
# -*- coding: utf8 -*-

from itertools import product, combinations
from functools import lru_cache

from ..syntax.types import AlgebraicType

from .algebras import Algebra, Subalgebra, Quotient
from .models import Product
from .modelfunctions import Operation


class Lattice(Algebra):

    """
    Clase para representar Reticulados, como un algebra con operaciones
    especificas
    """

    def __init__(self, universe, join, meet, name="", distributive=None):
        fo_type = AlgebraicType({"^": 2, "v": 2})
        operations = {}
        operations["v"] = join
        operations["^"] = meet
        super().__init__(fo_type, universe, operations, name)
        self.distributive = distributive

    def __mul__(self, other):
        """
        Calcula el producto entre reticulados
        """
        return LatticeProduct([self, other])

    def __pow__(self, exponent):
        """
        Calcula la potencia de un álgebra
        """
        return LatticeProduct([self] * exponent)

    def join(self, a, b):
        """
        devuelve el supremo de a y b para el reticulado
        """
        return self.operations['v'](a, b)

    def meet(self, a, b):
        """
        devuelve el infimo de a y b para el reticulado
        """
        return self.operations['^'](a, b)

    def gt(self, a, b):
        """
        devuelve la relación >= para los elementos a y b del reticulado
        """
        return self.join(a, b) == a

    def lt(self, a, b):
        """
        devuelve la relación <= para los elementos a y b del reticulado
        """
        return self.meet(a, b) == a

    @lru_cache(maxsize=1)
    def max(self):
        """
        devuelve el maximo del reticulado

        >>> from folpy.examples.lattices import *
        >>> model_to_lattice(rhombus).max()
        3
        >>> model_to_lattice(M3).max()
        4
        >>> model_to_lattice(N5).max()
        4
        """
        max_element = self.universe[0]
        for x in self.universe:
            max_element = self.join(x, max_element)
        return max_element

    @lru_cache(maxsize=1)
    def min(self):
        """
        devuelve el minimo del reticulado

        >>> from folpy.examples.lattices import *
        >>> model_to_lattice(rhombus).min()
        0
        >>> model_to_lattice(M3).min()
        0
        >>> model_to_lattice(N5).min()
        0
        """
        min_element = self.universe[0]
        for x in self.universe:
            min_element = self.meet(x, min_element)
        return min_element

    def continous(self):
        """
        Devuelve un álgebra isomorfa pero de universo [0..n]
        """
        translation = list(self.universe)
        universe = list(range(len(translation)))

        operations = {}
        for op in self.operations:
            operations[op] = self.operations[op].rename(translation)

        return (Lattice(universe,
                        operations['v'],
                        operations['^']), translation)

    def restrict(self, subuniverse):
        """
        Devuelve la restriccion del algebra al subuniverso que se supone
        que es cerrado en en subtype
        """
        return Sublattice(subuniverse,
                          {
                              '^': self.operations['^'].restrict(subuniverse),
                              'v': self.operations['v'].restrict(subuniverse),
                          },
                          self)

    @lru_cache(maxsize=1)
    def is_distributive(self):
        """
        Decide si un reticulado es distributivo

        >>> from folpy.examples.lattices import *
        >>> model_to_lattice(rhombus).is_distributive()
        True
        >>> model_to_lattice(M3).is_distributive()
        False
        >>> model_to_lattice(N5).is_distributive()
        False
        """
        if self.distributive:
            return self.distributive
        distributive = True
        for x, y, z in product(self.universe, repeat=3):
            condition1 = self.meet(x, self.join(y, z))
            condition2 = self.join(self.meet(x, y), self.meet(x, z))
            condition = condition1 == condition2
            distributive = distributive and condition
            if not distributive:
                break
        self.distributive = distributive
        return distributive

    @lru_cache()
    def covers(self, a):
        """
        devuelve una lista con los elementos que cubren a

        >>> from folpy.examples.lattices import *
        >>> model_to_lattice(rhombus).covers(0)
        [1, 2]
        >>> model_to_lattice(rhombus).covers(1)
        [3]
        >>> model_to_lattice(M3).covers(0)
        [1, 2, 3]
        """
        result = []
        for b in self.universe:
            if a != b and self.gt(b, a):
                if any((a != c and
                        self.gt(c, a) and
                        c != b and
                        self.gt(b, c)) for c in self.universe):
                    continue
                result.append(b)
        return result

    @property
    @lru_cache(maxsize=1)
    def covers_dict(self):
        """
        devuelve un diccionario que para cada elemento, tiene la lista con los
        elementos que cubren a ese elemento
        """
        result = {}
        for a in self.universe:
            result[a] = self.covers(a)
        return result

    @lru_cache()
    def covers_by(self, a):
        """
        devuelve una lista con los elementos que son cubiertos por a

        >>> from folpy.examples.lattices import *
        >>> model_to_lattice(rhombus).covers_by(3)
        [1, 2]
        >>> model_to_lattice(rhombus).covers_by(1)
        [0]
        >>> model_to_lattice(M3).covers_by(4)
        [1, 2, 3]
        """
        result = []
        for b in self.universe:
            if a != b and self.lt(b, a):
                if any((a != c and
                        self.lt(c, a) and
                        c != b and
                        self.lt(b, c)) for c in self.universe):
                    continue
                result.append(b)
        return result

    @property
    @lru_cache(maxsize=1)
    def covers_by_dict(self):
        """
        devuelve un diccionario que para cada elemento, tiene la lista con los
        elementos que son cubiertos por ese elemento
        """
        result = {}
        for a in self.universe:
            result[a] = self.covers_by(a)
        return result

    @lru_cache()
    def is_join_irreducible(self, a):
        """
        Decide si el elemento a es join-irreducible

        >>> from folpy.examples.lattices import *
        >>> model_to_lattice(N5).is_join_irreducible(2)
        True
        """
        return a != self.min() and len(self.covers_by_dict[a]) == 1

    @lru_cache(maxsize=1)
    def join_irreducibles(self):
        """
        Devuelve una lista con los join-irreducibles

        >>> from folpy.examples.lattices import *
        >>> model_to_lattice(N5).join_irreducibles()
        [1, 2, 3]
        """
        return [a for a in self.universe if self.is_join_irreducible(a)]

    @lru_cache()
    def is_meet_irreducible(self, a):
        """
        Decide si el elemento a es meet-irreducible

        >>> from folpy.examples.lattices import *
        >>> model_to_lattice(N5).is_join_irreducible(2)
        True
        """
        return a != self.max() and len(self.covers_dict[a]) == 1

    @lru_cache(maxsize=1)
    def meet_irreducibles(self):
        """
        Devuelve una lista con los meet-irreducibles

        >>> from folpy.examples.lattices import *
        >>> model_to_lattice(N5).join_irreducibles()
        [1, 2, 3]
        """
        return [a for a in self.universe if self.is_meet_irreducible(a)]


class Sublattice(Lattice, Subalgebra):
    """
    Clase para subreticulados
    """

    def __init__(self, universe, operations, supermodel):
        assert isinstance(supermodel, Lattice), "supermodel no es un reticulado"
        super().__init__(universe,
                         operations['v'],
                         operations['^'],
                         supermodel)

    @lru_cache(maxsize=1)
    def is_subdirect(self):
        """
        Dado una subreticulado de un producto, decide si es un producto
        subdirecto
        """
        if isinstance(self.supermodel, LatticeProduct):
            for i in self.supermodel.indexes():
                projection = self.supermodel.projection(i)
                natural_embeddingn = projection.composition(
                                                    self.natural_embedding()
                                                    )
                image_set = set(natural_embeddingn.image_model().universe)
                factor_set = set(self.supermodel.factors[i].universe)
                if not image_set == factor_set:
                    return False
            return True
        return False


class LatticeProduct(Product, Lattice):
    """
    Clase para producto de reticulados
    """

    def __init__(self, factors):
        for factor in factors:
            assert isinstance(factor, Lattice), str(factor) + " no es \
                reticulado"
        super().__init__(factors)


class LatticeQuotient(Quotient, Lattice):

    """
    Reticulado Cociente
    Dada un reticulado y una congruencia, devuelve el reticulado cociente
    """

    def __init__(self, supermodel, congruence):
        assert isinstance(supermodel, Lattice), "supermodel no es un reticulado"
        super().__init__(supermodel, congruence)


class Projective(Lattice):

    """
    Clase para representar un proyectivo de congruencias
    """

    def __init__(self,
                 generators,
                 full=False,
                 name="",
                 distributive=None):
        self.generators = list(generators)
        self.algebra = self.generators[0].algebra
        if full:
            universe = self.generators.copy()
        else:
            universe = self.gen_universe()
        join = self.join_operation(universe)
        meet = self.meet_operation(universe)
        super().__init__(universe,
                         join,
                         meet,
                         name=name,
                         distributive=distributive)

    @lru_cache()
    def gen_universe(self):
        universe = self.generators.copy()
        universe.append(self.algebra.maxcon())
        if len(self.generators) > 1:
            for r in range(2, len(self.generators)):
                for titas in combinations(self.generators, r):
                    intersection = self.intersection(titas)
                    if intersection not in universe:
                        universe.append(intersection)
        return universe

    def intersection(self, titas):
        if len(titas) == 0:
            return self.algebra.maxcon()
        elif len(titas) == 1:
            return titas[0]
        else:
            intersection = titas[0]
            for i in range(1, len(titas)):
                intersection = intersection & titas[i]
            return intersection

    def join_operation(self, universe):
        return Operation(lambda x, y: min(
            [t for t in universe if (t >= x and t >= y)]), universe)

    def meet_operation(self, universe):
        return Operation(lambda x, y: x & y, universe)


class CongruenceLattice(Projective):

    """
    Clase para representar el reticulado de congruencias
    """

    def __init__(self,
                 congruences,
                 name="",
                 distributive=None):
        super().__init__(congruences,
                         full=True,
                         name=name,
                         distributive=distributive)

    def join_operation(self, universe):
        return Operation(lambda x, y: x | y, universe)


def model_to_lattice(model):
    """
    convierte un modelo o algebra que es un reticulado, al tipo Lattice
    """
    assert '^' in model.operations
    assert 'v' in model.operations
    return Lattice(
        model.universe,
        model.operations['v'],
        model.operations['^'],
        name=model.name
        )


if __name__ == "__main__":
    import doctest
    doctest.testmod()
