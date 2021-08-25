from itertools import combinations, product

from .subuniverses import subuniverses


def substructures(model, subtype=None, without=[], proper=True):
    """
    Generador que va devolviendo las subestructuras.
    Intencionalmente no filtra por isomorfismos.
    Devuelve una subestructura y un embedding.
    No devuelve las subestructuras cuyos universos estan en without.

    >>> from folpy.examples.lattices import *
    >>> len(list(substructures(rhombus, rhombus.type)))
    12
    >>> len(list(substructures(rhombus, rhombus.type.subtype(["v"],[]))))
    13
    >>> len(list(substructures(rhombus, rhombus.type.subtype([],[]))))
    14
    >>> len(list(substructures(rhombus, rhombus.type.subtype([],[]),proper=False)))
    15
    """
    if not subtype:
        subtype = model.type
    without = list(map(set, without))
    for sub in subuniverses(model, subtype=subtype, proper=proper):
        if set(sub) not in without:
            yield model.substructure(sub, subtype=subtype)
