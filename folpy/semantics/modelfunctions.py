#!/usr/bin/env python
# -*- coding: utf8 -*-

from itertools import product

from ..utils import Function


class Operation(Function):

    r"""
    Operacion de primer orden
    """

    def __init__(self, d, d_universe=None, arity=None):
        super().__init__(d, d_universe=d_universe, arity=arity)
        self.relation = False

    def graph_fo_relation(self, universe):
        """
        Genera la relacion dada por el grafico de la funcion en el universo
        """
        return Relation([tuple(row) for row in self.table()], universe)

    def rename(self, renames):
        """
        Devuelve una nueva operacion reemplazando elementos del universo
        """
        def operation(*args):
            args = [renames[i] for i in args]
            result = self(*args)
            try:
                return renames.index(result)
            except e as e:
                # TODO esto no tiene sentido
                # hace falta porque a veces una subestructura no
                # es subestructura con alguna funcion,
                # y hay que poder traducirla
                return result

        return Operation(operation,
                         d_universe=list(range(len(renames))),
                         arity=self.arity())


class Relation(Function):

    r"""
    Relacion de primer orden

    >>> par = Relation({(0,):1,(1,):0,(2,):1,(3,):0,(4,):1},range(4))
    >>> par(2)
    True
    >>> par(3)
    False
    >>> par.table()
    [[0], [2], [4]]
    """

    def __init__(self, d, d_universe=None, arity=None):
        if d and isinstance(d, list) and isinstance(d[0], tuple):
            d = {k: True for k in d}
        assert d_universe
        super().__init__(d, d_universe=d_universe, arity=arity)
        self.d_universe = d_universe
        self.relation = True

    def rename(self, renames):
        """
        Devuelve una nueva operacion reemplazando elementos del universo
        """
        def relation(*args):
            args = [renames[i] for i in args]
            result = self(*args)
            return result

        return Relation(relation,
                        d_universe=list(range(len(renames))),
                        arity=self.arity())


def Constant(value):
    """
    Facilita la definicion de una operacion 0-aria para constantes
    """
    return Operation({(): value})


def Operation_Product(operations, d_universes):
    """
    Toma una lista de operaciones y de universos
    y devuelve la operacion en el producto de universos
    coordenada a coordenada
    """
    @Operation_decorator(list(product(*d_universes)), operations[0].arity())
    def product_op(*args):
        result = []
        for i, t in enumerate(zip(*args)):
            result.append(operations[i](*t))
        return tuple(result)

    return product_op


def Relation_Product(relations, d_universes):
    """
    Toma una lista de relaciones y de universos
    y devuelve la relacion en el producto de universos
    coordenada a coordenada
    """
    @Relation_decorator(list(product(*d_universes)), relations[0].arity())
    def product_rel(*args):
        result = []
        for i, t in enumerate(zip(*args)):
            result.append(relations[i](*t))
        return all(result)

    return product_rel


# decorators

def Operation_decorator(d_universe, arity=None):
    """
    Decorador para definir facilmente operaciones de primer orden
    con funciones en Python
    """
    def wrap(f):
        return Operation(f, d_universe=d_universe, arity=arity)
    return wrap


def Relation_decorator(d_universe, arity=None):
    """
    Decorador para definir facilmente relaciones de primer orden
    con funciones en Python
    """
    def wrap(f):
        return Relation(f, d_universe=d_universe, arity=arity)
    return wrap


if __name__ == "__main__":
    import doctest
    doctest.testmod()
