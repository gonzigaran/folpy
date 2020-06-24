#!/usr/bin/env python
# -*- coding: utf8 -*-

from itertools import chain, combinations


def indent(text):
    r"""
    Indenta un parrafo

    >>> print(indent("hola\n  hola\nhola"))
      hola
        hola
      hola
    <BLANKLINE>
    >>> print(indent(indent("hola\n  hola\nhola")))
        hola
          hola
        hola
    <BLANKLINE>
    """
    text = "  " + text.strip("\n")
    return text.replace('\n', '\n  ') + "\n"


def comment(text):
    r"""
    comenta un parrafo

    >>> print(comment("hola\n  hola\nhola"))
    # hola
    #   hola
    # hola
    <BLANKLINE>
    """
    text = "# " + text.strip("\n")
    return text.replace('\n', '\n# ') + "\n"


def powerset(iterable):
    """
    Devuelve un generador que itera sobre partes del iterable,
    va de mayor a menor.

    >>> list(powerset([1,2,3]))
    [[1, 2, 3], [1, 2], [1, 3], [2, 3], [1], [2], [3], []]
    """
    s = list(iterable)
    return map(list, chain.from_iterable(combinations(s, r) for r in
                                         range(len(s) + 1, -1, -1)))


def compose(f, g):
    """
    Compone funciones de Python

    >>> compose(lambda x: x+1, lambda x,y: x+y)(5,6)
    12
    """
    def composition(*args):
        return f(g(*args))
    return composition


if __name__ == "__main__":
    import doctest
    doctest.testmod()
