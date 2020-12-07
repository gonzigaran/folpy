# Model Parser for FOLPy

This is a model parser for the [First Order Logic Python Library](https://github.com/gonzigaran/folpy) based in a parser developed by [Pablo Ventura](https://github.com/pablogventura).

## Format of model files

### Comments lines

Line comments must be start with "#". Empty lines are ignored. Example:

```# This file contains the evil model```

### Universe of model

The first line should contain each element of universe separated by a space. Example:

```0 1 2```

### Relations

A relation should start with a declaration line with the name, number of tuples and arity separated by one space. Next lines sould be one for each tuple in the relation containing the relation tuple separated by a space. Example:

```
E 2 3
0 1 2
2 1 0
```

*It must contain exactly the same number of tuples declared in `number of tuples`*

### Operations

A operation should start with a declaration line with the name and arity separated by one space. Next lines sould be one for each tuple in the relation containing a tuple for the graph relation of the operation separated by a space. Example:

```
+ 2
0 0 0
0 1 1
0 2 2
1 0 1
1 1 2
1 2 0
2 0 2
2 1 0
2 2 1
```

*It must contain exactly the same number of tuples for all the domain of the operation*

A operation should start with a declaration line with the name and 0 (will be a 0-arity operation) separated by one space. Next line sould be the element. Example:

```
Zero 0
0
```

## Model Output

### Model

If the file contains relations, `folpy` would read the file as a `Model` object.

### Algebra

If the file contains only operations, `folpy` would read the file as an `Algebra` object.

### Lattice

If the file contains only operations, they are exactly 2, and with operatons names `^` and `v`, then `folpy` would read the file as a `Lattice` object.

