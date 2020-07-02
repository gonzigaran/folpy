#!/usr/bin/env python
# -*- coding: utf8 -*-

from ..utils import Function, indent
from .congruences import Congruence


class Homomorphism(Function):

    """
    Homomorfismos

    >>> from folpy.examples.posets import gen_chain
    >>> c2 = gen_chain(2)
    >>> h = Homomorphism({(0,):1,(1,):1}, c2, c2, c2.type)
    >>> print(h)
    Homeomorphism(
      [0] -> 1,
      [1] -> 1,
    ,
      Type({},{'<=': 2})
    ,
    )
    """

    def __init__(self, d, source, target, subtype, antitype=[], inj=None,
                 surj=None):
        super(Homomorphism, self).__init__(d)
        self.source = source
        self.target = target
        self.subtype = subtype
        # lleva una lista de relaciones/operaciones que rompen el morfismo
        self.antitype = antitype
        assert isinstance(antitype, list), type(antitype)
        self.inj = inj
        self.surj = surj
        assert self.arity() == 1
        # assert self.subtype.is_subtype_of(source.fo_type)
        #  and self.subtype.is_subtype_of(target.fo_type)

        if self.is_auto():
            self.stype = "Homeomorphism"
        else:
            self.stype = "Homomorphism"

    def __repr__(self):
        table = ["%s -> %s," % (x[:-1], x[-1]) for x in self.table()]
        result = "%s(\n" % self.stype
        result += indent("\n".join(table)) + ",\n"
        # result += indent(repr(self.source) + ",")
        # result += indent(repr(self.target) + ",")
        result += indent(repr(self.subtype)) + ",\n"
        if self.antitype:
            result += indent("antitype= " + repr(self.antitype)) + ",\n"
        if self.inj:
            result += indent("Injective,")
        if self.surj:
            result += indent("Surjective,")
        result += ")"
        return result

    def inverse(self):
        """
        Devuelve la inversa del morfismo
        Para que sea funcion la inversa tiene que ser injectivo.
        """
        assert self.inj

        d = {}
        for k in self.dict:
            if len(k) > 1:
                d[(self.dict[k],)] = k
            else:
                d[(self.dict[k],)] = k[0]
        return type(self)(d, self.target, self.source, self.subtype,
                          self.antitype, self.inj, self.surj)

    def is_embedding(self):
        """
        Devuelve si el homomorfismo es un embedding.
        Revisa la vuelta de las relaciones.
        """
        for rel in self.subtype.relations:
            if not self.inverse_preserves_rel(rel):
                return False

        return True

    def composition(self, g):
        """
        Compone con otro morfismo, F.compone(G) = F o G
        y devuelve un nuevo morfismo
        El tipo del morfismo esta dado por el de menor 'grado' entre los dos
        El tipo de primer orden es el mas chico entre los dos.
        """
        assert set(g.target.universe).issubset(set(self.source.universe))
        # el padre es el tipo menos restrictivo
        if issubclass(type(g), type(self)):
            morph_type = type(self)
        else:
            morph_type = type(g)
        if self.subtype.is_subtype_of(g.subtype):
            subtype = self.subtype
        else:
            subtype = g.subtype
        antitype = self.antitype + g.antitype

        result = morph_type(g.dict, g.source, self.target, subtype, antitype)
        result.map_in_place(self)

        result.inj = None
        result.surj = None
        if self.inj and g.inj:
            result.inj = True
        if self.surj and g.surj:
            result.surj = True

        return result

    def is_auto(self):
        """
        Es un 'auto-morfismo'?
        """
        return self.source == self.target

    def preserves_relation(self, rel):
        """
        Revisa si el homomorfismo preserva la relacion.

        Sean A un conjunto, R ⊆ Aⁿ y 𝛾:D ⊆ A → A una función.
        Diremos que 𝛾  preserva a R si para todo (a₁,...,aₙ) ∈ R∩Dⁿ
        se tiene que (𝛾(a₁),...,𝛾(aₙ)) ∈ R.

        >>> from folpy.examples.posets import *
        >>> rhombus.is_homomorphic_image(rhombus, rhombus.type)
        Homeomorphism(
          [0] -> 0,
          [1] -> 0,
          [2] -> 0,
          [3] -> 0,
        ,
          Type({},{'<=': 2})
        ,
        )
        >>> h = rhombus.is_homomorphic_image(rhombus, rhombus.type)
        >>> h.preserves_relation("<=")
        True
        """

        if rel in self.subtype.relations:
            return True
        elif rel in self.antitype:
            return False
        else:
            result = self.__preserves_relations(
                self.source.relations[rel], self.target.relations[rel])
            if not result:
                self.antitype.append(rel)
            return result

    def preserves_operation(self, op):
        # TODO ES CORRECTA LA IDEA?
        """
        Revisa preservacion de una operacion a traves de revisar la
         preservacion ida y vuelta de la relacion dada por el grafico
        """
        if op in self.subtype.operations:
            return True
        elif op in self.antitype:
            return False
        else:
            rel_source = self.source.operations[
                op].graph_fo_relation(self.source.universe)
            rel_target = self.target.operations[
                op].graph_fo_relation(self.target.universe)
            result = self.__preserves_relations(rel_source, rel_target)
            if not result:
                self.antitype.append(op)
            return result

    def inverse_preserves_rel(self, rel):
        """
        Prueba la inversa preserve la relacion
        """
        if isinstance(self, Embedding) and rel in self.subtype.relations:
            return True
        elif rel in self.antitype:
            return False
        else:
            result = self.__inverse_preserves_relations(
                self.source.relations[rel], self.target.relations[rel])
            if not result:
                self.antitype.append(rel)
            return result

    def preserves_type(self, supertype, check_inverse=False):
        """
        Revisa que el homomorfismo tambien sea homomorfismo para el supertipo.

        Revisa preservacion de las relaciones que tiene supertype, que no
        tiene el morfismo en su tipo.
        Si preserva el tipo, se cambia de tipo a ese.

        >>> from folpy.examples.lattices import M3, ret_type
        >>> from folpy.examples.posets import poset_type
        >>> M3.is_homomorphic_image(M3, ret_type)
        Homeomorphism(
          [0] -> 0,
          [1] -> 0,
          [2] -> 0,
          [3] -> 0,
          [4] -> 0,
        ,
          AlgebraicType({'^': 2, 'v': 2})
        ,
        )
        >>> h = M3.is_homomorphic_image(M3, ret_type)
        >>> M3.join_to_le()
        >>> h.preserves_type(ret_type + poset_type)
        True
        """
        checktype = supertype - self.subtype

        for rel in checktype.relations:
            if (not self.preserves_relation(rel) or
                    (check_inverse and not self.inverse_preserves_rel(rel))):
                return False
        for op in checktype.operations:
            if not self.preserves_operation(op):
                return False

        # se auto promueve a un homo del supertipo
        self.subtype = supertype.copy()
        return True

    def kernel(self):
        """
        Devuelve el kernel del homomorfismo
        """
        k = []
        for x in self.source.universe:
            for y in self.source.universe:
                if self.dict[(x,)] == self.dict[(y,)]:
                    k.append((x, y))
        return Congruence(k, self.source)

    def image_model(self):
        """
        Devuelve la imagen como submodelo de target
        """
        return self.target.restrict(list(self.image()), self.target.fo_type)

    def __preserves_relations(self, rel_a, rel_b):
        """
        Revisa la preservacion entre dos relaciones.
        Lo esperable seria que las dos relaciones tuvieran el mismo simbolo
        en las estructuras A y B
        """
        result = True
        for t in rel_a.domain():
            if rel_a(*t):
                result = result and rel_b(*self.vector_call(t))
        return result

    def __inverse_preserves_relations(self, rel_a, rel_b):
        """
        Prueba que ("rel_b" interseccion Im(f)^aridad(rel_b)) este
         contenido en f("rel_a")
        Funcion de Camper
        """
        # frelSource = [map(lambda x: self(x), row) for row in rel_a.table()]
        frelSource = []
        for row in rel_a.table():
            if set(row) <= set(x[0] for x in self.domain()):
                frelSource.append([self(x) for x in row])
        for row in rel_b.table():
            if all(x in self.image() for x in row):
                if row not in frelSource:
                    return False
        return True


