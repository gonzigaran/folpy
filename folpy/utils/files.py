#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import pickle


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
