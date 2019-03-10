# PyPeg

This is the github page for my Bachelor's thesis, "An RPython JIT for Parsing Expression Grammars".

The current title for the JIT, "pypeg" might change soon, since "pypeg" is already the name of an interpreter based on parsing expression grammars.

A more detailed overview of the Project, it's application and results are available under https://github.com/sktroost/PyPeg/blob/master/pypeg/blogpost

however, here is a basic rundown:

--What is this--

A Parsing Expression Grammar is a type of analytic formal grammar, introduced by Bryan Ford in 2004.
Applications for PEGs include pattern-matching, making them an alternative to regular expressions used in tools like grep.
Due to the expressive power of PEGs they can be also used to parse context-free languages.

In Practice, this means we can use PEGs to search for a pattern in a string of text (i.e. search a text for valid URLs),
or parse a string of a certain format (i.e. JSON, C).

--How does it work--

LPeg is another interpreter that implements PEGs by parsing them into bytecode and executing that through a virtual machine (VM).
PyPeg contains a VM that uses the same bytecode generated by LPeg, but executing them significantly faster at sufficiently large filesizes (see https://github.com/sktroost/PyPeg/tree/master/pypeg/plots/blogpostplots )

This speedup is achieved by using PyPy's RPython toolchain, which allows our python program to be compiled into C-Code, and out Interpreter to generate x86-Assembly code for better performance.

--How do I install it?--

Currently, this software requires a lot of dependencies and is not very user friendly. Current requirements include

-lua5.2 (as LPeg is used for bytecode generation)
-cffi (pypy requirement)
-pypy source (https://bitbucket.org/pypy/pypy/src)

A more detailed installation guide will be available soon.

--On what platforms does it run?--
Currently x86-Linux only.
