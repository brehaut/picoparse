"""Text parsing utilities for picoparse.

These functions exist for convenience; they implement common ideas about text syntax
for instance the quote and quoted parsers assume quotes can be ' or "
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

from string import whitespace as _whitespace_chars

from picoparse import p as partial
from picoparse import string, one_of, many, many1, many_until, any_token, run_parser
from picoparse import NoMatch, fail, tri, EndOfFile, optional, compose

def build_string(iterable):
    """A utility function to wrap up the converting a list of characters back into a string.
    """
    return u''.join(iterable)

as_string = partial(compose, build_string)



quote = partial(one_of, "\"'")
whitespace_char = partial(one_of, _whitespace_chars)
whitespace = as_string(partial(many, whitespace_char))
whitespace1 = as_string(partial(many1, whitespace_char))
newline = partial(one_of, "\n")

def caseless_string(s):
    """Attempts to match input to the letters in the string, without regard for case.
    """
    return string(zip(s.lower(), s.upper()))

def lexeme(parser):
    """Ignores any whitespace surrounding parser.
    """
    whitespace()
    v = parser()
    whitespace()
    return v
    
def quoted(parser=any_token):
    """Parses as much as possible until it encounters a matching closing quote.
    
    By default matches any_token, but can be provided with a more specific parser if required.
    Returns a string
    """
    quote_char = quote()
    value, _ = many_until(parser, partial(one_of, quote_char))
    return build_string(value)

def make_literal(s):
    "returns a literal parser"
    return partial(s, tri(string), s)

def literal(s):
    "A literal string."
    return make_literal(s)()
 
def make_caseless_literal(s):
    "returns a literal string, case independant parser."
    return partial(s, tri(caseless_string), s)

def caseless_literal(s):
    "A literal string, case independant."
    return make_caseless_literal(s)()


class Pos(object):
    def __init__(self, row, col):
        self.row = row
        self.col = col
    
    def __str__(self):
        return str(self.row) + ":" + str(self.col)


class TextDiagnostics(object):
    def __init__(self):
        self.lines = []
        self.row = 1
        self.col = 1
        self.line = []

    def generate_error_message(self, noMatch):
        return noMatch.default_message \
               + "\n" + "\n".join(self.lines)

    def cut(self, p):
        if p == EndOfFile:
            self.lines = []
        else:
            # 1   |  num rows = 5
            # 2 | |
            # 3 | |_ cut (3 rows) (2 discarded from buffer)
            # 4 |                  2 = 3 - (5 - 4)
            # 5 |_ buffer (4 rows)
            buffer_rows = len(self.lines)
            num_rows = self.row - 1
            cut_rows = p.row - 1
            discard_rows = cut_rows - (num_rows - buffer_rows)
            self.lines = self.lines[discard_rows:]

    def wrap(self, stream):
        try:
            while True:
                ch = stream.next()
                self.line.append(ch)
                if ch == '\n':
                    for tok in self.emit_line():
                        yield tok
        except StopIteration:
            for tok in self.emit_line():
                yield tok

    def emit_line(self):
        self.lines.append(u''.join(self.line))
        for ch in self.line:
            yield (ch, Pos(self.row, self.col))
            self.col += 4 if ch == '\t' else 1
        self.row += 1
        self.col = 1
        self.line = []

def run_text_parser(parser, input):
    return run_parser(parser, input, TextDiagnostics())

