#!/usr/bin/env python
# -*- coding: utf8 -*-

from ..utils import indent
from ..syntax.types import AlgebraicType

from .algebras import Algebra, Subalgebra, Quotient
from .models import Product


class Lattice(Algebra):

    """
    Clase para representar Reticulados, como un algebra con operaciones
    especificas
    """

    def __init__(self, universe, supreme, infimum, name="", distributive=None):
        fo_type = AlgebraicType({"^": 2, "v": 2})
        operations = {}
        operations["^"] = supreme
        operations["v"] = infimum
        super().__init__(fo_type, universe, operations, name)
        self.distributive = distributive

    def __repr__(self):
        if self.name:
            return "Lattice(name= %s)\n" % self.name
        else:
            result = "Lattice(\n"
            result += indent(repr(self.universe) + ",\n")
            result += indent(repr(self.operations))
            return result + ")"

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

    def continous(self):
        """
        Devuelve un álgebra isomorfa pero de universo [0..n]
        """
        translation = list(self.universe)
        universe = list(range(len(translation)))

        operations = {}
        for op in self.operations:
            operations[op] = self.operations[op].rename(translation)

        return (Lattice(self.type,
                        universe,
                        self.operations['^'],
                        self.operations['v']), translation)

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

    def is_distributive(self):
        """
        Decide si un reticulado es distributivo
        """
        if self.distributive:
            return self.distributive
        return "ToDo"


class Sublattice(Subalgebra, Lattice):
    """
    Clase para subreticulados
    """

    def __init__(self, universe, operations, supermodel):
        assert isinstance(supermodel, Lattice), "supermodel no es un reticulado"
        super().__init__(supermodel.type,
                         universe,
                         operations,
                         supermodel)

    def __repr__(self):
        result = "Sublattice(\n"
        result += indent(repr(self.universe) + ",\n")
        result += indent(repr(self.operations) + ",\n")
        result += indent("supermodel= " + repr(self.supermodel) + "\n")
        return result + ")"

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

    def __repr__(self):
        result = "LatticeQuotient(\n"
        result += indent(repr(self.universe) + ",\n")
        result += indent(repr(self.operations) + ",\n")
        result += indent("congruence= " + repr(self.congruence) + "\n")
        return result + ")"


if __name__ == "__main__":
    import doctest
    doctest.testmod()
