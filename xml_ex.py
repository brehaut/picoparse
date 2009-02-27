"""This is a simple _example_ of using picoparse. It implements a small, incomplete XML parser
"""

from picoparse import BufferWalker, scan_char, scan_nchar, scan_until, scan_while, choice
from functools import partial

def compose(f, g):
    return lambda *args, **kwargs: f(g(*args, **kwargs))

def build_string(iterable):
    return u''.join(iterable)

def parse_xml(input):
    buf = BufferWalker(input)
    result = parser(buf)

    node(buf)

open_angle = partial(scan_char, '<')
close_angle = partial(scan_char, '<')
slash = partial(scan_char, '/')
element_text = compose(build_string, partial(scan_until, ' \t\r\n<>/='))


def node(items):
    open_angle(items)
    name = element_text()