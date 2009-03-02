"""This is a simple _example_ of using picoparse to parse XML - not for real use. 

This example looks at XML as it is a textual stucture that the majority are familiar with. 
Comments throughout the file explain what is going on
"""
# Copyright (c) 2009, Andrew Brehaut, Steven Ashley
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
# * Redistributions of source code must retain the above copyright notice, 
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice, 
#   this list of conditions and the following disclaimer in the documentation  
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF 
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN 
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.

# We are going to import a lot of parsers and parser combinators from picoparse.
# You dont need to understand them all right away. This style of parser library lends itself 
# to learning and groking small pieces at a time
from picoparse import one_of, many, many1, not_one_of, run_parser, tri, commit, optional, fail
from picoparse import choice, string, peek, cut, string, eof, many_until, any_token, satisfies
from picoparse import sep, sep1, compose, cue
from picoparse.text import build_string, caseless_string, quoted, quote, whitespace, whitespace1
from picoparse.text import lexeme
from functools import partial

# We define common primative parsers by partial application. This is similar to the lexical 
# analysis stage of a more traditional parser tool.
#
# Note here is that these simple parsers are just specialisations of the general purpose
# 'one_of' parser that will accept any item that is the provided iterable.
#   partial(one_of, '<') is equivalent to lambda: one_of('<')
# This is an important idea with picoparse, as it lets you express the specialisation more
# succinctly and more precisely than defing a whole new function 
open_angle = partial(one_of, '<')
close_angle = partial(one_of, '>')
equals = partial(one_of, '=')
decimal_digit = partial(one_of, '0123456789')
hex_decimal_digit = partial(one_of, '0123456789AaBbCcDdEeFf')

# hex_value is a simple parser that knows how to parse out a set of hex digits and return them
# as an integer. build_string wraps up u''.join(iterable) for us. 
def hex_value():
    return int(build_string(many(hex_decimal_digit)), 16)

# The next primatives we need are for the XML name type. The specification for this is reasonably 
# involved; instead of manually implementing it, we are going to create a new parser for the
# grammer that the spec ifself uses. This parser will generate a new parser for us.
#
# To be clear, this piece of code creates a parser that runs when the module is loaded, not when
# parsing the XML itself.
#
# First we are going to create parsers for the individual characters that may appear in the spec,
# then we are going to define parsers for a character range.

# In the XML character spec, a hexdecimal digit begins with '#x'; cue is a parser combinator.
# it takes two parsers, runs the first, and then if that accepts, it runs the second and returns 
# the result. You can see that we are defining a specialisation of cue with a specialisation of 
# string (which only accepts if the input matches the iterable it is given), and hex_value above.
char_spec_hex = partial(cue, partial(string, '#x'), hex_value)

# The next two parsers use a function 'compose' as well as nested partials. This is creating
# a parser that returns a parser. compose(f, g) is equivalent to f(g()). 
char_spec_single_char = compose(partial(partial, one_of), quoted)
char_spec_single_hex_char = compose(partial(partial, one_of), char_spec_hex)

# Now that we have parsers for the different notations for characters, we need to create a parser
# that can choose the correct parser to use. For this we are going to specialise 'choice', This 
# combinator is given a set of parsers to try in order; If a parser fails, it backtracks and tries
# the next, until one succeeds. If none succeed, then the choice fails. 
char_spec_range_char = partial(choice, char_spec_hex, any_token)

# The second part of the character spec is a range. This is more complex that previous parsers
# and we are using a def for it. This parser takes advantage of the previous definition of 
# the char_spec_range_char to find either literal characters or hexdecimal codepoints.
# It returns a new parser specialising 'satisfies'. satisfies takes a function that is called 
# against the input. In this case we are creating a parser that checks that a character is within
# the given range
def char_spec_range():
    one_of("[")
    low = char_spec_range_char()
    one_of('-')
    high = char_spec_range_char()
    one_of("]")
    return partial(satisfies, lambda c: low <= c <= high)

char_spec_seperator = partial(lexeme, partial(one_of, '|'))

# This is the top level parser for the chararacter spec. sep1 is a combinator that finds something
# seperated by something else. In this case it finds one of a range, a single character or a hex 
# character, and the seperator is a '|'. sep and sep1 return a list.
#
# Secondly, note the 'eof()' here. This parser is checking that we have reached the end of the input
#
# The last thing to be aware of is that each of the choices _returns a list of parsers_
def xml_char_spec_parser():
    v = sep1(partial(choice, char_spec_range, char_spec_single_char, char_spec_single_hex_char),
             char_spec_seperator)
    eof()
    return v

# We cant call parsers from outside of a 'run_parser' call. run_parser evaluates the parser function
# you provide over the input you provide, returning the result, and the remainder. Remember that 
# xml_char_spec_parser returns a list of parsers. This function wraps those parses up in a choice.
# This choice parser will accept a single character if it falls within the spec. 
def xml_char_spec(spec, extra_choices=[]):
    parsers, remainder = run_parser(xml_char_spec_parser, spec.strip())
    return partial(choice, *(extra_choices + parsers))

