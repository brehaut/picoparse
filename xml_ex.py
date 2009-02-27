"""This is a simple _example_ of using picoparse. It implements a small, incomplete XML parser
"""

from picoparse import BufferWalker, scan_char, scan_nchar, scan_until, scan_while, choice
from picoparse import scan_whitespace, many
from functools import partial

def compose(f, g):
    return lambda *args, **kwargs: f(g(*args, **kwargs))

def build_string(iterable):
    return u''.join(iterable)

def parse_xml(input):
    buf = BufferWalker(input)
    result = node(buf)
    print result

open_angle = partial(scan_char, '<')
close_angle = partial(scan_char, '>')
slash = partial(scan_char, '/')
equals = partial(scan_char, '=')
element_text = compose(build_string, partial(scan_until, ' \t\r\n<>/='))

def node(items):
    scan_whitespace(items)
    open_angle(items)
    name = element_text(items)
    attributes = many(items, attribute)
#    attributes = [attribute(items)]
    print attributes
    close_angle(items)
    children = many(items, node)
    return "NODE", name, attributes, children

def attribute(items):
    scan_whitespace(items)
    name = element_text(items)
    scan_whitespace(items)
    equals(items)
    scan_whitespace(items)
    quote = scan_char("\"'", items)
    value = build_string(scan_until(quote, items))
    scan_char(quote, items)
    return "ATTR", name, value
    
    
parse_xml("""
<xml version="1.0"><node  foo="bar" baz="bop"></node></xml>
""")