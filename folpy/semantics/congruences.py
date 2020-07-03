#!/usr/bin/env python
# -*- coding: utf8 -*-

from collections import defaultdict


class _CardinalBlock(object):
    def __init__(self, value):
        self.value = value


class Partition(object):
    def __init__(self, iter_of_iter=()):
        self.v = dict()
        self.from_table(iter_of_iter)

    def __call__(self, a, b):
        return self.root(a) == self.root(b)

    def __eq__(self, other):
        return self.table() == other.table()

    def __lt__(self, other):
        return self.table() < other.table()

    def __le__(self, other):
        return self == other or self < other

    def __ge__(self, other):
        return other <= self

    def __gt__(self, other):
        return other < self

    def __repr__(self):
        result = repr(self.to_list())[1:-1].replace("[", "|").replace("]", "|")
        return "[" + result + "]"

    def __hash__(self):
        return hash(frozenset(self.v.items()))

    def from_table(self, ls):
        for a, b in ls:
            self.add_element(a)
            self.add_element(b)
            self.join_blocks(a, b)

    def table(self):
        result = set()
        for a in self.v:
            for b in self.v:
                if self(a, b):
                    result.add((a, b))
        return result

    def copy(self):
        result = Partition()
        result.v = self.v.copy()
        return result

    def from_blocks(self, lss):
        """
        Extiende la particion con una lista de listas
        :param list:
        :return:
        """
        for ls in lss:
            for e in ls:
                self.add_element(e)
                self.join_blocks(e, ls[0])

    def add_element(self, e):
        if e not in self.v:
            self.v[e] = _CardinalBlock(-1)

    def root(self, e):
        """
        Representante de la clase de equivalencia de e
        """
        # TODO NO DEBERIA SER RECURSIVO
        # deberia avanzar recordando los que no tienen al root como padre
        #  y acomodar todo al final
        if self.is_root(e):
            return e
        else:
            self.v[e] = self.root(self.v[e])
            return self.v[e]

    def join_blocks(self, i, j):
        ri = self.root(i)
        rj = self.root(j)
        if ri != rj:
            si = self.v[ri].value
            sj = self.v[rj].value
            if si > sj:
                self.v[ri] = rj
                self.v[rj] = _CardinalBlock(si + sj)
            else:
                self.v[rj] = ri
                self.v[ri] = _CardinalBlock(si + sj)

    def to_list(self):
        result = defaultdict(list)
        for e in self.v:
            result[self.root(e)].append(e)
        return list(result.values())

    def meet(self, other):
        """

        :type other: Partition
        """
        result = Partition()
        ht = dict()
        for e in self.v:
            r1 = self.root(e)
            r2 = other.root(e)
            if (r1, r2) in ht:
                r = ht[r1, r2]
                result.v[r] = _CardinalBlock(result.v[r].value + 1)
                result.v[e] = r
            else:
                ht[(r1, r2)] = e
                result.v[e] = _CardinalBlock(-1)
        return result

    def is_root(self, e):
        return isinstance(self.v[e], _CardinalBlock)

    def join(self, other):
        """
        The join(U, V)
            for each i which is not a root of U
                join-blocks(i, U[i], V)
        :type other: Partition
        """
        result = other.copy()
        for e in self.v:
            if not self.is_root(e):  # not a root
                result.join_blocks(e, self.root(e))
        return result

    def iter_tuples(self):
        for a in self.v:
            for b in self.v:
                if self(a, b):
                    yield (a, b)

    def block(self, e):
        result = set()
        r = self.root(e)
        for i in self.v:
            if self.root(i) == r:
                result.add(i)
        return frozenset(result)

    def iter_blocks(self):
        for e in self.v:
            if self.is_root(e):
                yield self.block(e)

    def roots(self):
        for e in self.v:
            if self.is_root(e):
                yield e

    def to_congruence(self, algebra):
        return Congruence(self.table(), algebra)


