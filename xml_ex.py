"""This is a simple _example_ of using picoparse to parse XML - not for real use. 

This example looks at XML as it is a textual stucture that the majority are familiar with. 
Comments throughout the file explain what is going on
"""
# Copyright (c) 2008, Andrew Brehaut, Steven Ashley
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

from picoparse import one_of, many, many1, not_one_of, run_parser, tri, commit, optional, fail
from picoparse import choice, string, peek, cut, string, eof, many_until, any_token
from functools import partial

# some general functions to help build parsers; build string exists so we can compose it 
# with parser that return a series of characters or strings
def compose(f, g):
    return lambda *args, **kwargs: f(g(*args, **kwargs))

def build_string(iterable):
    return u''.join(iterable)

# We define common primative parsers by partial application. This is similar to the lexical 
# analysis stage of a more traditional parser tool
open_angle = partial(one_of, '<')
close_angle = partial(one_of, '>')
slash = partial(one_of, '/')
question = partial(one_of, '?')
equals = partial(one_of, '=')
quote = partial(one_of, "\"'")
whitespace_char = partial(one_of, ' \t\n\r')
whitespace = partial(many, whitespace_char)
whitespace1 = partial(many1, whitespace_char)
element_text = compose(build_string, partial(many1, partial(not_one_of, ' \t\r\n<>/=!')))
decimal_digit = partial(one_of, '0123456789')
hex_decimal_digit = partial(one_of, '0123456789AaBbCcDdEeFf')

# next we define the processing of an entity and then an xml_char, which are used later in node
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
    return chr(int(build_string(many1(hex_decimal_digit)), 16))
    
def dec_entity():
    return chr(int(build_string(many1(decimal_digit)), 10))

def numeric_entity():
    one_of('#')
    return choice(hex_entity, dec_entity)

# finally, xml_char is created by partially apply choice to either, normal characters or entities
xml_char = partial(choice, partial(not_one_of, '<>&'), entity)

# we want to be able to parse quoted strings, sometimes caring what the form of the content is
def quoted_parser(parser):
    quote_char = quote()
    value, _ = many_until(any_token, tri(partial(one_of, quote_char)))
    return build_string(value)
    
# now we are ready to start implementing the main document parsers.
# xml is our entrypoint parser. The XML spec requires a specific (but optional) prolog
# before the root element node, of which there may only be one
def xml():
    prolog()
    whitespace()
    n = element()
    whitespace()
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

    open_angle()
    one_of('?')
    commit()
    result = parser()
    whitespace()
    
    one_of('?')
    close_angle()
    return result

def xmldecl():
    string('xml')
    whitespace()
    return ('xml', 
            optional(partial(xmldecl_attr, 'version', version_num), "1.0"), 
            optional(partial(xmldecl_attr, 'standalone', standalone), "yes"))
    
def xmldecl_attr(name, parser):
    string(name)
    whitespace()
    equals()
    whitespace()
    value = quoted_parser(version_num)
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
    text = build_string(many1(xml_char))
    return "TEXT", text

@tri
def doctype():
    open_angle()
    one_of('!')
    commit()
    string('DOCTYPE')
    many(partial(not_one_of, '>'))
    close_angle()

@tri
def element():
    open_angle()
    name = element_text()
    commit()
    attributes = many(attribute)
    whitespace()
    return "NODE", name, attributes, choice(closed_element, partial(open_element, name))

def closed_element():
    slash()
    close_angle()
    return []

def open_element(name):
    close_angle()
    children = many(node)
    end_element(name)
    return children

@tri
def end_element(name):
    whitespace()
    open_angle()
    slash()
    commit()
    if name != element_text():
        fail()
    whitespace()
    close_angle()

@tri
def attribute():
    whitespace()
    name = element_text()
    commit()
    whitespace()
    equals()
    whitespace()
    return "ATTR", name, quoted_parser(compose(build_string, partial(many, partial(choice, entity, partial(not_one_of, "\"'")))))

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

# tokens, remaining = run_parser(xml, file('/Users/andrew/Music/iTunes/iTunes Music Library.xml').read())

print "nodes:", tokens
print
print "remaining:", build_string(remaining)

