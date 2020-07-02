#!/usr/bin/env python
# -*- coding: utf8 -*-


class Theory():

    def __init__(self, name, axioms, results=[], options=[]):
        """
        Define a first-order class of models by a list of first-order axioms

        INPUT:
            name    -- a string giving the name of the class
            axioms  -- list of strings in the given syntax
            results -- list of strings in the given syntax
            options -- list of strings defining the syntax
        """
        self.name = name
        self.axioms = axioms
        self.results = results
        self.options = options

    def __repr__(self):
        """
        Display a first-order class in a way that can be parsed by Python
        """
        st = ('Theory(\"'
              + self.name
              + '\"'
              + ', axioms=[\n\"'
              + '\",\n\"'.join(self.axioms)
              + '\"]')
        if self.options != []:
            st += ',\noptions=[\n\"' + '\",\n\"'.join(self.options) + '\"]'
        if self.results != []:
            st += ',\nresults=[\n\"' + '\",\n\"'.join(self.results) + '\"]'
        return st + ')'

    def subclass(self, name, arg, results=[], options=[]):
        """
        Add a list of axioms or another FO class to the current one.

        INPUT:
            name -- a string naming the new FO subclass
            arg -- a list of axioms or an existing Theory
        """
        if type(arg) != list:
            arg = arg.axioms  # assume its another Theory
        newaxioms = self.axioms + [a for a in arg if a not in self.axioms]
        return Theory(name, newaxioms, results, self.options + options)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
