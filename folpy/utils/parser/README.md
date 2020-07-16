# Format of model files

Line comments must be start with "#". Empty lines are ignored. Example:

```# This file contains the evil model```

The first line should contain each element of universe separated by a space. Example:

```0 1 2```

A relation should start with a declaration line with the name, number of tuples and arity separated by one space. Next lines sould be one for each tuple in the relation containing the relation tuple separated by a space. Example:

```
E 2 3
0 1 2
2 1 0
```

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

A operation should start with a declaration line with the name and 0 (will be a 0-arity operation) separated by one space. Next line sould be the element. Example:

```
Zero 0
0
```
th "#"
