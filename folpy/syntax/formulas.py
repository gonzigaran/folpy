#!/usr/bin/env python
# -*- coding: utf8 -*-

from itertools import product, combinations

from .terms import Term


class Formula(object):
    """
    Clase general de las formulas de primer orden

    declaracion de variables de primer orden
    >>> from .terms import variables, OpSym
    >>> x,y,z = variables("x","y","z")

    >>> R = RelSym("R",2) # declaro una relacion R de aridad 2

    >>> f = OpSym("f",3) # declaro una operacion f de aridad 3

    >>> R(x,y) | R(y,x) & R(y,z)
    (R(x, y) ∨ (R(y, x) ∧ R(y, z)))

    >>> -R(f(x,y,z),y) | R(y,x) & R(y,z)
    (¬ R(f(x, y, z), y) ∨ (R(y, x) ∧ R(y, z)))

    >>> a = forall(x, -R(f(x,y,z),y))
    >>> a
    ∀ x ¬ R(f(x, y, z), y)
    >>> a.free_vars() == {y,z}
    True

    >>> a = R(x,x) & a
    >>> a
    (R(x, x) ∧ ∀ x ¬ R(f(x, y, z), y))
    >>> a.free_vars() == {x, y, z}
    True

    >>> exists(x, R(f(x,y,z),y))
    ∃ x R(f(x, y, z), y)

    >>> (-(true() & true() & false())) | false()
    ⊤

    """
    def __init__(self):
        pass

    def __and__(self, other):
        if isinstance(self, TrueFormula):
            return other
        elif isinstance(other, TrueFormula):
            return self

        return AndFormula([self, other])

    def __or__(self, other):
        if isinstance(self, FalseFormula):
            return other
        elif isinstance(other, FalseFormula):
            return self

        return OrFormula([self, other])

    def __neg__(self):
        if isinstance(self, TrueFormula):
            return false()
        elif isinstance(self, FalseFormula):
            return true()

        return NegFormula(self)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(repr(self))

    def free_vars(self):
        raise NotImplementedError

    def satisfy(self, model, vector):
        raise NotImplementedError


class NegFormula(Formula):
    """
    Negacion de una formula
    """
    def __init__(self, f):
        self.f = f

    def __repr__(self):
        return "¬ %s" % self.f

    def free_vars(self):
        return self.f.free_vars()

    def satisfy(self, model, vector):
        return not self.f.satisfy(model, vector)


class BinaryOpFormula(Formula):
    """
    Clase general de las formulas tipo f1 η ... η fn
    """
    def __init__(self, subformulas):
        self.subformulas = subformulas

    def free_vars(self):
        result = set()
        for f in self.subformulas:
            result = result.union(f.free_vars())
        return result


class OrFormula(BinaryOpFormula):
    """
    Disjuncion entre formulas
    """
    def __repr__(self):
        result = " ∨ ".join(str(f) for f in self.subformulas)
        result = "(" + result + ")"
        return result

    def __or__(self, other):
        if isinstance(self, FalseFormula):
            return other
        elif isinstance(other, FalseFormula):
            return self

        return OrFormula(self.subformulas + [other])

    def satisfy(self, model, vector):
        # el or y el and de python son lazy
        return any(f.satisfy(model, vector) for f in self.subformulas)


class AndFormula(BinaryOpFormula):
    """
    Conjuncion entre formulas
    """
    def __repr__(self):
        result = " ∧ ".join(str(f) for f in self.subformulas)
        result = "(" + result + ")"
        return result

    def __and__(self, other):
        if isinstance(self, TrueFormula):
            return other
        elif isinstance(other, TrueFormula):
            return self

        return AndFormula(self.subformulas + [other])

    def satisfy(self, model, vector):
        # el or y el and de python son lazy
        return all(f.satisfy(model, vector) for f in self.subformulas)


class RelSym(object):
    """
    Simbolo de relacion de primer orden
    """
    def __init__(self, rel, arity):
        self.rel = rel
        self.arity = arity

    def __call__(self, *args):
        if (len(args) != self.arity
                or any((not isinstance(a, Term)) for a in args)):
            raise ValueError("Arity not correct or any isn't a term")
        return RelFormula(self, args)

    def __repr__(self):
        return self.rel


class RelFormula(Formula):
    """
    Formula de primer orden de la aplicacion de una relacion
    """
    def __init__(self, sym, args):
        self.sym = sym
        self.args = args

    def __repr__(self):
        result = repr(self.sym)
        result += "("
        result += ", ".join(map(repr, self.args))
        result += ")"
        return result

    def free_vars(self):
        return set.union(*[f.free_vars() for f in self.args])

    def satisfy(self, model, vector):
        args = [t.evaluate(model, vector) for t in self.args]
        return model.relations[self.sym.rel](*args)