# Finally, we run the xml_char_spec function over the character sets to get two new parsers
# to accept the valid characters for names of elements and attributes. 
name_start_char = xml_char_spec('":" | [A-Z] | "_" | [a-z] | [#xC0-#xD6] | [#xD8-#xF6] | [#xF8-#x2FF] | [#x370-#x37D] | [#x37F-#x1FFF] | [#x200C-#x200D] | [#x2070-#x218F] | [#x2C00-#x2FEF] | [#x3001-#xD7FF] | [#xF900-#xFDCF] | [#xFDF0-#xFFFD] | [#x10000-#xEFFFF]')
name_char = xml_char_spec('"-" | "." | [0-9] | #xB7 | [#x0300-#x036F] | [#x203F-#x2040]', [name_start_char])

# We return to the parser for XML now, rather than the grammer for xml characers.

# Now that we have those two primatives, we can build a parser that accepts an xml name.
# You can see that a name has one name_start_char, followed by zero or more name_chars
def xml_name():
    return build_string([name_start_char()] + many(name_char))

# Next we define the processing of an entity and then an xml_char, which are used later in node
# definitions. A more sophisticated parser would let additional entities be regestered with 
# directives
named_entities = {
    'amp':'&',
    'quot':'"',
    'apos':"'",
    'lt':'<',
    'gt':'>',
}

# entity is the toplevel parser for &...; notation, it chooses which sub parser to use
def entity():
    one_of('&')
    ent = choice(named_entity, numeric_entity)
    one_of(';')
    return ent

def named_entity():
    name = build_string(many1(partial(not_one_of,';#')))
    if name not in named_entities: fail()
    return named_entities[name]

def hex_entity():
    one_of('x')
    return unichr(hex_value())

def dec_entity():
    return unichr(int(build_string(many1(decimal_digit)), 10))

def numeric_entity():
    one_of('#')
    return choice(hex_entity, dec_entity)

# finally, xml_char is created by partially apply choice to either, normal characters or entities
xml_char = partial(choice, partial(not_one_of, '<>&'), entity)
    
# now we are ready to start implementing the main document parsers.
# xml is our entrypoint parser. The XML spec requires a specific (but optional) prolog
# before the root element node, of which there may only be one. Note that once again
# we are checking reach the end of input.
def xml():
    prolog()
    n = lexeme(element)
    eof()
    return n

def prolog():
    whitespace()
    optional(tri(partial(processing, xmldecl)), None)
    many(partial(choice, processing, comment, whitespace1))
    optional(doctype, None)    
    many(partial(choice, processing, comment, whitespace1))

# The xml declaration could be parsed with a specialised processing directive, or it can be
# handled as a special case. We are going to handle it as a specialisation of the processing.
# our processing directive can optionally be given a parser to provide more detailed handling
# or it will just consume the body 
@tri
def processing(parser = False):
    parser = parser if parser else compose(build_string, partial(many, partial(not_one_of, '?')))

    string('<?')
    commit()
    result = parser()
    whitespace()
    
    string('?>')
    return result

def xmldecl():
    caseless_string('xml')
    whitespace()
    return ('xml', optional(partial(xmldecl_attr, 'version', version_num), "1.0"), 
                   optional(partial(xmldecl_attr, 'standalone', standalone), "yes"))
    
def xmldecl_attr(name, parser):
    string(name)
    lexeme(equals)
    value = quoted(version_num)
    return value

def version_num():
    string('1.')
    return "1." + build_string(many1(decimal_digit))
    
def standalone():
    return choice(partial(string, 'yes'), partial(string, 'no'))

@tri
def comment():
    string("<!--")
    commit()
    result, _ = many_until(any_token, tri(partial(string, "-->")))
    return "COMMENT", build_string(result)

# Node is the general purpose node parser. it wil choose the first parser
# from the set provided that matches the input
def node():
    return choice(processing, element, text_node, comment)

def text_node():
    return "TEXT", build_string(many1(xml_char))

@tri
def doctype():
    string('<!DOCTYPE')
    commit()
    many_until(any_token, close_angle)

@tri
def element():
    open_angle()
    name = xml_name()
    commit()
    attributes = lexeme(partial(sep, attribute, whitespace1))
    return "NODE", name, attributes, choice(closed_element, partial(open_element, name))

def closed_element():
    string('/>')
    return []

def open_element(name):
    close_angle()
    children = many(node)
    end_element(name)
    return children

@tri
def end_element(name):
    whitespace()
    string("</")
    commit()
    if name != xml_name():
        fail()
    whitespace()
    close_angle()

@tri
def attribute():
    name = xml_name()
    commit()
    lexeme(equals)
    return "ATTR", name, quoted()

parse_xml = partial(run_parser, xml)

tokens, remaining = parse_xml("""
<?xml version="1.0" ?>
<!DOCTYPE MyDoctype>

<!-- a comment -->
<root>
    <!-- another comment -->
    <self-closing />
    <? this processing is ignored ?>
    <node foo="bar" baz="bo&amp;p'">
        This is some node text &amp; it contains a named entity &#65;nd some &#x41; numeric
    </node>
</root>
""")

print "nodes:", tokens
print
print "remaining:", build_string(remaining)

