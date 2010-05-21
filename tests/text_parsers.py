#!/usr/bin/env python
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

if __name__ == '__main__':
    import sys
    from os import path
    sys.path.insert(0, path.abspath(path.join(path.dirname(sys.argv[0]), '..')))

import unittest

import core_parsers
import string
from picoparse import partial as p
from picoparse.text import newline, whitespace_char, whitespace, whitespace1
from picoparse.text import lexeme, quote, quoted, caseless_string, run_text_parser

from utils import TextParserTestCase

class TestTextTokenConsumers(core_parsers.TestTokenConsumers):
    def run_parser(self, *args):
		return run_text_parser(*args)
		
class TestTextManyCombinators(core_parsers.TestManyCombinators):
    def run_parser(self, *args):
		return run_text_parser(*args)

class TestTextSeparatorCombinators(core_parsers.TestSeparatorCombinators):
    def run_parser(self, *args):
		return run_text_parser(*args)

class TestTextSequencingCombinators(core_parsers.TestSequencingCombinators):
    def run_parser(self, *args):
		return run_text_parser(*args)

class TestTextFuture(core_parsers.TestFuture):
    def run_parser(self, *args):
		return run_text_parser(*args)

whitespace_strings = [' ', '  ', '   ', '\n', '\t', '\n \n\r\t\n \t']

class TestWhitespaceParsers(TextParserTestCase):
    def testnewline(self):
        self.assertNoMatch(newline, '')
        self.assertMatch(newline, '\n', '\n', [])
        self.assertMatch(newline, '\n\n', '\n', '\n')
        self.assertNoMatch(newline, '\r\n')
        self.assertNoMatch(newline, '\r')

    def testwhitespace_char(self):
        self.assertNoMatch(whitespace_char, '')
        for ch in string.whitespace:
            self.assertMatch(whitespace_char, ch, ch, '')
            self.assertMatch(whitespace_char, ch + ' ', ch, ' ')
            self.assertMatch(whitespace_char, ch + 'a', ch, 'a')
        self.assertNoMatch(whitespace_char, 'a')

    def testwhitespace(self):
        self.assertMatch(whitespace, 'a', '', 'a')
        for ws in whitespace_strings:
            self.assertMatch(whitespace, ws, ws, '')
            self.assertMatch(whitespace, ws + 'a', ws, 'a')

    def testwhitespace1(self):
        self.assertNoMatch(whitespace1, '')
        self.assertNoMatch(whitespace1, 'a')
        for ws in whitespace_strings:
            self.assertMatch(whitespace1, ws, ws, '')
            self.assertMatch(whitespace1, ws + 'a', ws, 'a')

class TestSimpleParsers(TextParserTestCase):
    def testquote(self):
        self.assertMatch(quote, "'", "'", '')
        self.assertMatch(quote, '"', '"', '')
        self.assertMatch(quote, "'a", "'", 'a')
        self.assertMatch(quote, '"a', '"', 'a')
        self.assertNoMatch(quote, '')
    
    def testdigit(self):
        raise Exception('not implemented')
    
    def testdigits(self):
        raise Exception('not implemented')
        
    def testnumber(self):
        raise Exception('not implemented')
    
    def testfloating(self):
        raise Exception('not implemented')
    
    def testalpha(self):
        raise Exception('not implemented')
    
    def testword(self):
        raise Exception('not implemented')

    def testbuild_string(self):
        raise Exception('not implemented')

    def testas_string(self):
        raise Exception('not implemented')

    def testcaseless_string(self):
        raise Exception('not implemented')

class TestLiterals(TextParserTestCase):
    def make_literal(self):
        raise Exception('not implemented')

    def literal(self):
        raise Exception('not implemented')

    def make_caseless_literal(self):
        raise Exception('not implemented')

    def caseless_literal(self):
        raise Exception('not implemented')

class TestWrappers:
    def testparened(self):
        parened_lit = partial(parened, make_literal('lit'))
        self.testwrapper(parened_lit, "(", "lit", ")")

    def testbraced(self):
        braced_lit = partial(braced, make_literal('lit'))
        self.testwrapper(bracketed_lit, "[", "lit", "]")
        
    def testbraced(self):
        braced_lit = partial(braced, make_literal('lit'))
        self.testwrapper(bracketed_lit, "{", "lit", "}")

    def testquoted(self):
        quoted_quote = partial(quoted, quote)
        self.testwrapper(quoted, "'", 'thing', "'")
        self.testwrapper(quoted, '"', 'thing', '"')
        self.testwrapper(quoted_quote, "'", '"', "'")
        self.testwrapper(quoted_quote, '"', "'", '"')       
        self.assertNoMatch(quoted, '"thing\'')
        self.assertNoMatch(quoted, '\'thing"')
        self.assertNoMatch(quoted_quote, "\"''")
        self.assertNoMatch(quoted_quote, '\'""')

    def testlexeme(self):
        lex_lit = partial(lexeme, make_literal('lit'))
        lex_number = partial(lexeme, digits)
        self.assertMatch(lex_number, '0', '0', '')
        self.assertMatch(lex_number, '0', '0 ', 'a')
        self.assertMatch(lex_lit, 'lit', 'lit', '')
        self.assertMatch(lex_lit, 'lit', 'lit a', 'a')
        for ws1 in whitespace_strings:
            self.assertMatch(lex_lit, ws1 + 'lit', 'lit', '')
            self.assertMatch(lex_number, '1234' + ws1, 1234, '')
            self.assertMatch(lex_number, '1234' + ws1 + 'a', 1234, 'a')
            for ws2 in whitespace_strings:
                self.assertMatch(lex_lit, ws1 + 'lit' + ws2, 'lit', '')
                self.assertMatch(lex_number, ws1 + '1234' + ws2, 1234, '')
                self.assertMatch(lex_number, ws1 + '1234' + ws2 + 'a', 1234, 'a')

        self.assertNoMatch(lex_number, '')
        self.assertNoMatch(lex_lit, '')
        
    def testwrapper(self, parser, before, middle, after):
        self.assertMatch(parser, before + middle + after, middle, '')
        self.assertNoMatch(parser, '')
        self.assertNoMatch(parser, middle)
        self.assertNoMatch(parser, before + middle)
        self.assertNoMatch(parser, middle + after)
        self.assertNoMatch(parser, before + after)


if __name__ == '__main__':
    unittest.main()

__all__ = [cls.__name__ for name, cls in locals().items()
                        if isinstance(cls, type) 
                        and name.startswith('Test')]