class Congruence(Partition):
    """
    Congruencia

    >>> from folpy.examples.lattices import rhombus
    >>> rel = Congruence([(1, 1),(2, 2),(3, 3),(0, 0),(1, 3),(3, 1),
    ... (0, 2),(2, 0)], rhombus)
    >>> rel(1, 3)
    True
    >>> rel(0, 3)
    False
    >>> sorted(list(rel.table()))
    [(0, 0), (0, 2), (1, 1), (1, 3), (2, 0), (2, 2), (3, 1), (3, 3)]
    """

    def __init__(self, table, algebra, check_operations=False):
        self.algebra = algebra
        super().__init__(table)
        self_relation = []
        for i in algebra.universe:
            self_relation.append((i, i))
        self.from_table(self_relation)
        if check_operations:
            assert self._are_operations_preserved()

    def __and__(self, other):
        """
        Genera la congruencia a partir de la intersección de 2 congruencias
        """
        assert self.algebra == other.algebra
        return self.meet(other).to_congruence(self.algebra)

    def __or__(self, other):
        """
        Genera la congruencia a partir de la unión de 2 congruencias
        """
        assert self.algebra == other.algebra
        return self.join(other).to_congruence(self.algebra)

    def __eq__(self, other):
        if self.algebra != other.algebra:
            return False
        return super(Congruence, self).__eq__(other)

    def __lt__(self, other):
        if self.algebra != other.algebra:
            return False
        return super(Congruence, self).__lt__(other)

    def __le__(self, other):
        if self.algebra != other.algebra:
            return False
        return super(Congruence, self).__le__(other)

    def __ge__(self, other):
        if self.algebra != other.algebra:
            return False
        return super(Congruence, self).__ge__(other)

    def __gt__(self, other):
        if self.algebra != other.algebra:
            return False
        return super(Congruence, self).__gt__(other)

    def __repr__(self):
        return "Congruence(" + super(Congruence, self).__repr__() + ")"

    def __hash__(self):
        return hash(frozenset(self.v.items()))

    def classes(self):
        return self.iter_blocks()

    def equiv_class(self, x):
        return self.block(x)

    def copy(self):
        return Congruence(self.table(), self.algebra)

    def _is_operation_preserved(self, op):
        if self.algebra.operations[op].arity() == 0:
            pass
        else:
            for t in self.algebra.operations[op].domain():
                for s in self.algebra.operations[op].domain():
                    if self._are_tuples_related(t, s):
                        if not self(self.algebra.operations[op](*t),
                                    self.algebra.operations[op](*s)):
                            return False
        return True

    def _are_operations_preserved(self):
        result = True
        for op in self.algebra.operations:
            result = result and self._is_operation_preserved(op)
        return result

    def _are_tuples_related(self, t, s):
        for i in range(len(t)):
            if not self(t[i], s[i]):
                return False
        return True


class CongruenceSystem(object):
    """
    Sistema de Congruecias
    Dado una lista de congruencias, una lista de elementos y un sigma generador
    del proyecto, genera el Sistema de Congruencias para ese proyectivo

    >>> from folpy.examples.lattices import rhombus
    >>> C1 = Congruence([(1, 1),(2, 2),(3, 3),(0, 0),(1, 3),(3, 1),(0, 2),
    ... (2, 0)], rhombus)
    >>> C2 = Congruence([(1, 1),(2, 2),(3, 3),(0, 0),(2, 3),(3, 2),(0, 1),
    ... (1, 0)], rhombus)
    >>> CS = CongruenceSystem([C1, C2], [2, 1])
    >>> CS.solutions()
    frozenset({0})

    """

    def __init__(self, congruences, elements, sigma=None, check_system=False):
        assert congruences and isinstance(congruences, list)
        assert elements and isinstance(elements, list)
        assert len(elements) == len(elements)
        n = len(elements)
        algebra = congruences[0].algebra
        for tita in congruences:
            assert isinstance(tita, Congruence)
            assert tita.algebra == algebra
        for x in elements:
            assert x in algebra.universe
        self.algebra = algebra
        self.n = n
        self.congruences = congruences
        self.elements = elements
        if check_system:
            if sigma:
                assert self.is_system(lambda x, y: sup_proj(sigma, x, y))
            else:
                assert self.is_system()
        self.sigma = sigma

    def solutions(self):
        sol = self.congruences[0].equiv_class(self.elements[0])
        for i in list(range(self.n)):
            if i != 0:
                sol = sol & self.congruences[i].equiv_class(self.elements[i])
        return sol

    def has_solution(self):
        if len(self.solutions()) == 0:
            return False
        else:
            return True

    def is_system(self, sup=lambda x, y: x | y):
        for i in list(range(self.n)):
            for j in list(range(self.n)):
                if i != j:
                    if ([self.elements[i], self.elements[j]] not in
                            sup(self.congruences[i], self.congruences[j])):
                        return False
        return True


def sup_proj(sigma, x, y):
    """
    Devuelve el supremo entre x e y dentro del reticulado de congruencias
    generado por el conjunto sigma
    """
    assert x.algebra == y.algebra
    all_gt_xy = [c for c in sigma if (x <= c and y <= c)]
    result = x.algebra.maxcon()
    for r in all_gt_xy:
        result = result & r
    return result


if __name__ == "__main__":
    import doctest
    doctest.testmod()
