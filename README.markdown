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
 * `examples\calculator.py` is an example implementation of infix arithmetic
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

## How do I…

Heres is a glossary of parsers and combinators by outcome to help learn to use Picoparse. Look at doc comments for specifics. 

### Match input

Matching input is done by calling primitive parsers.

 * `picoparse.one_of` Match one item in the input stream that is equal to the
   argument. Requires that the item supports `==`.
 * `picoparse.not_one_of` Match one item that is not equal to the argument.
 * `picoparse.satisfies` Matches one item that satisfies a guard function.
 * `picoparse.any_token` Matches one of any item. 
 * `picoparse.eof` Matches the end of input.
 * `picoparse.text.whitespace_char` Matches a single whitespace character
 * `picoparse.text.newline` Matches a single newline character
 * `picoparse.text.quote` Match one single or double quote
 
### Match multiple items
 
Matching multiple items is achieved by passing a primitive parser to a combinator function. These parsers are all greedy

 * `picoparse.many` Matches a parser zero or more times.
 * `picoparse.many1` Matches a parser one or more times.
 * `picoparse.many_until` Matches a parser zero or more times until the 
   terminating parser matches.
 * `picoparse.many_until1` Matches a parser one or more times until the 
   terminating parser matches.
 * `picoparse.sep` Matches a parser zero or more times, with a separator being
   matched between each pair.    
 * `picoparse.sep` Matches a parser one or more times, with a separator being
   matched between each pair.  
 * `picoparse.optional` Matches zero or one of parser. 
 * `picoparse.text.whitespace` Match zero or more whitespace characters
 * `picoparse.text.whitespace1` Match one or more whitespace characters
   
### Make a choice

Choosing between possible parsers is achieved with the `choice` combinator, often assisted by `tri`.

 * `picoparse.choice` Match one of the parsers passed in order. If none match,
   the choice fails to match as well.
 * `picoparse.tri` should decorate a parser that consumes multiple pieces of 
   input. You can `picoparse.commit` to the choice if you know that no 
   other choice should succeed. (see calculator and xml examples for this in 
   use.) `tri` will automatically commit if it reaches the end of the decorated 
   parser.

### Match a sequence

 * `picoparse.string` will apply `one_of` in for each item in the iterable 
    argument. Note that this is any string of matches, not just for character 
    parsing.
 * `picoparse.text.caseless_string` will match the given str without regard 
    for upper or lower case (text only)
 * `picoparse.cue` for something ignorable that cues you to what you really 
    want to match. eg, matching "#x" in a hex parser
 * `picoparse.follow` for something ignorable that follows what you really want 
    to match. eg, matching "l" after a long integer.
 * `picoparse.seq` for matching a specific set of (possibly named) parsers.

### Matching something wrapped
 
 * `picoparse.text.lexeme` match a parser with optional whitespace on either    
    side.
 * `picoparse.text.quoted` Match a parser with in single or double quote 
    characters until a matching quote is found.
 
## Tracking development and reporting bugs 

This project is tracked with GIT via [GitHub](http://github.com/brehaut/picoparse/), and uses
a [Bugs Everywhere](http://bugseverywhere.org/) bug tracker for tracking bugs.


## See also

Also implementing similar ideas in python are [PyParsing](http://pyparsing.wikispaces.com/) and [Pysec](http://www.valuedlessons.com/2008/02/pysec-monadic-combinatoric-parsing-in.html).