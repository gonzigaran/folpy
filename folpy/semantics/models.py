#!/usr/bin/env python
# -*- coding: utf8 -*-

from itertools import chain, product

from ..utils import indent, powerset, minion
from .morphisms import Embedding, Homomorphism
from .modelfunctions import (
    Relation,
    Relation_Product,
    Operation_Product,
    Constant
)


class Model(object):

    """
    Modelos de algun tipo de primer orden.
    """

    def __init__(self, fo_type, universe, operations, relations, name=""):
        self.type = fo_type
        assert not isinstance(universe, int)
        self.universe = universe
        self.cardinality = len(universe)
        assert set(operations.keys()) >= set(
            fo_type.operations.keys()), "Estan mal definidas las funciones"
        assert set(relations.keys()) >= set(
            fo_type.relations.keys()), "Estan mal definidas las relaciones"
        self.operations = operations
        self.relations = relations
        self.supermodel = self
        self.name = name

    def __repr__(self):
        if self.name:
            return "Model(name= %s)\n" % self.name
        else:
            result = "Model(\n"
            result += indent(repr(self.type) + ",\n")
            result += indent(repr(self.universe) + ",\n")
            result += indent(repr(self.operations) + ",\n")
            result += indent(repr(self.relations))
            return result + ")"

    def __eq__(self, other):
        """
        Para ser iguales tienen que tener el mismo tipo
        y el mismo comportamiento en las operaciones/relaciones del tipo
        y el mismo universo
        """
        if set(self.universe) != set(other.universe):
            return False
        if self.type != other.type:
            return False
        for op in self.type.operations:
            if self.operations[op] != other.operations[op]:
                return False
        for rel in self.type.relations:
            if self.relations[rel] != other.relations[rel]:
                return False
        return True

    def __ne__(self, other):
        """
        Triste necesidad para la antiintuitiva logica de python
        'A==B no implica !(A!=B)'
        """
        return not self.__eq__(other)

    def __len__(self):
        return self.cardinality

    def __hash__(self):
        """
        Hash para los modelos de primer orden

        >>> from folpy.examples.posets import *
        >>> hash(gen_chain(2))==hash(gen_chain(3))
        False
        >>> hash(gen_chain(2)*gen_chain(2))==hash(rhombus)
        False
        """
        return hash(frozenset(chain([self.type],
                                    self.universe,
                                    self.operations.items(),
                                    self.relations.items())))

    def __mul__(self, other):
        """
        Calcula el producto entre modelos

        >>> from folpy.examples.posets import *
        >>> c2 = gen_chain(2)
        >>> bool(rhombus.is_isomorphic(c2*c2, rhombus.type))
        True
        """
        return Product([self, other])

    def __pow__(self, exponent):
        """
        Calcula la potencia de un modelo

        >>> from folpy.examples.posets import *
        >>> c2 = gen_chain(2)
        >>> bool((rhombus**2).is_isomorphic(c2**4, rhombus.type))
        True
        """
        return Product([self] * exponent)

    def homomorphisms_to(self, target, subtype, inj=None, surj=None,
                         without=[]):
        """
        Genera todos los homomorfismos de este modelo a target, en el subtype.

        >>> from folpy.examples.posets import *
        >>> c2 = gen_chain(2)
        >>> c3 = gen_chain(3)
        >>> len(c2.homomorphisms_to(c2,c2.type))
        3
        >>> len(c3.homomorphisms_to(c2,c2.type))
        4
        >>> len(rhombus.homomorphisms_to(rhombus,rhombus.type))
        36
        """
        return minion.homomorphisms(self, target, subtype, inj=inj,
                                    surj=surj, without=without)

    def embeddings_to(self, target, subtype, without=[]):
        """
        Genera todos los embeddings de este modelo a target, en el subtype.
        """
        return minion.embeddings(self, target, subtype, without=without)

    def automorphisms(self, subtype, without=[]):
        """
        Genera todos los automorfismos de este modelo, en el subtype.
        """
        return self.isomorphisms_to(self, subtype, without=without)

    def isomorphisms_to(self, target, subtype, without=[]):
        """
        Genera todos los isomorfismos de este modelo a target, en el subtype.
        """
        return minion.isomorphisms(self, target, subtype, without=without)

    def is_homomorphic_image(self, target, subtype, without=[]):
        """
        Si existe, devuelve un homomorfismo de este modelo a target,
        en el subtype;
        Si no, devuelve False
        """
        return minion.is_homomorphic_image(self, target, subtype,
                                           without=without)

    def is_substructure(self, target, subtype, without=[]):
        """
        Si existe, devuelve un embedding de este modelo a target,
        en el subtype;
        Si no, devuelve False
        """
        return minion.is_substructure(self, target, subtype, without=without)

    def is_isomorphic(self, target, subtype, without=[]):
        """
        Si existe, devuelve un isomorfismo de este modelo a target,
        en el subtype;
        Si no, devuelve False
        """
        return minion.is_isomorphic(self, target, subtype, without=without)

    def is_isomorphic_to_any(self, targets, subtype, without=[]):
        """
        Si lo es, devuelve el primer isomorfismo encontrado desde este
        modelo a alguno en targets, en el subtype;
        Si no, devuelve False
        """
        return minion.is_isomorphic_to_any(self, targets, subtype,
                                           without=without)

    def subuniverse(self, subset, subtype):
        """
        Devuelve el subuniverso generado por subset para el subtype
        y devuelve una lista con otros conjuntos que tambien hubieran
        generado el mismo subuniverso

        >>> from folpy.examples.lattices import *
        >>> rhombus.subuniverse([1],rhombus.type)
        ([1], [[1]])
        >>> rhombus.subuniverse([1,2],rhombus.type)[0]
        [0, 1, 2, 3]
        >>> rhombus.subuniverse([1,2],rhombus.type.subtype(["^"],[]))[0]
        [1, 2, 3]
        """
        result = subset
        result.sort()
        partials = [list(subset)]
        increasing = True
        while increasing:
            increasing = False
            for op in subtype.operations:
                for x in product(result, repeat=self.operations[op].arity()):
                    elem = self.operations[op](*x)
                    if elem not in result and elem in self.universe:
                        result.append(elem)
                        result.sort()
                        partials.append(list(result))
                        increasing = True

        return (result, partials)

    def subuniverses(self, subtype):
        """
        NO DEVUELVE EL SUBUNIVERSO VACIO
        Generador que va devolviendo los subuniversos.
        Intencionalmente no filtra por isomorfismos.

        >>> from folpy.examples.lattices import *
        >>> len(list(rhombus.subuniverses(rhombus.type)))
        12
        """
        result = []
        subsets = powerset(self.universe)
        checked = [[]]
        for subset in subsets:
            if subset not in checked:
                subuniverse, partials = self.subuniverse(subset, subtype)
                for partial in partials:
                    checked.append(partial)
                if subuniverse not in result:
                    result.append(subuniverse)
                    yield subuniverse

    def restrict(self, subuniverse, subtype):
        """
        Devuelve la restriccion del modelo al subuniverso que se supone
        que es cerrado en en subtype
        """
        return Submodel(subtype, subuniverse,
                        {
                            op: self.operations[op].restrict(subuniverse)
                            for op in self.operations
                        },
                        {
                            rel: self.relations[rel].restrict(subuniverse)
                            for rel in self.relations
                        },
                        self)

    def substructure(self, subuniverse, subtype):
        """
        Devuelve una subestructura y un embedding.
        """
        substructure = self.restrict(subuniverse, subtype)
        emb = Embedding(
            {(k,): k for k in subuniverse}, substructure, self, subtype)
        return (emb, substructure)

    def substructures(self, subtype, without=[]):
        """
        Generador que va devolviendo las subestructuras.
        Intencionalmente no filtra por isomorfismos.
        Devuelve una subestructura y un embedding.
        No devuelve las subestructuras cuyos universos estan en without.

        >>> from folpy.examples.lattices import *
        >>> len(list(rhombus.substructures(rhombus.type)))
        12
        >>> len(list(rhombus.substructures(rhombus.type.subtype(["v"],[]))))
        13
        >>> len(list(rhombus.substructures(rhombus.type.subtype([],[]))))
        15
        """
        without = list(map(set, without))
        for sub in self.subuniverses(subtype):
            if set(sub) not in without:
                # parece razonable que el modelo de una subestructura conserve
                # todas las relaciones y operaciones
                # independientemente de el subtipo del que se buscan
                # embeddings.
                yield self.substructure(sub, subtype)

    def join_to_le(self):
        """
        Genera una relacion <= a partir de v
        Solo si no tiene ninguna relacion "<="

        >>> from folpy.examples.lattices import *
        >>> rhombus.join_to_le()
        >>> rhombus.relations["<="]
        Relation(
          [0, 0],
          [0, 1],
          [0, 2],
          [0, 3],
          [1, 1],
          [1, 3],
          [2, 2],
          [2, 3],
          [3, 3],
        )
        """
        if "<=" not in self.relations:
            def leq(x, y):
                return self.operations["v"](x, y) == x
            self.relations["<="] = Relation(leq, self.universe, arity=2)

    def diagram(self, c, s=0):
        """
        Devuelve el diagrama de la estructura con el prefijo c y con un
        shift de s.
        """
        result = []
        for x, y in product(self.universe, repeat=2):
            result += ["-(%s%s=%s%s)" % (c, x + s, c, y + s)]
        for op in self.operations:
            if self.operations[op].arity() == 0:
                result += ["(%s=%s%s)" % (op, c, self.operations[op]() + s)]
            else:
                for x, y, z in iter(self.operations[op].table()):
                    result += ["%s%s %s %s%s = %s%s" %
                               (c, x + s, op, c, y + s, c, z + s)]
        for rel in self.relations:
            for x, y in product(self.universe, repeat=2):
                if self.relations[rel](x, y):
                    result += ["(%s%s %s %s%s)" % (c, x + s, rel, c, y + s)]
                else:
                    result += ["-(%s%s %s %s%s)" % (c, x + s, rel, c, y + s)]
        return result

    def continous(self):
        """
        Devuelve un modelo isomorfo pero de universo [0..n]
        """
        translation = list(self.universe)
        universe = list(range(len(translation)))

        operations = {}
        for op in self.operations:
            operations[op] = self.operations[op].rename(translation)

        relations = {}
        for rel in self.relations:
            relations[rel] = self.relations[rel].rename(translation)

        return (Model(self.type, universe, operations, relations), translation)


