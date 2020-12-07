#!/usr/bin/env python
# -*- coding: utf8 -*-

from itertools import chain, permutations, combinations
from functools import lru_cache

from ..utils import indent
from .models import Model, Submodel, Product
from .morphisms import Homomorphism
from .modelfunctions import Operation, Constant
from .congruences import Congruence, Partition


class Algebra(Model):

    """
    Clase para representar Algebras, como un modelo que no tiene relaciones
    """

    def __init__(self, fo_type, universe, operations, name=""):
        super().__init__(fo_type, universe, operations, {}, name)

    def __hash__(self):
        """
        Hash para los modelos de primer orden

        >>> from folpy.examples.lattices import *
        >>> hash(gen_chain(2))==hash(gen_chain(3))
        False
        >>> hash(gen_chain(2)*gen_chain(2))==hash(rhombus)
        False
        """
        algebra_chain = chain(
            [self.type],
            self.universe,
            self.operations.items()
            )
        return hash(frozenset(algebra_chain))

    def __mul__(self, other):
        """
        Calcula el producto entre álgebras

        >>> from folpy.examples.lattices import gen_chain, rhombus
        >>> c2 = gen_chain(2)
        >>> bool(rhombus.is_isomorphic(c2*c2,rhombus.type))
        True
        """
        return AlgebraProduct([self, other])

    def __pow__(self, exponent):
        """
        Calcula la potencia de un álgebra

        >>> from folpy.examples.lattices import gen_chain, rhombus
        >>> c2 = gen_chain(2)
        >>> bool(rhombus.is_isomorphic(c2**2,rhombus.type))
        True
        """
        return AlgebraProduct([self] * exponent)

    def continous(self):
        """
        Devuelve un álgebra isomorfa pero de universo [0..n]
        """
        translation = list(self.universe)
        universe = list(range(len(translation)))

        operations = {}
        for op in self.operations:
            operations[op] = self.operations[op].rename(translation)

        return (Algebra(self.type, universe, operations), translation)

    def maxcon(self):
        """
        Función que devuelve la congruencia máxima del reticulado de
        congruencias. (la congruencia en donde todos los elementos están
        relacionados con todos)
        """
        universe = [(x, y) for x in self.universe for y in self.universe]
        return Congruence(universe, self)

    def mincon(self):
        """
        Función que devuelve la congruencia mínima del reticulado de
        congruencias. (la congruencia en donde cada elemento está relacionado
        solo consigo mismo)
        """
        universe = [(x, x) for x in self.universe]
        return Congruence(universe, self)

    def principal_congruences(self):
        """
        Función que devuelve el conjunto de las congruencias principales del
        álgebra
        """
        result = []
        order = []
        unary_polynomials = self.unary_polynomials()
        for (a, b) in combinations(self.universe, 2):
            congruence = self.principal_congruence(a, b, unary_polynomials)
            n = len(result)
            order_n = []
            congruence_in = False
            for i in range(n):
                le = result[i] <= congruence
                ge = result[i] >= congruence
                if le:
                    if ge:
                        congruence_in = True
                        break
                    else:
                        order_n.append((i, n))
                if ge:
                    order_n.append((n, i))
            if not congruence_in:
                order = order + order_n
                result.append(congruence)

        return (result, order)

    def principal_congruence(self, a, b, unary_polynomials=None):
        """
        Función que devuelve la congruencia principal para el par (a,b).
        """
        pairs = [(a, b)]
        partition = Partition()
        for x in self.universe:
            partition.add_element(x)
        partition.join_blocks(a, b)
        if not unary_polynomials:
            unary_polynomials = self.unary_polynomials()
        while pairs:
            (x, y) = pairs.pop()
            for poly in unary_polynomials:
                r = partition.root(unary_polynomials[poly](x))
                s = partition.root(unary_polynomials[poly](y))
                if s != r:
                    partition.join_blocks(r, s)
                    pairs.append((r, s))
        con = partition.to_congruence(self)
        return con

    def unary_polynomials(self):
        """
        Genera el conjunto de todos los polinomios unarios de operaciones del
        álgebra
        """
        unary_polynomials = {}
        for op_name in self.operations:
            op = self.operations[op_name]
            if op.arity() == 1:
                unary_polynomials[op_name] = op
            else:
                arity = op.arity()
                for j in range(arity):
                    for vector in permutations(self.universe, arity - 1):
                        name = op_name + "_" + str(j) + str(vector)
                        poly = self.unary_polynomial(op_name, j, vector)
                        unary_polynomials[name] = poly
        return unary_polynomials

    def unary_polynomial(self, op_name, j, vector):
        """
        Genera el polinomio unario del álgebgra para la operación `op_name` y
        el vector `vector` (tiene que tener ancho = aridad de `op_name` - 1).
        La variable está en el lugar `j`
        """
        op = self.operations[op_name]

        def poly(x):
            return op(*vector[0:j], x, *vector[j:])
        return poly

    def atoms_congruence_lattice(self):
        """
        Devuelve los atomos del reticulado de congruencia, a partir de los
        minimales del conjunto de congruencias principales
        """
        (principal_congruences, order) = self.principal_congruences()
        minimals_idx = []
        for (a, b) in order:
            if a not in minimals_idx:
                minimals_idx.append(a)
            if b in minimals_idx:
                minimals_idx.remove(b)
        return [principal_congruences[i] for i in minimals_idx]

    def belongs(self, Q):
        """
        Dada una cuasivariedad Q, se fija si el álgebra pertenece a Q. En caso
        de pertenecer, devuelve el morfismo que de la representacion con las
        relativamente subdirectamente irreducibles.
        """
        return Q.contains(self)

    def congruences_in(self, factors):
        """
        Dado un conjunto de álgebras ´factors´, devuelve todas las congruencias
        tal que el cociente de ´self´ con esas congruencias es isomorfo a algún
        factor

        >>> from folpy.examples.lattices import gen_chain, rhombus
        >>> len(rhombus.congruences_in([gen_chain(2)]))
        2
        """
        congruences = []
        for factor in factors:
            homomorphisms = self.homomorphisms_to(factor,
                                                  surj=True)
            for homomorphism in homomorphisms:
                con = homomorphism.kernel()
                if con not in congruences:
                    congruences.append(con)
        return congruences

    def congruences(self):
        """
        Devuelve todas las congruencias del algebra

        >>> from folpy.examples.lattices import gen_chain, rhombus
        >>> len(gen_chain(2).congruences())
        2
        >>> len(gen_chain(3).congruences())
        4
        >>> len(gen_chain(4).congruences())
        8
        >>> len(rhombus.congruences())
        4
        """
        (principal_congruences, principal_congruences_order) = \
            self.principal_congruences()
        n_principal_congruences = len(principal_congruences)
        new_congruences = principal_congruences.copy()
        new_congruences_ix = [[i] for i in range(n_principal_congruences)]
        congruences = principal_congruences.copy()
        congruences.append(self.mincon())
        while new_congruences:
            new_new_congruences = []
            new_new_congruences_ix = []
            for k in range(len(new_congruences_ix)):
                idx = new_congruences_ix[k]
                last_index = idx[-1]
                for i in range(last_index + 1, n_principal_congruences):
                    if any((i, j) in principal_congruences_order for j in idx):
                        continue
                    congruence = new_congruences[k]
                    new_congruence = congruence | principal_congruences[i]
                    if new_congruence not in congruences:
                        congruences.append(new_congruence)
                        new_new_congruences.append(new_congruence)
                        new_new_congruences_ix.append(idx + [i])
            new_congruences = new_new_congruences
            new_congruences_ix = new_new_congruences_ix
        return congruences

    def congruence_lattice(self):
        """
        Devuelve el reticulado de congruencias

        >>> from folpy.examples.lattices import rhombus
        >>> len(rhombus.congruence_lattice())
        4
        """
        from .lattices import CongruenceLattice
        return CongruenceLattice(self.congruences())

    def restrict(self, subuniverse, subtype=None):
        """
        Devuelve la restriccion del algebra al subuniverso que se supone
        que es cerrado en en subtype
        """
        if not subtype:
            subtype = self.type
        return Subalgebra(subtype, subuniverse,
                          {
                              op: self.operations[op].restrict(subuniverse)
                              for op in self.operations
                          },
                          self)


