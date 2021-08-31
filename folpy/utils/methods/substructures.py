from itertools import combinations

from .subuniverses import subuniverses, is_subuniverse


def substructures(
        model,
        supermodel=None,
        filter_isos=False,
        filter_subdirect=False,
        subtype=None,
        proper=True,
        without=[]):
    """
    Generador que va devolviendo las subestructuras.
    Intencionalmente no filtra por isomorfismos.
    Devuelve una subestructura y un embedding.
    No devuelve las subestructuras cuyos universos estan en without.

    >>> from folpy.examples.lattices import *
    >>> one_op_subtype = rhombus.type.subtype(["^"],[])
    >>> empty_subtype = rhombus.type.subtype([],[])
    >>> len(list(substructures(rhombus, rhombus.type)))
    11
    >>> len(list(substructures(gen_chain(4), rhombus.type)))
    14
    >>> len(list(substructures(rhombus, subtype=one_op_subtype)))
    12
    >>> len(list(substructures(rhombus, subtype=empty_subtype)))
    14
    >>> len(list(substructures(rhombus, subtype=empty_subtype, proper=False)))
    15
    """
    if not subtype:
        subtype = model.type
    without = list(map(set, without))
    for sub in subuniverses(model, subtype=subtype, proper=proper):
        if set(sub) not in without:
            yield model.substructure(sub, subtype=subtype)


def substructures_by_maximals(
        model,
        supermodel=None,
        filter_isos=True,
        filter_subdirect=False,
        subtype=None,
        proper=True,
        without=[]):
    """
    Generador de subestructuras que filtra por isomorfismos y tiene opcion
    para quedarse solo con los subdirectos (para esto el modelo tiene que ser
    un producto)

    TODO implementar lo de filter_subdirect
    TODO implementar lo de subtype
    TODO implementar lo de without
    """
    if not supermodel:
        supermodel = model
    if filter_subdirect:
        assert len(model.factors) > 1
    if not subtype:
        subtype = model.type
    universe = model.universe.copy()
    result = []
    result_compl = []
    for i in range(1, len(model)):
        has_subs_of_this_len = False
        for subset in combinations(universe, i):
            subset = set(subset)
            if any(x.issubset(subset) for x in result_compl):
                continue
            has_subs_of_this_len = True
            possible_subuniverse = [x for x in universe if x not in subset]
            if is_subuniverse(model, possible_subuniverse):
                substructure = supermodel.restrict(possible_subuniverse)
                result_compl.append(subset)
                if filter_isos and any(substructure.is_isomorphic(x)
                                       for x in result):
                    continue
                result.append(substructure)
                yield substructure
                for sub in substructures_by_maximals(
                                substructure,
                                supermodel=supermodel,
                                filter_isos=filter_isos,
                                filter_subdirect=filter_subdirect,
                                subtype=subtype,
                                proper=proper):
                    if filter_isos and any(sub.is_isomorphic(x)
                                           for x in result):
                        continue
                    if sub not in result:
                        result.append(sub)
                        yield sub
        if not has_subs_of_this_len:
            break
    if not proper:
        not_proper_sub = supermodel.restrict(supermodel.universe)
        if not_proper_sub not in result:
            result.append(not_proper_sub)
            yield not_proper_sub
    return result