class Submodel(Model):

    """
    Submodelos de algun tipo de primer orden.
    """

    def __init__(self, fo_type, universe, operations, relations, supermodel):
        super().__init__(fo_type, universe, operations, relations)
        self.supermodel = supermodel

    def __repr__(self):
        result = "Submodel(\n"
        result += indent(repr(self.type) + ",\n")
        result += indent(repr(self.universe) + ",\n")
        result += indent(repr(self.operations) + ",\n")
        result += indent(repr(self.relations) + ",\n")
        result += indent("supermodel= " + repr(self.supermodel) + "\n")
        return result + ")"

    def natural_embedding(self):
        """
        Genera el Embedding natural entre el submodelo y el modelo
        """
        d = {(x,): x for x in self.universe}
        return Embedding(d, self, self.supermodel, self.type)


class Product(Model):

    def __init__(self, factors):
        """
        Toma una lista de factores
        """
        # TODO falta un armar las operaciones y relaciones
        for factor in factors:
            if isinstance(factor, Product):
                factors.remove(factor)
                factors += factor.factors
        self.factors = factors

        fo_type = factors[0].type
        if any(f.type != fo_type for f in factors):
            raise ValueError("Factors must be all from same type")

        d_universe = list(product(*[f.universe for f in factors]))

        operations = {}
        for op in fo_type.operations:
            if fo_type.operations[op] == 0:
                constant_list = [f.operations[op]() for f in factors]
                operations[op] = Constant(tuple(constant_list))
            else:
                operations_list = [f.operations[op] for f in factors]
                universe = [f.universe for f in factors]
                operations[op] = Operation_Product(operations_list, universe)

        relations = {}
        for rel in fo_type.relations:
            relations_list = [f.relations[rel] for f in factors]
            universe = [f.universe for f in factors]
            relations[rel] = Relation_Product(relations_list, universe)

        super().__init__(fo_type, d_universe, operations, relations)

    def projection(self, i):
        """
        Genera el morfismo que es la proyección en la coordenada i
        """
        assert i in self.indexes()
        d = {(x,): x[i] for x in self.universe}
        return Homomorphism(d, self, self.factors[i], self.type, surj=True)

    def indexes(self):
        return list(range(len(self.factors)))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
