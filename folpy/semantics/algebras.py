#!/usr/bin/env python
# -*- coding: utf8 -*-

from itertools import chain

from ..utils import indent
from .models import Model, Submodel, Product
from .morphisms import Homomorphism
from .modelfunctions import Operation, Constant
from .congruences import Congruence


class Algebra(Model):

    """
    Clase para representar Algebras, como un modelo que no tiene relaciones
    """

    def __init__(self, fo_type, universe, operations, name=""):
        super().__init__(fo_type, universe, operations, {})

    def __repr__(self):
        if self.name:
            return "Algebra(name= %s)\n" % self.name
        else:
            result = "Algebra(\n"
            result += indent(repr(self.type) + ",\n")
            result += indent(repr(self.universe) + ",\n")
            result += indent(repr(self.operations))
            return result + ")"

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
        """
        congruences = []
        for factor in factors:
            homomorphisms = self.homomorphisms_to(factor,
                                                  factor.type,
                                                  surj=True)
            for homomorphism in homomorphisms:
                con = homomorphism.kernel()
                if con not in congruences:
                    congruences.append(con)
        return congruences

    def restrict(self, subuniverse, subtype):
        """
        Devuelve la restriccion del algebra al subuniverso que se supone
        que es cerrado en en subtype
        """
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

    def __repr__(self):
        result = "Subalgebra(\n"
        result += indent(repr(self.fo_type) + ",\n")
        result += indent(repr(self.universe) + ",\n")
        result += indent(repr(self.operations) + ",\n")
        result += indent("supermodel= " + repr(self.supermodel) + "\n")
        return result + ")"

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
        result = "Quotient(\n"
        result += indent(repr(self.fo_type) + ",\n")
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
