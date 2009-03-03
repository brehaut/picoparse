# picoparse

> "Yo dawg, I heard you like parsing…"

Picoparse is a very small parser / scanner library for Python. It is built to make 
constructing parsers  straight forward, and without the complications regular expressions 
bring to the table. The design is inspired by the 
[Parsec](http://www.haskell.org/haskellwiki/Parsec) library from Haskell.

Picoparse will lazily scan input as needed and provides smart backtracking facilities. The 
core library is not specific to text and will work over any iterable type.

## Contents

 * The `picoparse` package is the core of the parser library. 
 * `picoparse.text` contains a few useful tools for building text oriented 
    parsers.
 * `examples\xml.py` is an example implementation of a parser for a reasonable 
    subset of xml.
 * `examples\calculatpr.py` is an example implementation of infix arithmetic
    parser and evaluator.
 * `test.py` runs all the test cases found in `tests`

## Installing

You can install the latest release with `easy_install` or (presumably) `pip`; eg:

    easy_install picoparse

Alternatively, you can get the source as a tarball or with `git` and install with:

    python setup.py install 
 
## Using Picoparse

Parsers are functions that consume input by calling smaller parsers, and returning a value. 
`run_parser` is used to call your top-level parser and provide it with an input stream eg:

    run_parser(my_toplevel_parser, file(input_file).read())

It is recommended that you examine `examples\xml.py` to see a worked example.

An important idea with Picoparse is 'specialising' an existing parser by using `functools.partial` to generate a new parser function. Eg, to create a parser that consumes an 'a':

    a = partial(one_of, 'a')  # roughly equivalent to a = lambda: one_of('a')

and to make a parser that accepts many 'a's:

    many_as = partial(many, a)

## Tracking development and reporting bugs 

This project is tracked with GIT via [GitHub](http://github.com/brehaut/picoparse/), and uses
a [Bugs Everywhere](http://bugseverywhere.org/) bug tracker for tracking bugs.


## See also

Also implementing similar ideas in python are [PyParsing](http://pyparsing.wikispaces.com/) and [Pysec](http://www.valuedlessons.com/2008/02/pysec-monadic-combinatoric-parsing-in.html).