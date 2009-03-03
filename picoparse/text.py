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

from picoparse import string, one_of, many, many1, many_until, any_token, run_parser
from functools import partial

quote = partial(one_of, "\"'")
whitespace_char = partial(one_of, ' \t\n\r')
whitespace = partial(many, whitespace_char)
whitespace1 = partial(many1, whitespace_char)
newline = partial(one_of, '\n')

def build_string(iterable):
    """A utility function to wrap up the converting a list of characters back into a string.
    """
    return u''.join(iterable)
    
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


class TextDiagnostics(object):
    def __init__(self):
        self.lines = []
        self.row = 1
        self.col = 1
        self._line = []
        self.offset = 1
    
    def error_text(self, location, error):
        pass
    
    def cut(self, (row, col)):
        to_cut = (row - 1) - self.offset 
        self.offset += to_cut
        self.lines = self.lines[to_cut:]
    
    def wrap(self, stream):
        try:
            while True:
                t = stream.next()
                if t == '\r' or t == '\n':
                    for r in self._emit_line():
                        yield r
                    if t == '\r':
                        t2 = stream.next()
                        if t2 != '\n':
                            self._line.append(t2)
                else:
                    self._line.append(t)
        except StopIteration:
            for r in self._emit_line():
                yield r
    
    def _emit_line(self):
        line_str = u''.join(self._line)
        self.lines.append(line_str)
        for token in self._line:
            yield (token, (self.row, self.col))
            self.col += 1
        yield ('\n', (self.row, self.col))
        self.col = 1
        self.row += 1
        self._line = []


def run_text_parser(parser, input):
    return run_parser(parser, input, TextStreamWrapper().wrap)
