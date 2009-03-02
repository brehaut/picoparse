# picoparse

> "Yo dawg, I heard you like parsing…"

Picoparse is a very small parser / scanner library for Python. It is built to make constructing parsers  straight forward, and without the complications regular expressions bring to the table. The design is heavily by [Parsec](http://www.haskell.org/haskellwiki/Parsec) from Haskell.

Picoparse will lazily scan input as needed and provides smart backtracking facilities. The core library 
is not specific to text and will work over any iterable type.

## Tracking development and reporting bugs 

This project is tracked with GIT via [GitHub](http://github.com/brehaut/picoparse/), and uses a [Bugs Everywhere](http://bugseverywhere.org/) bug tracker for tracking bugs.

## Contents

 * The `picoparse` package is the core of the parser library. 
 * `picoparse.text` contains a few useful tools for building text oriented parsers.
 * `xml_ex.py` is an example implementation of a parser for a reasonable subset of xml.
 
## See also

Also implementing similar ideas are [PyParsing](http://pyparsing.wikispaces.com/) and [Pysec](http://www.valuedlessons.com/2008/02/pysec-monadic-combinatoric-parsing-in.html).