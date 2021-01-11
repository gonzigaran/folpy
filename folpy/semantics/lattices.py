#!/usr/bin/env python
# -*- coding: utf8 -*-

from itertools import product
from functools import lru_cache

from ..syntax.types import AlgebraicType
from ..utils import latdraw

from .algebras import Algebra, Subalgebra, Quotient, AlgebraProduct
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
        self.join_dic = {(x, x): x for x in self.universe}
        self.meet_dic = {(x, x): x for x in self.universe}

    def __mul__(self, other):
        """
        Calcula el producto entre reticulados

        >>> from folpy.examples.lattices import *
        >>> c2 = model_to_lattice(gen_chain(2))
        >>> rhom = c2*c2
        >>> len(rhom)
        4
        """
        return LatticeProduct([self, other])

    def __pow__(self, exponent):
        """
        Calcula la potencia de un álgebra

        >>> from folpy.examples.lattices import *
        >>> c2 = model_to_lattice(gen_chain(2))
        >>> rhom2 = c2**3
        >>> len(rhom2)
        8
        """
        return LatticeProduct([self] * exponent)

    def join(self, x, y):
        """
        devuelve el supremo de x e y para el reticulado
        """
        if (x, y) not in self.join_dic:
            join = self.operations['v'](x, y)
            self.join_dic[(x, y)] = join
            self.join_dic[(y, x)] = join
            return join
        return self.join_dic[(x, y)]

    def meet(self, x, y):
        """
        devuelve el infimo de x e y para el reticulado
        """
        if (x, y) not in self.meet_dic:
            meet = self.operations['^'](x, y)
            self.meet_dic[(x, y)] = meet
            self.meet_dic[(y, x)] = meet
            return meet
        return self.meet_dic[(x, y)]

    def gt(self, a, b):
        """
        devuelve la relación > para los elementos a y b del reticulado
        """
        return a != b and self.meet(a, b) == b

    def ge(self, a, b):
        """
        devuelve la relación >= para los elementos a y b del reticulado
        """
        return self.meet(a, b) == b

    def lt(self, a, b):
        """
        devuelve la relación < para los elementos a y b del reticulado
        """
        return a != b and self.meet(a, b) == a

    def le(self, a, b):
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

        >>> from folpy.examples.lattices import *
        >>> len(rhombus.restrict([0,3]))
        2
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

    def draw(self):
        return latdraw.LatDraw(self)

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
            if self.gt(b, a):
                if any((self.gt(c, a) and
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
            if self.lt(b, a):
                if any((self.lt(c, a) and
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

    @property
    @lru_cache(maxsize=1)
    def atoms(self):
        """
        Devuelve los atomos del reticulado

        >>> from folpy.examples.lattices import *
        >>> model_to_lattice(rhombus).atoms
        [1, 2]
        """
        return self.covers(self.min())

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
        assert len(self.universe[0]) == len(self.supermodel.factors)
        n = len(self.supermodel.factors)
        if isinstance(self.supermodel, LatticeProduct):
            if all(set([x[i] for x in self.universe]) ==
                   set(self.supermodel.factors[i].universe) for i in range(n)):
                return True
        return False


class LatticeProduct(AlgebraProduct, Lattice):
    """
    Clase para producto de reticulados
    """

    def __init__(self, factors):
        for factor in factors:
            assert isinstance(factor, Lattice), str(factor) + " no es \
                reticulado"
        alg_prod = AlgebraProduct(factors)
        Lattice.__init__(self,
                         alg_prod.universe,
                         alg_prod.operations['v'],
                         alg_prod.operations['^'])
        self.factors = factors


class LatticeQuotient(Quotient, Lattice):

    """
    Reticulado Cociente
    Dada un reticulado y una congruencia, devuelve el reticulado cociente

    >>> from folpy.examples.lattices import *
    >>> rhom = model_to_lattice(rhombus)
    >>> A = LatticeQuotient(rhom, rhom.maxcon())
    >>> len(A)
    1
    >>> A = LatticeQuotient(rhom, rhom.mincon())
    >>> bool(A.is_isomorphic(rhom))
    True
    """

    def __init__(self, supermodel, congruence):
        assert isinstance(supermodel, Lattice), "supermodel no es un reticulado"
        alg_quo = Quotient(supermodel, congruence)
        Lattice.__init__(self,
                         alg_quo.universe,
                         alg_quo.operations['v'],
                         alg_quo.operations['^'])


class Projective(Lattice):

    """
    Clase para representar un proyectivo de congruencias

    >>> from folpy.examples.lattices import *
    >>> tita1 = rhombus.congruences()[1]
    >>> tita2 = rhombus.congruences()[2]
    >>> P = Projective([tita1, tita2])
    >>> len(P)
    3
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
        self.universe = universe
        join = self.join_operation()
        meet = self.meet_operation()
        super().__init__(universe,
                         join,
                         meet,
                         name=name,
                         distributive=distributive)

    def gen_universe(self):
        congruences = self.generators.copy()
        if len(self.generators) > 1:
            new_congruences = congruences.copy()
            n = len(congruences)
            new_congruences_ix = [[i] for i in range(n)]
            while new_congruences:
                new_intersections = []
                new_intersections_ix = []
                for k in range(len(new_congruences_ix)):
                    idx = new_congruences_ix[k]
                    last_index = idx[-1]
                    for i in range(last_index + 1, n):
                        congruence = new_congruences[k]
                        new_congruence = congruence & congruences[i]
                        if new_congruence not in congruences:
                            congruences.append(new_congruence)
                            new_intersections.append(new_congruence)
                            new_intersections_ix.append(idx + [i])
                new_congruences = new_intersections
                new_congruences_ix = new_intersections_ix
        congruences.append(self.algebra.maxcon())
        return congruences

    def join_op(self, x, y):
        return min([t for t in self.universe if (t >= x and t >= y)])

    def meet_op(self, x, y):
        return x & y

    def join_operation(self):
        def function(x, y):
            return self.join_op(x, y)
        return Operation(function, d_universe=self.universe, arity=2)

    def meet_operation(self):
        def function(x, y):
            return self.meet_op(x, y)
        return Operation(function, d_universe=self.universe, arity=2)

    def gt(self, x, y):
        return x > y

    def ge(self, x, y):
        return x >= y

    def lt(self, x, y):
        return x < y

    def le(self, x, y):
        return x <= y


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

    @property
    @lru_cache(maxsize=1)
    def atoms(self):
        return self.algebra.atoms_congruence_lattice()

    def join_op(self, x, y):
        return x | y


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
