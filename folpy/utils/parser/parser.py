# -*- coding: utf-8 -*-
# !/usr/bin/env python

import sys
import gzip

from ...semantics import Model, Algebra
from ...semantics.modelfunctions import Relation, Operation
from ...syntax import Type, AlgebraicType
from ...syntax.formulas import Formula
from ...syntax.terms import Variable, Term
from . import preprocessing


class ParserError(Exception):
    """
    Sintax error while parsing
    """

    def __init__(self, line, message):
        super(ParserError, self).__init__(("Line %s: " % line) + message)


def c_input(line):
    """
    Clean input
    """
    line = line.decode("ascii")
    if "#" in line:
        line = line[:line.find("#")]
    return line.strip()


def parse_universe(line):
    # el universo puede estar hecho de strings, de tuplas,etc
    return [eval(i) for i in line.split()]


def barajador(t, d1, d2):
    result = list(d1)
    for i, k in enumerate(d2):
        for j in (j for j, x in enumerate(d1) if x == k):
            result[j] = t[i]
    return tuple(result)


def parse_defformula(line, universe, relations, operations):
    # R(x,y) m(x,y) == j(x,y)
    # print("%s interpreted as:" % line)
    entorno = dict()
    entorno["model"] = Model(universe, relations, operations)
    entorno.update({r: relations[r].syntax_sym for r in relations})
    entorno.update({f: operations[f].syntax_sym for f in operations})
    sym, line = line.split("(", 1)
    declaracion, formula = line.split(")", 1)
    declaracion = declaracion.split(",")
    if len(declaracion) > len(set(declaracion)):
        raise ValueError("por ahora no se pueden declarar repitiendo variables")
    declaracion = tuple(Variable(v) for v in declaracion)

    vars = {v.sym: v for v in declaracion}
    entorno.update(vars)
    try:
        formula = eval(formula, globals(), entorno)
    except NameError:
        raise ValueError("Missing variables in the declaration of %s" % sym)
    if set(formula.free_vars()) > set(declaracion):
        raise ValueError("Missing variables in the declaration of %s" % sym)
    if isinstance(formula, Formula):
        entorno["formula"] = formula
        entorno["arity"] = len(vars)

        valores = eval("formula.extension(model,arity)", globals(), entorno)
        valores = {barajador(t,
                             declaracion,
                             formula.implied_declaration()) for t in valores}
        result = Relation(sym, len(declaracion))
        result.r = valores
        # print(valores)
        return result
    elif isinstance(formula, Term):
        raise NotImplementedError("Functions declared by\
             formula not implemented")


def parse_defrel(line):
    sym, ntuples, arity = line.split()
    ntuples, arity = int(ntuples), int(arity)
    return Relation(sym, arity), ntuples


def parse_defop(line):
    sym, arity = line.split()
    arity = int(arity)
    return Operation(sym, arity)


def parse_tuple(line):
    return tuple(map(eval, line.split()))


def random_delete_tuples(number):
    def f(rel):
        for i in range(number):
            rel.r.pop()
        return rel

    return f


def parser(path=None, preprocess=True, verbose=True):
    """
    New parser
    """
    if path:
        try:
            f = gzip.open(path, "rb")
            f.readline()
            f.seek(0)
        except FileNotFoundError:
            raise ParserError(-1, "File missing")
    else:
        f = sys.stdin
    relations = {}
    operations = {}
    current_rel = None
    current_op = None
    rel_missing_tuples = 0
    op_missing_tuples = 0
    universe = None
    decorators = []
    for linenumber, line in enumerate(f):
        assert (current_op is None or current_rel is None)
        try:
            line = c_input(line)
            if line:
                if universe is None:
                    # tiene que ser el universo!
                    universe = parse_universe(line)
                elif current_rel is None and current_op is None:
                    if "@" in line:
                        decorators.append(eval(line[1:]))
                    elif "(" in line:
                        # empieza una relacion u operacion definida por formula
                        relop = parse_defformula(line,
                                                 universe,
                                                 relations,
                                                 operations)
                        if type(relop) == Relation:
                            for d in reversed(decorators):
                                relop = d(relop)
                            decorators = []
                            relations[relop.sym] = relop

                            # TODO APLICACION DE DECORADORES
                        else:
                            operations[relop.sym] = relop
                            # TODO APLICACION DE DECORADORES
                    elif line.count(" ") == 1:
                        # empieza una operacion
                        current_op = parse_defop(line)
                        op_missing_tuples = len(universe) ** current_op.arity
                        if verbose:
                            print("universe %s" % universe)
                            print("%s tuples: %s" %
                                  (current_op.sym, op_missing_tuples))
                    elif line.count(" ") == 2:
                        # empieza una relacion
                        current_rel, rel_missing_tuples = parse_defrel(line)
                        if verbose:
                            try:
                                print("%s density: %f" % (
                                    current_rel.sym,
                                    float(rel_missing_tuples) /
                                    (len(universe) ** current_rel.arity)))
                            except ValueError:
                                print("WARNING: no pudo calcular la densidad")
                else:
                    if current_rel is not None:
                        # continua una relacion
                        try:
                            if rel_missing_tuples:
                                current_rel.add(parse_tuple(line))
                                rel_missing_tuples -= 1
                            if not rel_missing_tuples:
                                relations[current_rel.sym] = current_rel
                                current_rel = None
                                # TODO APLICACION DE DECORADORES
                        except ValueError:
                            print(line)
                            raise
                    elif current_op is not None:
                        # continua una operacion
                        if op_missing_tuples:
                            current_op.add(parse_tuple(line))
                            op_missing_tuples -= 1
                        if not op_missing_tuples:
                            operations[current_op.sym] = current_op
                            current_op = None
                            # TODO APLICACION DE DECORADORES
        except Exception as e:
            raise e
            raise ParserError(linenumber, e.args[0])
            # TODO el manejo de errores no deberia imprimir excepciones por
            # pantalla
    if universe is None:
        raise ParserError(linenumber, "Universe not defined")
    if current_rel is not None and not rel_missing_tuples:
        raise ParserError(
            linenumber, "Missing tuples for relation %s" % current_rel.sym)
    if current_op is not None:
        raise ParserError(
            linenumber, "Missing tuples for operation %s" % current_op.sym)

    if preprocess:
        prep_relations = set()
        for sym in relations:
            if sym.startswith("T"):
                rel = relations[sym]
                union_pre = preprocessing.preprocesamiento2(rel)
                prep_relations = prep_relations.union(union_pre)
        relations = {sym: relations[sym]
                     for sym in relations if not sym.startswith("T")}
        if verbose:
            print("Target thinning turned T into %s Ts" % len(prep_relations))
        for r in prep_relations:
            relations[r.sym] = r

    operations_names = {key: value.arity() for key, value in operations}
    if relations == {}:
        algebra_type = AlgebraicType(operations_names)
        return Algebra(algebra_type, universe, operations)
    else:
        relations_names = {key: value.arity() for key, value in relations}
        model_type = Type(operations_names, relations_names)
        return Model(model_type, universe, relations, operations)


if __name__ == "__main__":
    MODEL = parser()
    print(MODEL)
