#!/usr/bin/env python
# -*- coding: utf8 -*-

from itertools import product, chain
import copy
import inspect

from .misc import indent, compose


class Function(object):

    r"""
    Define el arreglo n dimensional que se usan para tener operaciones y
     relaciones n-arias.
    Necesariamente toma numeros desde 0
    Tambien puede tomar una función directamente

    Args:
        d (dict): función en tipo dict, list o calleable
        arity (int): Aridad de la función
        d_universe (list): Universo del dominio
    Attributes:
        func (callable): función en tipo calleable
        dict (dict): función en tipo dict
        d_universe (list): Universo del dominio
        arityval (int): Aridad de la función
        relation (bool): Define si es una función o una relación (función
     booleana)

    >>> sum_mod3=Function({
    ... (0,0):0,
    ... (0,1):1,
    ... (0,2):2,
    ... (1,0):1,
    ... (1,1):2,
    ... (1,2):0,
    ... (2,0):2,
    ... (2,1):0,
    ... (2,2):1,})
    >>> sum_mod3mas3=Function({(0,0):3,
    ... (0,1):4,
    ... (0,2):5,
    ... (1,0):4,
    ... (1,1):5,
    ... (1,2):3,
    ... (2,0):5,
    ... (2,1):3,
    ... (2,2):4,})
    >>> sum_mod3.table() #doctest: +ELLIPSIS
    [[0, 0, 0], [0, 1, 1], [0, 2, 2], ... [2, 0, 2], [2, 1, 0], [2, 2, 1]]
    >>> sum_mod3
    Function(
      [0, 0] -> 0,
      [0, 1] -> 1,
      [0, 2] -> 2,
      [1, 0] -> 1,
      [1, 1] -> 2,
      [1, 2] -> 0,
      [2, 0] -> 2,
      [2, 1] -> 0,
      [2, 2] -> 1,
    )

    >>> sorted(list(sum_mod3.domain()))
    [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]

    >>> sum_mod3.arity()
    2

    >>> sum_mod3 == sum_mod3mas3
    False
    >>> sum_mod3.map_in_place(lambda x: x+3)
    >>> sum_mod3 == sum_mod3mas3
    True
    >>> sum_mod3(1,2)
    3

    >>> sum_mod3(2,2)
    4

    >>> sum_mod3.table() #doctest: +ELLIPSIS
    [[0, 0, 3], [0, 1, 4], [0, 2, 5], ..., [2, 2, 4]]
    >>> sum_mod3=Function(lambda x,y:(x+y)%3,d_universe=[0,1,2])
    >>> sum_mod3.table() #doctest: +ELLIPSIS
    [[0, 0, 0], [0, 1, 1], [0, 2, 2], [1, 0, 1], ..., [2, 1, 0], [2, 2, 1]]
    >>> sum_mod3
    Function(
      [0, 0] -> 0,
      [0, 1] -> 1,
      [0, 2] -> 2,
      [1, 0] -> 1,
      [1, 1] -> 2,
      [1, 2] -> 0,
      [2, 0] -> 2,
      [2, 1] -> 0,
      [2, 2] -> 1,
    )

    >>> sorted(list(sum_mod3.domain()))
    [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2), (2, 0), (2, 1), (2, 2)]

    >>> sum_mod3.arity()
    2

    >>> sum_mod3 == sum_mod3mas3
    False
    >>> sum_mod3.map_in_place(lambda x: x+3)
    >>> sum_mod3 == sum_mod3mas3
    True
    >>> sum_mod3(1,2)
    3

    >>> sum_mod3(2,2)
    4

    >>> sum_mod3.table() #doctest: +ELLIPSIS
    [[0, 0, 3], [0, 1, 4], [0, 2, 5], [1, 0, 4], ..., [2, 1, 3], [2, 2, 4]]
    """

    def __init__(self, d, arity=None, d_universe=None):
        # assert issubclass(type(l),list)
        self.func = None
        self.dict = None
        self.d_universe = d_universe
        if callable(d):
            assert d_universe, d_universe
            self.func = d
        elif isinstance(d, list):
            self.dict = self.__list_to_dict(d)
        else:
            self.dict = d
        if self.dict:
            assert all(isinstance(t, tuple) for t in list(self.dict.keys()))
        if arity:
            self.arityval = arity
        else:
            if self.func:
                # la aridad es la aridad de func
                self.arityval = len(inspect.getfullargspec(self.func).args)
            else:
                try:
                    self.arityval = len(list(self.dict.keys())[0])
                except IndexError:
                    raise ValueError("Arity is not defined")
                if not all(len(k) == self.arityval for k in self.dict.keys()):
                    raise ValueError("Inconsistent arity")

        self.relation = False  # maneja si la funcion es booleana
        if not self.d_universe:
            self.d_universe = list(set(chain(*list(self.domain()))))

    def __call__(self, *args):
        if not len(args) == self.arity():
            raise ValueError(
                "Arity is %s, not %s. Do you need use vector_call?"
                % (self.arity(), len(args)))
        try:
            if self.func:
                if all(x in self.d_universe for x in args):
                    result = self.func(*args)
                else:
                    raise KeyError
            else:
                result = self.dict[args]
        except KeyError:
            if self.relation and all(x in self.d_universe for x in args):
                return False
            raise ValueError("Value '%s' not in domain of '%s'"
                             % (str(args), repr(self)))

        if self.relation:
            return bool(result)
        else:
            return result

    def __lasfen__(self):
        """
        Devuelve la cardinalidad del conjunto de partida.
        """
        return len(self.array)

    def __eq__(self, other):
        """
        Dos funciones son iguales si tienen el mismo dominio y el mismo
         comportamiento.
        """
        if self.func:
            return frozenset(map(tuple, self.table())) ==\
                 frozenset(map(tuple, other.table()))
        else:
            # basta con revisar el arreglo, ya que contiene el dominio y el
            # comportamiento
            return self.dict == other.dict

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        """
        Hash de las funciones para manejar funciones en conjuntos.
        No es muy rapida.
        >>> f=Function({(0,0):0,
        ...  (0,1):1,
        ...  (0,2):2,
        ...  (1,0):1,
        ...  (1,1):2, (1,2):0, (2,0):2, (2,1):0, (2,2):1,})
        >>> g=Function({(2,0):2,
        ...  (0,1):1,
        ...  (0,2):2,
        ...  (1,0):1, (0,0):0, (1,1):2, (1,2):0, (2,1):0, (2,2):1,})
        >>> h=Function({(2,0):1,
        ...  (0,1):1,
        ...  (0,2):2,
        ...  (1,0):1, (0,0):0, (1,1):2, (1,2):0, (2,1):0, (2,2):1,})
        >>> hash(f)==hash(g)
        True
        >>> hash(f)==hash(h)
        False
        """
        if self.func:
            return hash(frozenset(chain(self.d_universe, [self.func])))
        else:
            return hash(frozenset(self.dict.items()))

    def __repr__(self):
        if self.relation:
            result = "Relation(\n"
            table = ["%s," % x for x in self.table()]
        else:
            if self.arity():
                result = "Function(\n"
                table = ["%s -> %s," %
                         (x[:-1], x[-1]) for x in self.table()]
            else:
                result = "Constant(\n"
                table = str(self.table()[0][0])

        if len(table) > 10:
            table = table[:5] + [".", ".", "."] + table[-5:]
        table = indent("\n".join(table))

        return result + table + ")"

    def __iter__(self):
        """
        Vuelve a las funciones iterables a partir de su grafico
        o a las relaciones directamente desde su conjunto de tuplas.
        """
        return iter(self.table())

    def copy(self):
        """
        Devuelve una copia de si mismo
        """
        result = copy.copy(self)
        if self.func:
            result.d_universe = list(result.d_universe)
        else:
            result.dict = self.dict.copy()
        return result

    def domain(self):
        """
        Un generador del dominio
        """
        if self.relation or self.func:
            return product(self.d_universe, repeat=self.arity())
        else:
            return iter(self.dict.keys())

    def image(self):
        """
        Un generador de la imagen
        """
        if self.func:
            return iter(set(self.func(*t) for t in self.domain()))
        else:
            return iter(set(self.dict.values()))

    def arity(self):
        """
        Devuelve la aridad de la funcion, revisando la 'primer' tupla del
         diccionario.
        """
        return self.arityval

    def map_in_place(self, f):
        """
        Funciona como un map, pero respeta la estructura de la matriz.
        """
        if self.func:
            self.func = compose(f, self.func)
        else:
            self.dict = self.dict.copy()
            for key in self.dict:
                self.dict[key] = f(self.dict[key])

    def restrict(self, subuniverse):
        """
        Restringe la funcion a un subconjunto.
        """

        result = self.copy()
        if result.func:
            result.d_universe = subuniverse
        else:
            for t in self.dict:
                if any(e not in subuniverse for e in t):
                    del result.dict[t]
        return result

    def vector_call(self, vector):
        """
        Aplica la funcion a un vector de elementos del dominio.
        """
        return type(vector)(list(map(self, vector)))

    def table(self):
        """
        Devuelve una lista de listas con la tabla que representa a la
         relacion/operacion
        """
        if self.func:
            result = sorted((t, self.func(*t)) for t in self.domain())
        else:
            result = sorted(self.dict.items())
        if self.relation:
            result = [k_v for k_v in result if k_v[1]]
            result = [list(k_v1[0]) for k_v1 in result]
        else:
            result = [list(k_v2[0]) + [k_v2[1]] for k_v2 in result]
        return result

    def __list_to_dict(self, matrix):
        """
        Convierte una matriz del modo anterior de generar funciones en
         un diccionario
        """
        from itertools import product
        import numpy as np
        matrix = np.array(matrix, dtype=np.dtype(object))
        arity = matrix.ndim
        result = {}
        for t in product(list(range(len(matrix))), repeat=arity):
            if matrix.item(*t) is not None:
                result[t] = matrix.item(*t)
        return result


if __name__ == "__main__":
    import doctest
    doctest.testmod()
