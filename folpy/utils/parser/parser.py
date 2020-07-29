# -*- coding: utf-8 -*-
# !/usr/bin/env python

import sys

from ...semantics import Model, Algebra, Lattice
from ...semantics.modelfunctions import Relation, Operation
from ...syntax import Type, AlgebraicType


STATES = ['UNIVERSE', 'RELATION', 'OPERATION', 'NAME']


class ParserError(Exception):
    """
    Sintax error while parsing
    """

    def __init__(self, line, message):
        super(ParserError, self).__init__(("Line %s: " % line) + message)


class Parser(object):
    """
    Parse a model

    TODO verbose
    TODO preprocess
    TODO name

    >>> from folpy.semantics import Algebra, Model
    >>> p = Parser("folpy/utils/parser/example.model")
    >>> type(p.parse()) == Model
    True
    """

    def __init__(self, path=None, preprocess=True, verbose=True):
        if path:
            try:
                f = open(path, "rb")
            except FileNotFoundError:
                raise ParserError(-1, "File missing")
        else:
            f = sys.stdin
        self.file = f
        self.preprocess = preprocess
        self.verbose = verbose
        self.name_type = ({}, {})
        self.relations = {}
        self.operations = {}
        self.current_state = 'UNIVERSE'
        self.current_sym = None
        self.current_len = 0
        self.universe = None
        self.current_line = 0
        self.name = None

    def parse(self):
        for linenumber, line in enumerate(self.file):
            assert self.current_line == linenumber
            line = line.decode("ascii").strip()
            if ("#" not in line) and (line != ""):
                self.parse_line(line)
            self.current_line += 1
        return self.return_model()

    def parse_line(self, line):
        if self.current_state is None:
            if self.current_len != 0:
                raise ParserError(self.current_line,
                                  "Bad definition of operation or relation")
            self.current_state = self.get_state(line)
        if self.current_state == 'UNIVERSE':
            self.parse_universe(line)
        elif self.current_state == 'RELATION':
            self.parse_relation(line)
        elif self.current_state == 'OPERATION':
            self.parse_operation(line)
        elif self.current_state == 'NAME':
            self.parse_name(line)
        else:
            raise ParserError(self.current_line,
                              "State error, %s" % self.current_state)

    def get_state(self, line):
        assert self.current_state is None
        line_list = line.split()
        if (not line_list[0].isdigit()) and len(line_list) == 3:
            return 'RELATION'
        elif (not line_list[0].isdigit()) and len(line_list) == 2:
            return 'OPERATION'
        else:
            return None

    def parse_universe(self, line):
        assert self.universe is None
        self.universe = [eval(i) for i in line.split()]
        self.current_state = None

    def parse_relation(self, line):
        line_list = line.split()
        if line_list[0].isdigit():
            if not all(value.isdigit() for value in line_list):
                raise ParserError(self.current_line,
                                  "Bad definition of relation tuple")
            self.parse_relation_tuple(line_list)
        else:
            assert len(line_list) == 3
            self.parse_relation_name(line_list)

    def parse_relation_name(self, line_list):
        rel_name = line_list[0]
        rel_len = int(line_list[1])
        rel_arity = int(line_list[2])
        if rel_name in self.name_type[1].keys():
            raise ParserError(self.current_line,
                              "Relation name %s repeted" % rel_name)
        self.name_type[1][rel_name] = rel_arity
        self.relations[rel_name] = []
        self.current_sym = rel_name
        self.current_len = rel_len

    def parse_relation_tuple(self, line_list):
        rel_name = self.current_sym
        rel_len = self.current_len
        rel_arity = self.name_type[1][rel_name]
        if len(line_list) != rel_arity:
            raise ParserError(self.current_line,
                              "Relation %s arity doesn't match" % rel_name)
        tuple_value = tuple([int(val) for val in line_list])
        self.relations[rel_name].append(tuple_value)
        self.current_len = rel_len - 1
        if self.current_len == 0:
            self.current_state = None
            self.current_sym = None

    def parse_operation(self, line):
        line_list = line.split()
        if line_list[0].isdigit():
            if not all(value.isdigit() for value in line_list):
                raise ParserError(self.current_line,
                                  "Bad definition of operation tuple")
            self.parse_operation_tuple(line_list)
        else:
            assert len(line_list) == 2
            self.parse_operation_name(line_list)

    def parse_operation_name(self, line_list):
        op_name = line_list[0]
        op_arity = int(line_list[1])
        if op_name in self.name_type[0].keys():
            raise ParserError(self.current_line,
                              "Operation name %s repeted" % op_name)
        self.name_type[0][op_name] = op_arity
        self.operations[op_name] = {}
        self.current_sym = op_name
        self.current_len = len(self.universe) ** op_arity

    def parse_operation_tuple(self, line_list):
        op_name = self.current_sym
        op_len = self.current_len
        op_arity = self.name_type[0][op_name]
        if len(line_list) != op_arity + 1:
            raise ParserError(self.current_line,
                              "Operation %s arity doesn't match" % op_name)
        line_list = [int(val) for val in line_list]
        tuple_value = tuple(line_list[:op_arity])
        image = line_list[op_arity]
        self.operations[op_name][tuple_value] = image
        self.current_len = op_len - 1
        if self.current_len == 0:
            self.current_state = None
            self.current_sym = None

    def parse_name(self, line):
        raise NotImplementedError("Name to model not implemented")

    def return_model(self):
        self.operations = {k: Operation(
            self.operations[k],
            self.universe
            ) for k in self.operations.keys()}
        if self.relations == {}:
            algebra_type = AlgebraicType(self.name_type[0])
            op_names = self.operations.keys()
            if (len(op_names) == 2) and ('^' in op_names) and ('v' in op_names):
                return Lattice(self.universe,
                               self.operations['v'],
                               self.operations['^'])
            else:
                return Algebra(algebra_type,
                               self.universe,
                               self.operations)
        else:
            self.relations = {k: Relation(
                self.relations[k],
                self.universe
                ) for k in self.relations.keys()}
            model_type = Type(self.name_type[0], self.name_type[1])
            return Model(model_type,
                         self.universe,
                         self.operations,
                         self.relations)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
