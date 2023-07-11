from itertools import combinations

from .subuniverses import subuniverses, is_subuniverse, is_subdirect_subuniverse


def substructures_downup(
        model,
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
    >>> empty = rhombus.type.subtype([],[])
    >>> len(list(substructures_downup(rhombus, rhombus.type)))
    11
    >>> len(list(substructures_downup(rhombus, rhombus.type, proper=False)))
    12
    >>> len(list(substructures_downup(gen_chain(4), rhombus.type)))
    14
    >>> len(list(substructures_downup(gen_chain(4), rhombus.type, proper=False)))
    15
    >>> len(list(substructures_downup(rhombus, subtype=one_op_subtype)))
    12
    >>> len(list(substructures_downup(rhombus, subtype=empty)))
    14
    >>> len(list(substructures_downup(rhombus, subtype=empty, proper=False)))
    15
    """
    if not subtype:
        subtype = model.type
    without = list(map(set, without))
    for sub in subuniverses(model, subtype=subtype, proper=proper):
        if filter_subdirect:
            if not is_subdirect_subuniverse(sub, model.universe):
                continue
        if set(sub) not in without:
            yield model.substructure(sub, subtype=subtype)


def substructures_updown(
        model,
        filter_isos=False,
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
    if filter_subdirect:
        assert len(model.factors) > 1
    if not subtype:
        subtype = model.type
    universe = model.universe.copy()
    result = []
    # conviene guardar hashes de estructuras
    result_compl = []
    for i in range(1, len(model)):
        for subset in combinations(universe, i):
            subset = set(subset)
            possible_subuniverse = [x for x in universe if x not in subset]
            if filter_subdirect:
                if not is_subdirect_subuniverse(
                                possible_subuniverse, model.universe):
                    continue
            if is_subuniverse(model, possible_subuniverse):
                substructure = model.restrict(possible_subuniverse)
                result_compl.append(subset)
                if filter_isos and any(substructure.is_isomorphic(x)
                                       for x in result):
                    continue
                result.append(substructure)
                yield substructure
    if not proper:
        not_proper_sub = model.restrict(model.universe)
        if not_proper_sub not in result:
            result.append(not_proper_sub)
            yield not_proper_sub
    return result


def substructures_by_maximals(
        model,
        filter_isos=False,
        filter_subdirect=False,
        subtype=None,
        proper=True,
        without=[]):
    """
    Generador de subestructuras a partir de iteración de maximales.

    TODO implementar proper
    TODO implementar subtype
    TODO implementar without
    
    >>> from folpy.examples.lattices import *
    >>> one_op_subtype = rhombus.type.subtype(["^"],[])
    >>> empty = rhombus.type.subtype([],[])
    >>> len(list(substructures_by_maximals(rhombus, subtype=rhombus.type)))
    11
    >>> len(list(substructures_by_maximals(gen_chain(4), subtype=rhombus.type)))
    14
    """
    if filter_subdirect:
        assert len(model.factors) > 1
    if not subtype:
        subtype = model.type

    global complements_subsets
    global known_substructures

    def maximal_substructures(model, supermodel):
        if not supermodel:
            supermodel = model
        diff_universe = set(supermodel.universe)-set(model.universe)
        global complements_subsets
        global known_substructures

        for i in range(1, len(model)):
            has_subs_of_this_len = False
            for subset in combinations(model.universe, i):
                subset = set(subset)
                supersubset = subset.union(diff_universe)
                if supersubset in complements_subsets:
                    continue
                if any(x.issubset(subset) for x in complements_subsets):
                    continue
                possible_subuniverse = [x for x in model.universe
                                        if x not in subset]
                if filter_subdirect:
                    if not is_subdirect_subuniverse(
                                    possible_subuniverse, supermodel.universe):
                        continue
                has_subs_of_this_len = True
                if is_subuniverse(model, possible_subuniverse):
                    new_substructure = supermodel.restrict(possible_subuniverse)
                    complements_subsets.append(supersubset)
                    if filter_isos and any(new_substructure.is_isomorphic(x)
                                           for x in known_substructures):
                        continue
                    known_substructures.append(new_substructure)
                    yield new_substructure
            if not has_subs_of_this_len:
                break

    known_substructures = []
    complements_subsets = []
    old_substructure_list = maximal_substructures(model, model)
    new_substructure_list = []

    while old_substructure_list:
        for sub in old_substructure_list:
            known_substructures.append(sub)
            yield sub
            for maximal in maximal_substructures(sub, model):
                new_substructure_list.append(maximal)
        old_substructure_list = new_substructure_list.copy()
        new_substructure_list = []

    return True
