#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import subprocess as sp

from .. import files


class LatDraw(object):
    count = 0

    def __init__(self, lattice):
        """
        Toma el input para minion, si espera todas las soluciones y una funcion
        para aplicar a las listas que van a ir siendo soluciones.
        """
        self.id = LatDraw.count
        self.lattice = lattice

        LatDraw.count += 1
        self.lat_draw_path = get_path() + "/"
        self.input_filename = self.lat_draw_path + "input_lat_draw%s" % self.id

        files.create_pipe(self.input_filename)
        self.app = sp.Popen(["java", "-jar", self.lat_draw_path + "LatDraw.jar",
                             self.input_filename],
                            stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        files.write(self.input_filename, self.generate_lat_file())
        # TODO revisar la stderr para reconocer los errores en LatDraw

    def generate_lat_file(self):

        """
        (
          (0 (a b c))
          (a (1))
          (b (1))
          (c (1))
          (1 ())
        )"""
        lattice = self.lattice
        lattice.join_to_le()
        result = ""
        espacio = '" "'
        result += "\n"
        result += "(\n"
        for e in lattice.universe:
            if [r[1] for r in lattice.relations["<="].table() if r[0] == e]:
                result += '  ("%s" ("%s"))\n' % (e, espacio.join(
                    str(r[1]) for r in lattice.relations["<="].table()
                    if r[0] == e))
            else:
                result += '  ("%s" ())\n' % e
        result += ")\n"
        return result

    def kill(self):
        """
        Mata a LatDraw
        """
        if hasattr(self, 'app'):
            self.app.stdout.close()
            self.app.stdin.close()
            self.app.stderr.close()
            self.app.kill()
            del self.app


def get_path():
    """
    Devuelve la ruta del directorio donde está este archivo

    >>> get_path() #doctest: +ELLIPSIS
    '/.../utils/latdraw'
    """
    return os.path.dirname(os.path.realpath(__file__))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
