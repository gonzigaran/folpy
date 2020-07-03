#!/usr/bin/env python
# -*- coding: utf8 -*-

class Term(object):
    """
    Clase general de los terminos de primer orden
    """
    def __init__(self):
        pass

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def free_vars(self):
        raise NotImplementedError

    def evaluate(self, model, vector):
        """
        Evalua el termino en el modelo para el vector de valores
        """
        raise NotImplementedError


class Variable(Term):
    """
    Variable de primer orden
    """
    def __init__(self, sym):
        if isinstance(sym, int):
            self.sym = "x" + str(sym)
        else:
            self.sym = sym

    def __repr__(self):
        return self.sym

    def free_vars(self):
        return {self}

    def evaluate(self, model, vector):
        try:
            return vector[self]
        except KeyError:
            raise ValueError("Free variable %s is not defined" % (self))


class OpSym(object):
    """
    Simbolo de operacion de primer orden
    """
    def __init__(self, op, arity):
        self.op = op
        self.arity = arity

    def __call__(self, *args):
        if (len(args) != self.arity
                or any((not isinstance(a, Term)) for a in args)):
            raise ValueError("Arity not correct or any isn't a term")
        return OpTerm(self, args)

    def __repr__(self):
        return self.op


class OpTerm(Term):
    """
    Termino de primer orden de la aplicacion de una funcion
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

    def evaluate(self, model, vector):
        args = [t.evaluate(model, vector) for t in self.args]
        return model.operations[self.sym.op](*args)


def fo_type_to_opsym(fo_type):
    """
    Devuelve una lista de OpSym para un tipo
    """
    result = []
    for f in fo_type.operations:
        result.append(OpSym(f, fo_type.operations[f]))
    return result


def variables(*lvars):
    """
    Declara variables de primer orden
    """
    return tuple(Variable(x) for x in lvars)
