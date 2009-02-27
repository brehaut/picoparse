"""This is a simple _example_ of using picoparse. It implements a small, incomplete XML parser
"""

from picoparse import one_of, many, many1, not_one_of, run_parser, tri, commit, optional, fail
from picoparse import choice, string, peek
from functools import partial

named_entities = {
    'amp':'&',
    'quot':'"',
    'apos':"'",
    'lt':'<',
    'gt':'>',
}

def compose(f, g):
    return lambda *args, **kwargs: f(g(*args, **kwargs))

def build_string(iterable):
    return u''.join(iterable)

open_angle = partial(one_of, '<')
close_angle = partial(one_of, '>')
slash = partial(one_of, '/')
equals = partial(one_of, '=')
quote = partial(one_of, "\"'")
whitespace = partial(many, partial(one_of, ' \t\n\r'))
element_text = compose(build_string, partial(many1, partial(not_one_of, ' \t\r\n<>/=')))
decimal_digit = partial(one_of, '0123456789')
hex_decimal_digit = partial(one_of, '0123456789AaBbCcDdEeFf')

def xml():
    whitespace()
    optional(processing, None)
    whitespace()
    return node()

def entity():
    one_of('&')
    ent = choice(named_entity, numeric_entity)
    one_of(';')
    return ent

def named_entity():
    name = build_string(many1(partial(not_one_of,';')))
    if name not in named_entities: fail()
    return named_entities[name]

def hex_entity():
    one_of('x')
    return chr(int(build_string(many1(hex_decimal_digit)), 16))

def dec_entity():
    return chr(int(build_string(many1(hex_decimal_digit)), 10))
    
def numeric_entity():
    one_of('#')
    return choice(hex_entity, dec_entity)

xml_char = partial(choice, partial(not_one_of, '<>&'), entity)

def node():
    return choice(processing, element,  text_node)

def text_node():
    text = build_string(many1(xml_char))
    return "TEXT", text

@tri
def processing():
    whitespace()
    open_angle()
    one_of('?')
    many(partial(not_one_of, '?'))
    one_of('?')
    close_angle()

@tri
def element():
    whitespace()
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
    optional(partial(end_element, name), None)    
    return children

def end_element(name):
    whitespace()
    open_angle()
    slash()
    if name != element_text():
        fail()
    whitespace()
    close_angle()

@tri
def attribute():
    whitespace()
    name = many1(element_text)
    commit()
    whitespace()
    equals()
    whitespace()
    quote()
    value = build_string(many(partial(choice, entity, partial(not_one_of, "\"'"))))
    quote()
    return "ATTR", name, value

    

tokens, remaining = run_parser(xml, """
<? xml version="1.0" ?>
<root>
    <self-closing />
    <? this processing is ignored ?>
    <node foo="bar" baz="bo&amp;p">
        This is some node text &amp; it contains a named entity &#65;nd some &#x41; numeric
    </node>
</root>
""")

print "nodes:", tokens
print
print "remaining:", build_string(remaining)

