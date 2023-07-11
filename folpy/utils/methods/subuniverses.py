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
    11
    """
    if not subtype:
        subtype = model.type
    
    class Node(object):
        """
        Tipo auxiliar para este algoritmo
        """
        def __init__(self, closed, incomparables, generators) -> None:
            self.closed = closed
            self.incomparables = incomparables
            self.generators = generators
        
        def join(self, other):
            subset = set(self.closed).union(set(other.closed))
            closed = subuniverse(model, list(subset), subtype=subtype)[0]
            inc = [i for i in self.incomparables if i in other.incomparables and i not in closed]
            gen = self.generators + other.generators
            return Node(closed, inc, gen)
        
        def copy(self):
            from copy import deepcopy
            return deepcopy(self)

    
    one_gen_subuniverses = {}
    for x in model.universe:
        subuniv = subuniverse(model, [x], subtype=subtype)[0]
        if subuniv not in one_gen_subuniverses.values():
            one_gen_subuniverses[x] = subuniv
            if not (len(subuniv) == len(model.universe) and proper):
                yield subuniv

    generators = list(one_gen_subuniverses.keys())
    one_gen_nodes = {}
    nodes_queue = []

    while generators:
        g = generators.pop(0)
        incomparables = [x for x in generators if not 
                         (x in one_gen_subuniverses[g] or 
                          g in one_gen_subuniverses[x])]
        node = Node(one_gen_subuniverses[g], incomparables, [g])
        one_gen_nodes[g] = node
        nodes_queue.append(node.copy())

    subuniverses = list(one_gen_subuniverses.values())

    while nodes_queue:
        node = nodes_queue.pop(0)
        while node.incomparables:
            g = node.incomparables.pop(0)
            new_node = node.join(one_gen_nodes[g])
            if new_node.closed not in subuniverses:
                if new_node.incomparables:
                    nodes_queue.append(new_node)
                subuniverses.append(new_node.closed)
                if not (len(new_node.closed) == len(model.universe) and proper):
                    yield new_node.closed


def subuniverses_exhausted(model, subtype=None, proper=True):
    """
    NO DEVUELVE EL SUBUNIVERSO VACIO
    Generador que va devolviendo los subuniversos.
    Intencionalmente no filtra por isomorfismos.

    >>> from folpy.examples.lattices import *
    >>> len(list(subuniverses_exhausted(rhombus, rhombus.type)))
    11
    """
    if not subtype:
        subtype = model.type
    result = []
    subsets = powerset(model.universe)
    checked = [[]]
    for subset in subsets:
        if proper and (len(subset) == len(model.universe)):
            continue
        if subset in checked:
            continue
        subuniv, partials = subuniverse(model, subset, subtype=subtype)
        for partial in partials:
            if partial not in checked:
                checked.append(partial)
        if proper and (len(subuniv) == len(model.universe)):
            continue
        if subuniv not in result:
            result.append(subuniv)
            yield subuniv


def is_subuniverse(model, subset, subtype=None):
    """
    Dado un conjunto, decide si es subuniverso o no
    """
    return len(subset) == len(subuniverse(model, subset, subtype=subtype)[0])


def is_subuniverse_for_lattices(model, possible_subuniverse):
    for x in product(possible_subuniverse, repeat=2):
        if model.join(*x) not in possible_subuniverse:
            return False
        if model.meet(*x) not in possible_subuniverse:
            return False
    return True


def is_subdirect_subuniverse(subuniverse, universe):
    assert type(universe[0]) == tuple, "No es un producto"
    universes = [set(x) for x in zip(*universe)]
    subuniverses = [set(x) for x in zip(*subuniverse)]

    return universes == subuniverses