class EqFormula(Formula):
    """
    Formula de primer orden que es una igualdad entre terminos
    """
    def __init__(self, t1, t2):
        if not (isinstance(t1, Term) and isinstance(t2, Term)):
            raise ValueError("Must be terms")
        self.t1 = t1
        self.t2 = t2

    def __repr__(self):
        return "%s == %s" % (self.t1, self.t2)

    def free_vars(self):
        return set.union(self.t1.free_vars(), self.t2.free_vars())

    def satisfy(self, model, vector):
        return self.t1.evaluate(model, vector) ==\
                 self.t2.evaluate(model, vector)


class QuantifierFormula(Formula):
    """
    Clase general de una formula con cuantificador
    """
    def __init__(self, var, f):
        self.var = var
        self.f = f

    def free_vars(self):
        return self.f.free_vars() - {self.var}


class ForAllFormula(QuantifierFormula):
    """
    Formula Universal
    """
    def __repr__(self):
        return "∀ %s %s" % (self.var, self.f)

    def satisfy(self, model, vector):
        for i in model.universe:
            vector[self.var] = i
            if not self.f.satisfy(model, vector):
                return False
        return True


class ExistsFormula(QuantifierFormula):
    """
    Formula Existencial
    """
    def __repr__(self):
        return "∃ %s %s" % (self.var, self.f)

    def satisfy(self, model, vector):
        vector = vector.copy()
        for i in model.universe:
            vector[self.var] = i
            if self.f.satisfy(model, vector):
                return True
        return False


class TrueFormula(Formula):
    """
    Formula de primer orden constantemente verdadera
    """

    def __repr__(self):
        return "⊤"

    def free_vars(self):
        return set()

    def satisfy(self, model, vector):
        return True


class FalseFormula(Formula):
    """
    Formula de primer orden constantemente falsa
    """

    def __repr__(self):
        return "⊥"

    def free_vars(self):
        return set()

    def satisfy(self, model, vector):
        return False


def forall(var, formula):
    """
    Devuelve la formula universal
    """
    return ForAllFormula(var, formula)


def eq(t1, t2):
    if t1 == t2:
        return true()
    return EqFormula(t1, t2)


def exists(var, formula):
    """
    Devuelve la formula existencial
    """
    return ExistsFormula(var, formula)


def true():
    """
    Devuelve la formula True
    """
    return TrueFormula()


def false():
    """
    Devuelve la formula False
    """
    return FalseFormula()


def grafico(term, vs, model):
    result = {}
    for tupla in product(model.universe, repeat=len(vs)):
        result[tupla] = term.evaluate(model, {v: a for v, a in zip(vs, tupla)})
    return tuple(sorted(result.items()))


def generate_terms(funtions, vs, model):
    """
    Devuelve todos los terminos (en realidad solo para infimo y supremo)
    usando las funciones y las variables con un anidaminento de rec
    """
    result = []
    graficos = set()

    for v in vs:
        g = grafico(v, vs, model)
        if g not in graficos:
            result.append(v)
            graficos.add(g)
    nuevos = [1]
    while nuevos:
        nuevos = []
        for f in funtions:
            for ts in product(result, repeat=f.arity):
                g = grafico(f(*ts), vs, model)
                if g not in graficos:
                    nuevos.append(f(*ts))
                    graficos.add(g)
            result += nuevos
    return result


def atomics(relations, terms, equality=True):
    """
    Genera todas las formulas atomicas con relations
    de arity variables libres

    >>> from .terms import variables
    >>> R = RelSym("R",2)
    >>> vs = variables(*range(2))
    >>> list(atomics([R],vs))
    [R(x0, x0), R(x0, x1), R(x1, x0), R(x1, x1), x0 == x1]
    >>> list(atomics([R],vs,equality=False))
    [R(x0, x0), R(x0, x1), R(x1, x0), R(x1, x1)]
    """
    terms
    for r in relations:
        for t in product(terms, repeat=r.arity):
            yield r(*t)

    if equality:
        for t in combinations(terms, 2):
            yield eq(*t)


def fo_type_to_relsym(fo_type):
    """
    Devuelve una lista de RelSym para un tipo
    """
    result = []
    for r in fo_type.relations:
        result.append(RelSym(r, fo_type.relations[r]))
    return result
