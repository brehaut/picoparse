# picoparse

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
 * `examples/xml.py` is an example implementation of a parser for a reasonable 
    subset of xml.
 * `examples/calculator.py` is an example implementation of infix arithmetic
    parser and evaluator.
 * `test.py` runs all the test cases found in `tests`

## Installing

You can install the latest release with `easy_install` or (presumably) `pip`; e.g:

    easy_install picoparse

Alternatively, you can get the source as a tarball or with `git` and install with:

    python setup.py install 
 
## Using Picoparse

Parsers are functions that consume input by calling smaller parsers, and returning a value. 
`run_parser` is used to call your top-level parser and provide it with an input stream eg:

    run_parser(my_toplevel_parser, file(input_file).read())

It is recommended that you examine `examples/xml.py` to see a worked example.

An important idea with Picoparse is 'specialising' an existing parser by using `functools.partial` to generate a new parser function. Eg, to create a parser that consumes an 'a':

    a = partial(one_of, 'a')  # roughly equivalent to a = lambda: one_of('a')

and to make a parser that accepts many 'a's:

    many_as = partial(many, a)
    
## Examples

The most detailed example is `examples/xml.py` however this might be overwhelming initially. This example is intended to be as a tutorial; it covers a broach range of the features of picoparse as it builds up an minimal (and not fully conformant) XML parser. To get there it includes a sub parser to handle the XML specs character classes.

The simplest are `examples/paren.py` and `examples/paren2.py` however these never got the tutorial treatment. These paren examples count nested parenthesis and brackets. The first one is about the simplest parser you could consider. The second version shows how we can use partial application to specialize one parser into specific ones. This highlights the 'parser combinator' aspect of the design.

`examples/calculator.py` is an example of a simple, general, infix expression parser. If you know exactly which operators you want, there are more sophisticated models that you can use, but they are quite confusing on first examination.

Lastly there is `examples/emailaddress.py` which is a direct mapping of the email address RFC's grammar into picoparse functions. This is the most complex of the examples but should give you an indication how easy it can be to convert formal grammars into pure python.

## Background

A few notes on style; Picoparse is takes advantage of the features of python that support functional programming. If you are new to this, it's worth doing some reading about it. In particular the parsers we create are a style called [Parser Combinators](http://en.wikipedia.org/wiki/Parser_combinators); this is basically a fancy way of say that our parsers are functions and that some parsers are created by combining existing parsers. The most obvious example here is something like `many` which takes another parser as its argument. You'll see more detail about this in the examples, particularly the xml example.

The parser combinator style is a special case of whats known as a [Recursive Decent](http://en.wikipedia.org/wiki/Recursive_descent_parser) (or LL for Left-Left) parser. Each parser function recurses down into more specialized parsers. What makes it special is that it has *Infinite Lookahead* through a feature of the design where it [backtracks](http://en.wikipedia.org/wiki/Backtracking) when it fails to parse. *Lookahead* means that that parser can look at a number of tokens ahead of where you currently are. Traditional recursive decent parser have a fixed lookahead (usually one or two tokens).

A word on tokens; in traditional parsers the design is split into two parts: [Lexical Analysis](http://en.wikipedia.org/wiki/Lexical_analysis) and Parsing. The lexical analysis (or lexing or tokenization) takes a stream of characters and returns a stream of tokens, the parser would then consume this stream of tokens. Parser Combinators let you do both stages at once. Picoparse is general enough that if you do wish to have a separate lexing stage, you can write your parser in terms of tokens instead of characters.   

These two characteristics make parser combinators amazingly expressive. You have the full power of your programming language to bring to bare, and you can describe things with remarkable ease (e.g. how the xml parser parsers characters with a parser made from parsing a formal specification directly from the xml spec for example of this). The trade of is that its not as fast on as some more traditional methods; hence the library is designed to make the development of small or experimental parsers easy and enjoyable rather than focusing on raw speed.

For more detail on how picoparse handles backtracking you will want to look at the primative parsers `choice`, `fail`, `commit` and the decorator `tri`. Choice describes a series of options to try parsing the input with in order. Fail tells the system that the current path doesn't match. Commit indicates that this path has reached a point where the system is not allowed to backtrack past. Typically you only need to worry about committing for performance reasons. If you need to get more detail on this you'll need to examine the BufferWalker class. *Note:* The BufferWalker has accumulated a bunch of features and needs refactoring but neither author has had a chance to undertake this yet.

## How do I…

Heres is a glossary of parsers and combinators organised by outcome to help learn to use Picoparse. Look at doc comments for specifics. 

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
 * `picoparse.sep1` Matches a parser one or more times, with a separator being
   matched between each pair.  
 * `picoparse.optional` Matches a parser zero or one times. 
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
