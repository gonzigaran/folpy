#!/usr/bin/env python
# -*- coding: utf8 -*-

# Minion interface code Peter Jipsen 2011-03-26 alpha version
# requires sage.chapman.edu/sage/minion_20110326.spkg

import codecs
import os
import pickle
import subprocess as sp
from select import poll, POLLIN
from itertools import product
from collections import defaultdict

from ...semantics import Homomorphism, Embedding, Isomorphism
from .. import misc


class MinionSol(object):
    count = 0

    def __init__(self, input_data, allsols=True, fun=lambda x: x):
        """
        Toma el input para minion, si espera todas las soluciones y una
        funcion para aplicar a las listas que van a ir siendo soluciones.
        """
        self.id = MinionSol.count
        MinionSol.count += 1

        self.fun = fun
        self.allsols = allsols
        self.minion_path = get_path() + "/"

        self.input_filename = self.minion_path + "input_minion%s" % self.id
        create_pipe(self.input_filename)

        minionargs = ["-printsolsonly", "-randomseed", "0"]
        if allsols:
            minionargs += ["-findallsols"]
        minionargs += [self.input_filename]

        self.minionapp = sp.Popen([self.minion_path + "minion"] + minionargs,
                                  stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        write(self.input_filename, input_data)
        self.EOF = False
        self.solutions = []

    def __parse_solution(self):
        """
        Bloquea hasta conseguir una solucion, o el EOF
        La parsea y devuelve una lista
        """
        str_sol = self.minionapp.stdout.readline().decode('utf-8')
        if str_sol:
            str_sol = str_sol[:-1]  # borro el \n
            try:
                result = list(map(int, str_sol.strip().split(" ")))
                for i, v in enumerate(result):
                    if v == -1:
                        result[i] = None
                result = {(i,): v for i, v in enumerate(result)}
                # ACA IRIAN LAS TRADUCCIONES DE NOMBRES EN EL FUTURO
            except ValueError:
                str_sol += "\n"
                # leo toda la respuesta de minion para saber que paso
                str_sol += self.minionapp.stdout.read().decode('utf-8')
                raise ValueError("Minion Error:\n%s" % str_sol)
            if not self.allsols:
                self.EOF = True
                self.__terminate()
            return result
        else:
            str_err = self.minionapp.stderr.read().decode('utf-8')
            if str_err:
                raise ValueError("Minion Error:\n%s" % str_err)
            self.EOF = True
            self.__terminate()

    def __iter__(self):
        for solution in self.solutions:
            yield self.fun(solution)

        while not self.EOF:
            solution = self.__parse_solution()
            if solution:
                self.solutions.append(solution)
                yield self.fun(solution)

    def __getitem__(self, index):
        try:
            return self.fun(self.solutions[index])
        except IndexError:
            for i, solution in enumerate(self):
                if i == index:
                    # no hace falta aplicar self.fun porque esta llamando a
                    # __iter__
                    return solution
            raise IndexError("There aren't so many solutions.")

    def __bool__(self):
        if self.solutions or self.EOF:
            return bool(self.solutions)
        else:
            solution = self.__parse_solution()
            if solution:
                self.solutions.append(solution)
                return True
            else:
                return False

    def __len__(self):
        if not self.EOF:
            for i in self:
                pass
        return len(self.solutions)

    def __terminate(self):
        """
        Mata a Minion
        """
        if hasattr(self, 'minionapp'):
            self.minionapp.stdout.close()
            self.minionapp.stdin.close()
            self.minionapp.stderr.close()
            self.minionapp.kill()

            del self.minionapp
        remove(self.input_filename)

    def __del__(self):
        """
        Si no lo habia matado, mata a Minion.
        """
        if not self.EOF:
            self.__terminate()


class MorphMinionSol(MinionSol):
    """
    Soluciones de Minion que son morfismos
    Necesita que las estructuras sean de universos del tipo 0...n
    """

    def __init__(self,
                 morph_type,
                 subtype,
                 source,
                 target,
                 inj=None, surj=None, allsols=True, without=[]):
        self.morph_type = morph_type
        self.subtype = subtype
        self.source, self.source_renames = source.continous()
        self.target, self.target_renames = target.continous()
        self.inj = inj
        self.surj = surj
        self.EOF = False
        if self.morph_type == Homomorphism:
            input_data = self.__input_homo(without)
        elif self.morph_type == Embedding:
            self.inj = True
            input_data = self.__input_embedd(without)
        elif self.morph_type == Isomorphism:
            self.inj = True
            self.surj = True
            input_data = self.__input_embedd(without)
        else:
            raise IndexError("Morphism unknown")

        self.fun = lambda x: self.morph_type(
            {(self.source_renames[k[0]],): self.target_renames[v]
                for k, v in x.items()},
            source,
            target,
            self.subtype,
            antitype=[],
            inj=self.inj,
            surj=self.surj
                                            )  # funcion que tipa los morfismos
        super(MorphMinionSol, self).__init__(input_data, allsols, fun=self.fun)

    def __minion_name(self, oprel):
        """
        Traduce los nombres de las operaciones/relaciones
        """
        # Minion accepts only letters for first character of names
        if oprel.isalpha():
            return oprel

        ops = {"^": "m", "+": "p", "-": "s", "*": "t", "<=": "leq"}
        if oprel in ops:
            return ops[oprel]
        else:
            # le agrego espacios para evitar los = que mete b64
            oprel += " " * ((3 - len(oprel)) % 3)

            return codecs.encode(bytearray(oprel, "ascii"),
                                 "base64").decode("ascii")[:-1]

    def __oprel_table(self, symbol, oprel, prefix=""):
        """
        Devuelve un string con la tabla que representa a la relacion/operacion
        en minion
        """
        table = oprel.table()
        table_name = prefix + self.__minion_name(symbol)
        height = len(table)
        width = oprel.arity()
        if not oprel.relation:
            width += 1
        result = ""
        for row in table:
            result += " ".join(map(str, row)) + "\n"
        result = "%s %s %s\n" % (table_name, height, width) + result
        return result

    def __input_homo(self, without=[]):
        """
        Genera un string para darle a Minion para tener los homomorfismos de
        source en target quitando los que aparecen en without.
        """
        A = self.source
        B = self.target

        result = "MINION 3\n\n"
        result += "# Busca homomorfismos de \n"
        result += misc.comment(str(A))
        result += "# en\n"
        result += misc.comment(str(B))
        if self.inj:
            result += "# que sean inyectivos\n"
        if self.surj:
            result += "# que sean suryectivos\n"
        result += "\n"
        result += "**VARIABLES**\n"
        result += "DISCRETE f[%s]{0..%s}\n\n" % (A.cardinality, B.cardinality-1)
        result += "**TUPLELIST**\n"
        for op in self.subtype.operations:
            result += self.__oprel_table(op, B.operations[op]) + "\n"
        for rel in self.subtype.relations:
            result += self.__oprel_table(rel, B.relations[rel]) + "\n"

        if without:
            result += self.morphisms_to_minion_table(without) + "\n"

        result += "**CONSTRAINTS**\n"
        if self.inj:
            # exige que todos los valores de f
            result += "alldiff([f[%s]])\n" % "],f[".join(map(str, A.universe))
            # sean distintos para el univ de partida
        if self.surj:
            for i in B.universe:
                # exige que i aparezca al menos una vez en el "vector" f
                result += "occurrencegeq(f, " + str(i) + ", 1)\n"

        for op in self.subtype.operations:
            cons = A.operations[op].table()
            for row in cons:
                result += "table([f[" + "],f[".join(map(str, row)
                                                    ) + "]],%s)\
                                                \n" % self.__minion_name(op)
            result += "\n"

        for rel in self.subtype.relations:
            cons = A.relations[rel].table()
            for row in cons:
                result += "table([f[" + "],f[".join(map(str, row)
                                                    ) + "]],%s)\
                                                \n" % self.__minion_name(rel)
            result += "\n"

        if without:
            result += "negativetable(f,without)\n"

        result += "**EOF**\n"
        return result

    def __input_embedd(self, without=[]):
        """
        Genera un string para darle a Minion para tener los embeddings de A en B
        """
        A = self.source
        B = self.target

        result = "MINION 3\n\n"
        result += "# Busca embeddings de a en b\n"
        if self.inj:
            result += "# que sean inyectivos\n"
        if self.surj:
            result += "# que sean suryectivos\n"
        result += "\n"
        result += "**VARIABLES**\n"
        result += "DISCRETE f[%s]{0..%s}\n\n" % (A.cardinality,
                                                 B.cardinality-1)
        result += "DISCRETE g[%s]{-1..%s}\n\n" % (B.cardinality,
                                                  A.cardinality-1)
        result += "**SEARCH**\n"
        result += "PRINT [f]\n\n"  # para que no me imprima los valores de g
        result += "**TUPLELIST**\n"

        for op in self.subtype.operations:
            result += self.__oprel_table(op,
                                         B.operations[op], prefix="b") + "\n"
        for rel in self.subtype.relations:
            result += self.__oprel_table(rel,
                                         B.relations[rel], prefix="b") + "\n"
        for rel in self.subtype.relations:
            result += self.__oprel_table(rel,
                                         A.relations[rel], prefix="a") + "\n"
        if without:
            result += self.morphisms_to_minion_table(without) + "\n"
        result += "**CONSTRAINTS**\n"
        if self.inj:
            # exige que todos los valores de f
            result += "alldiff([f[%s]])\n" % "],f[".join(map(str, A.universe))
            # sean distintos para el univ de partida
        if self.surj:
            for i in B.universe:
                # exige que i aparezca al menos una vez en el "vector" f
                result += "occurrencegeq(f, " + str(i) + ", 1)\n"

        for op in self.subtype.operations:
            cons = A.operations[op].table()
            for row in cons:
                result += "table([f[" + "],f[".join(map(str, row)
                                                    ) + "]],%s)\
                                        \n" % ("b" + self.__minion_name(op))
            result += "\n"
        for rel in self.subtype.relations:
            cons = A.relations[rel].table()
            for row in cons:
                result += "table([f[" + "],f[".join(map(str, row)
                                                    ) + "]],%s)\
                                        \n" % ("b" + self.__minion_name(rel))
            result += "\n"
        for rel in self.subtype.relations:
            cons = B.relations[rel].table()
            for row in cons:
                result += "watched-or({"
                for i in row:
                    result += "element(g, %s, -1)," % i
                result += "table([g[" + "],g[".join(map(str, row))
                result += "]],%s)})\n" % ("a" + self.__minion_name(rel))
            result += "\n"
        for i in A.universe:
            result += "element(g, f[%s], %s)\n" % (i, i)  # g(f(x))=X

        # cant de valores en el rango no en dominio
        result += "occurrencegeq(g, -1, %s)\n" % (max(B.universe) +
                                                  1 - A.cardinality)
        if without:
            result += "negativetable(f,without)\n"
        result += "**EOF**\n"
        return result

    def morphisms_to_minion_table(self, morphs):
        """
        Convierte una lista de morfismos en una tabla que entiende minion
        """
        table = [self.morphism_to_minion_format(morph) for morph in morphs]
        table_name = "without"
        height = len(table)
        width = len(table[0])
        result = ""
        for row in table:
            result += " ".join(map(str, row)) + "\n"
        result = "%s %s %s\n" % (table_name, height, width) + result
        return result

    def morphism_to_minion_format(self, morph):
        """
        Genera la entrada de minion para un morfismo.
        """
        result = [-1] * (max([x[0] for x in list(morph.dict.keys())]) + 1)
        for i in list(morph.dict.keys()):
            result[i[0]] = morph.dict[i]
        return result


class ParallelMorphMinionSol(object):

    """
    Maneja varias consultas del mismo tipo a Minion que corren en paralelo.
    """

    def __init__(self,
                 morph_type,
                 subtype,
                 sources,
                 targets,
                 inj=None,
                 surj=None,
                 allsols=False,
                 cores=100,
                 without={}):

        self.targets = list(targets)
        self.morph_type = morph_type
        self.subtype = subtype
        try:
            self.sources = list(sources)
        except TypeError:
            self.sources = [sources]
        self.inj = inj
        self.surj = surj
        self.allsols = allsols
        self.solution = None
        self.without = defaultdict(list, without)
        self.queue = list(product(self.sources, self.targets))

        self.poll = poll()
        self.minions = {}
        self.iterators = {}

        for i in range(cores):
            self.next_to_running()

    def next_to_running(self):
        """
        Pone a la siguiente instancia de Minion a andar
        """
        if self.queue:
            source, target = self.queue.pop()
            new_minion = MorphMinionSol(self.morph_type,
                                        self.subtype,
                                        source,
                                        target,
                                        inj=self.inj,
                                        surj=self.inj,
                                        allsols=self.allsols,
                                        without=self.without[(source, target)])
            fd = new_minion.minionapp.stdout.fileno()
            self.minions[fd] = new_minion
            self.iterators[fd] = iter(new_minion)
            self.poll.register(fd, POLLIN)

    def read(self, fd):
        """
        Lee un file descriptor y lo vuelve a poner en el poll
        """
        if self.minions[fd]:
            result = self.minions[fd][0]
        else:
            result = False
        del self.minions[fd]
        del self.iterators[fd]
        self.poll.unregister(fd)
        return result

    def solve(self):
        """
        Devuelve si hay una solucion, en cuyo caso la devuelve.
        """
        if self.solution is None:
            while self.queue or self.minions:
                for (fd, event) in self.poll.poll():
                    result = self.read(fd)
                    if result:
                        self.solution = result
                        if not self.allsols:
                            for f in list(self.minions.keys()):
                                self.minions[f].__del__()
                        return self.solution
                    else:
                        if self.queue:
                            self.next_to_running()
            self.solution = False
            return False
        else:
            return self.solution

    def __iter__(self):
        while self.queue or self.minions:
            for (fd, event) in self.poll.poll():
                try:
                    result = next(self.iterators[fd])
                    assert not self.minions[fd].EOF
                    self.poll.register(fd, POLLIN)
                    yield result
                except StopIteration:
                    assert self.minions[fd].EOF
                    self.poll.unregister(fd)
                    self.minions[fd].__del__()
                    del self.minions[fd]
                    if self.queue:
                        self.next_to_running()


def homomorphisms(source,
                  target,
                  subtype,
                  inj=None,
                  surj=None,
                  allsols=True,
                  without=[]):
    """
    call Minion to calculate all homomorphisms from A to B

    >>> from folpy.examples.lattices import gen_chain, rhombus
    >>> c2 = gen_chain(2)
    >>> len(homomorphisms(rhombus, c2, rhombus.type))
    4
    """
    if inj and len(source) > len(target):
        # evidentemente no hay homos inyectivos
        return []
    if surj and len(source) < len(target):
        # evidentemente no hay homos sobreyectivos
        return []
    return MorphMinionSol(Homomorphism,
                          subtype,
                          source,
                          target,
                          inj,
                          surj,
                          allsols,
                          without)


def embeddings(source, target, subtype, surj=None, allsols=True, without=[]):
    """
    call Minion to calculate all embeddings of A into B

    >>> from folpy.examples.posets import gen_chain, rhombus
    >>> c2 = gen_chain(2)
    >>> len(embeddings(c2, rhombus, rhombus.type))
    5
    """
    if len(source) > len(target):
        # evidentemente no hay embedding
        return []
    return MorphMinionSol(Embedding,
                          subtype,
                          source,
                          target,
                          True,
                          surj,
                          allsols,
                          without)


def isomorphisms(source, target, subtype, allsols=True, without=[]):
    """
    call Minion to calculate all homomorphisms from A to B

    >>> from folpy.examples.posets import gen_chain, rhombus, M3
    >>> c2 = gen_chain(2)
    >>> len(isomorphisms(c2, rhombus, rhombus.type))
    0
    >>> len(isomorphisms(c2, c2, c2.type))
    1
    >>> i = isomorphisms(c2, c2, c2.type)[0]
    >>> len(isomorphisms(c2, c2, c2.type, without=[i]))
    0
    >>> len(isomorphisms(M3, M3, M3.type))
    6
    """
    if len(source) != len(target):
        # evidentemente no son isomorfos
        return []
    return MorphMinionSol(Isomorphism,
                          subtype,
                          source,
                          target,
                          True,
                          True,
                          allsols,
                          without)


def is_homomorphic_image(source, target, subtype, without=[]):
    """
    return homomorphism if B is a homomorphic image of A (uses Minion)
    else returns False

    >>> from folpy.examples.posets import gen_chain, rhombus, M3
    >>> c2 = gen_chain(2)
    >>> bool(is_homomorphic_image(c2, M3, c2.type))
    True
    >>> bool(is_homomorphic_image(M3, rhombus, M3.type))
    True
    """
    h = homomorphisms(source, target, subtype, allsols=False, without=without)
    if h:
        return h[0]
    else:
        return False


def is_substructure(source, target, subtype, without=[]):
    """
    return embedding if B is a substructure of A (uses Minion)
    else returns False

    >>> from folpy.examples.posets import gen_chain, rhombus, M3
    >>> c2 = gen_chain(2)
    >>> bool(is_substructure(c2, M3, c2.type))
    True
    >>> bool(is_substructure(M3, rhombus, M3.type))
    False
    >>> bool(is_substructure(rhombus, M3, M3.type))
    True
    """
    e = embeddings(source, target, subtype, allsols=False, without=without)
    if e:
        return e[0]
    else:
        return False


def is_isomorphic(source, target, subtype, without=[]):
    """
    return isomorphism if A is isomorphic to B (uses Minion)
    else returns False

    >>> from folpy.examples.posets import gen_chain, rhombus, M3
    >>> c2 = gen_chain(2)
    >>> bool(is_isomorphic(c2, M3, c2.type))
    False
    >>> bool(is_isomorphic(M3, M3, M3.type))
    True
    """
    i = isomorphisms(source, target, subtype, allsols=False, without=without)
    if i:
        return i[0]
    else:
        return False


def is_isomorphic_to_any(source, targets, subtype, cores=10, without=[]):
    """
    Devuelve un iso si source es isomorfa a algun target
    sino, false. Usa multiples preguntas a minion en paralelo.
    """
    if not targets:
        return False

    i = ParallelMorphMinionSol(
        Isomorphism, subtype, source, targets, cores=cores, without=without)
    return i.solve()


def get_path():
    """
    Devuelve la ruta del directorio donde está este archivo

    >>> get_path() #doctest: +ELLIPSIS
    '/.../utils/minion'
    """
    return os.path.dirname(os.path.realpath(__file__))


def object_to_file(obj, path):
    """
    Guarda un objeto en un archivo

    >>> object_to_file([1,3],"testfile")
    >>> l = file_to_object("testfile")
    >>> l
    [1, 3]
    >>> remove("testfile")
    """
    f = open(path, "wb")
    pickle.dump(obj, f)
    f.close()


def file_to_object(path):
    """
    Lee un objeto en un archivo

    >>> object_to_file([1,3],"testfile")
    >>> l = file_to_object("testfile")
    >>> l
    [1, 3]
    >>> remove("testfile")
    """
    f = open(path, "rb")
    obj = pickle.load(f)
    f.close()
    return obj


def create_pipe(path):
    """
    Crea un named pipe

    """

    try:
        os.mkfifo(path)
    except OSError:
        # ya existe
        pass


def remove(path):
    """
    Elimina un archivo
    """
    try:
        os.remove(path)
    except OSError:
        # no existe
        pass


def write(path, data):
    """
    Escribe datos en un archivo
    """
    f = open(path, 'w')
    f.write(data)
    f.close()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