class Subalgebra(Submodel, Algebra):
    """
    Clase para subalgebras
    """

    def __init__(self, fo_type, universe, operations, supermodel):
        assert isinstance(supermodel, Algebra), "supermodel no es un algebra"
        super().__init__(
            fo_type, universe, operations, {}, supermodel)

    @lru_cache(maxsize=1)
    def is_subdirect(self):
        """
        Dado una subalgebra de un producto, decide si es un producto subdirecto
        """
        if isinstance(self.supermodel, AlgebraProduct):
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


class AlgebraProduct(Product, Algebra):
    """
    Clase para Producto de álgebras
    """

    def __init__(self, factors):
        for factor in factors:
            assert isinstance(factor, Algebra), str(factor) + " no es algebra"
        super().__init__(factors)


class Quotient(Algebra):

    """
    Algebra Cociente
    Dada un algebra y una congruencia, devuelve el álgebra cociente
    """

    def __init__(self, supermodel, congruence):
        assert isinstance(supermodel, Algebra), "supermodel no es un algebra"
        universe = list(congruence.roots())
        operations = {}
        for op in supermodel.operations:
            ope = supermodel.operations[op].restrict(universe)
            d = {}
            if supermodel.operations[op].arity() != 0:
                for i in list(ope.domain()):
                    if not ope(*i) in universe:
                        for j in universe:
                            if congruence(ope(*i), j):
                                d[i] = j
                                break
                    else:
                        d[i] = ope(*i)
                operations[op] = Operation(d, universe, ope.arity())
            else:
                for j in universe:
                    if congruence(ope(), j):
                        operations[op] = Constant(j)
                        break
        super().__init__(supermodel.type, universe, operations)
        self.congruence = congruence
        self.supermodel = supermodel

    def __repr__(self):
        result = self.class_name + "(\n"
        result += indent(repr(self.type) + ",\n")
        result += indent(repr(self.universe) + ",\n")
        result += indent(repr(self.operations) + ",\n")
        result += indent("congruence= " + repr(self.congruence) + "\n")
        return result + ")"

    def natural_map(self):
        """
        Devuelve el mapa natural entre el álgebra y el cociente
        """
        d = {}
        for x in self.supermodel.universe:
            for y in self.universe:
                if self.congruence(x, y):
                    d[(x,)] = y
                    break
        return Homomorphism(d, self.supermodel, self, self.type, surj=True)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