class Embedding(Homomorphism):

    """
    Embeddings

    >>> from folpy.examples.posets import gen_chain
    >>> c2 = gen_chain(2)
    >>> h = Embedding({(0,):1,(1,):1}, c2, c2, c2.type)
    >>> print(h)
    Autoembedding(
      [0] -> 1,
      [1] -> 1,
    ,
      Type({},{'<=': 2})
    ,
      Injective,
    )
    """

    def __init__(self, d, source, target, subtype,
                 antitype=[], inj=True, surj=None):
        assert inj
        super(Embedding, self).__init__(
            d, source, target, subtype, antitype, inj, surj)
        if self.is_auto():
            self.stype = "Autoembedding"
        else:
            self.stype = "Embedding"

    def isomorphism_to_image(self):
        """
        Devuelve un isomorfismo a la imagen del embedding.
        """
        return Isomorphism(self.dict, self.source,
                           self.target.restrict(list(self.image()),
                                                self.subtype),
                           self.subtype, self.antitype)

    def preserves_type(self, supertype, check_inverse=True):
        """
        Revisa la preservacion del tipo, pero tiene el chequeo de inversa
         predeterminado
        """
        return super(Embedding, self).preserves_type(supertype, check_inverse)

    def is_subdirect_embedding(self):
        """
        Checkea si el embedding es subdirecto
        """
        return self.image_model().is_subdirect()


class Isomorphism(Embedding):

    """
    Isomorfismos

    >>> from folpy.examples.posets import gen_chain
    >>> c2 = gen_chain(2)
    >>> h = Isomorphism({(0,):1,(1,):1}, c2, c2, c2.type)
    >>> print(h)
    Automorphism(
      [0] -> 1,
      [1] -> 1,
    ,
      Type({},{'<=': 2})
    ,
      Injective,
      Surjective,
    )

    """

    def __init__(self, d, source, target, subtype, antitype=[],
                 inj=True, surj=True):
        assert inj and surj
        super(Isomorphism, self).__init__(
            d, source, target, subtype, antitype, inj, surj)
        if self.is_auto():
            self.stype = "Automorphism"
        else:
            self.stype = "Isomorphism"


if __name__ == "__main__":
    import doctest
    doctest.testmod()
