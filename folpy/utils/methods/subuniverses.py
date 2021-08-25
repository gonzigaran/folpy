from itertools import product

from .. import powerset


def subuniverse(model, subset, subtype=None):
    """
    Devuelve el subuniverso generado por subset para el subtype
    y devuelve una lista con otros conjuntos que tambien hubieran
    generado el mismo subuniverso

    >>> from folpy.examples.lattices import *
    >>> subuniverse(rhombus, [1],rhombus.type)
    ([1], [[1]])
    >>> len(subuniverse(rhombus, [1,2],rhombus.type)[0])
    4
    >>> subuniverse(rhombus, [1,2],rhombus.type.subtype(["v"],[]))[0]
    [1, 2, 3]
    """
    if not subtype:
        subtype = model.type
    result = subset
    result.sort()
    partials = [list(subset)]
    increasing = True
    result_old = []
    result_new = []
    while increasing:
        increasing = False
        for op in subtype.operations:
            for x in product(result, repeat=model.operations[op].arity()):
                if all(i in result_old for i in x):
                    continue
                elem = model.operations[op](*x)
                if (elem not in result and
                        elem in model.universe and
                        elem not in result_new):
                    result_new.append(elem)
                    result_new.sort()
                    partials.append(list(result + result_new))
                    increasing = True
        result_old = result.copy()
        result = result + result_new
        result_new = []
    result.sort()
    return (result, partials)


def subuniverses(model, subtype=None, proper=True):
    """
    NO DEVUELVE EL SUBUNIVERSO VACIO
    Generador que va devolviendo los subuniversos.
    Intencionalmente no filtra por isomorfismos.

    >>> from folpy.examples.lattices import *
    >>> len(list(subuniverses(rhombus, rhombus.type)))
    12
    """
    if not subtype:
        subtype = model.type
    result = []
    subsets = powerset(model.universe)
    checked = [[]]
    if proper:
        checked.append(model.universe)
    for subset in subsets:
        if subset in checked:
            continue
        subuniv, partials = subuniverse(model, subset, subtype)
        for partial in partials:
            if partial not in checked:
                checked.append(partial)
        if subuniv not in result:
            result.append(subuniv)
            yield subuniv


def is_subuniverse(model, subset, subtype=None):
    """
    Dado un conjunto, decide si es subuniverso o no
    """
    return len(subset) == len(subuniverse(model, subset, subtype=subtype))
