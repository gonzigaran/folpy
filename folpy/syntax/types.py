#!/usr/bin/env python
# -*- coding: utf8 -*-

from itertools import chain


class Type(object):
    """
    Maneja tipos de primer orden:
    Teoricamente es una 4-upla (C,F,R,a)
    Toma dos diccionarios con nombres y aridades, el primero para las
    operaciones y el segundo para las relaciones.
    Las constantes se consideran como operaciones 0-arias.

    >>> t = Type({"+":2},{"<":2})
    >>> t
    Type({'+': 2},{'<': 2})
    >>> st = t.subtype(["+"],[])
    >>> st
    Type({'+': 2},{})
    >>> st.is_subtype_of(t)
    True
    >>> suma = Type({'+': 2},{'<': 2}) + Type({'-': 2},{'<=': 2})
    >>> (set(suma.operations.keys()) == {"+","-"},
    ... set(suma.relations.keys()) == {"<","<="})
    (True, True)
    >>> resta = Type({'+': 2, '-': 2},
    ... {'<=': 2, '<': 2}) - Type({'-': 2},{'<=': 2})
    >>> (set(resta.operations.keys()) == {"+"},
    ... set(resta.relations.keys()) == {"<"})
    (True, True)
    """

    def __init__(self, operations, relations):
        self.operations = operations
        self.relations = relations

    def __repr__(self):
        result = "Type({"
        result += ", ".join([("'%s': %s" % x)
                             for x in sorted(self.operations.items())])
        result += "},{"
        result += ", ".join([("'%s': %s" % x)
                             for x in sorted(self.relations.items())])
        result += "})"
        return result

    def __eq__(self, other):
        return (self.operations == other.operations
                and self.relations == other.relations)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __sub__(self, other):
        """
        Resta de tipos, devuelve un nuevo tipo con las rel/op que pertenecen
        a self, pero no a other.
        """
        assert other.is_subtype_of(self), (self, other)
        result = self.copy()
        for op in other.operations:
            del result.operations[op]
        for rel in other.relations:
            del result.relations[rel]
        return result

    def __add__(self, other):
        """
        Suma de tipos, genera un tipo por union de los diccionarios.
        """
        result = self.copy()
        for rel in other.relations:
            assert rel not in result.relations, (rel, self, other)
            result.relations[rel] = other.relations[rel]
        for op in other.operations:
            assert op not in result.operations
            result.operations[op] = other.operations[op]
        return result

    def __hash__(self):
        """
        Hash de los tipos

        >>> t1 = Type({"+":2}, {"<":2})
        >>> t2 = Type({"-":2,"+":2}, {"<":2})
        >>> hash(t1)==hash(t2)
        False
        >>> hash(t1)==hash(t2.subtype(["+"],["<"]))
        True
        """
        return hash(frozenset(chain(self.operations.items(),
                                    self.relations.items())))

    def copy(self):
        """
        Devuelve una copia del tipo
        """
        return Type(self.operations.copy(), self.relations.copy())

    def subtype(self, operations, relations):
        """
        Devuelve un tipo dado por la restriccion a las opereraciones
        y relaciones dadas
        """
        return Type({op: self.operations[op] for op in operations},
                    {rel: self.relations[rel] for rel in relations})

    def is_subtype_of(self, supertype):
        """
        Devuelve si el tipo es un subtipo del supertipo
        """
        result = all(op in supertype.operations and self.operations[
                     op] == supertype.operations[op] for op in self.operations)
        result = result and all(rel in supertype
                                .relations and self.relations[rel] == supertype
                                .relations[rel] for rel in self.relations)
        return result


class AlgebraicType(Type):
    """
    Maneja tipos algebráicos de primer orden, sin nombres de relaciones
    """

    def __init__(self, operations):
        super().__init__(operations, {})

    def __repr__(self):
        result = "AlgebraicType({"
        result += ", ".join([("'%s': %s" % x)
                             for x in sorted(self.operations.items())])
        result += "})"
        return result


if __name__ == "__main__":
    import doctest
    doctest.testmod()
