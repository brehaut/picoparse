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

import unittest

import utils
import core_parsers

import picoparse
from picoparse.text import newline, whitespace_char, whitespace, whitespace1
from picoparse.text import lexeme, quote, quoted, caseless_string

from utils import TextParserTestCase

class TestTextTokenConsumers(core_parsers.TestTokenConsumers):
    def run_parser(self, *args):
		return picoparse.text.run_text_parser(*args)
		
class TestTextManyCombinators(core_parsers.TestManyCombinators):
    def run_parser(self, *args):
		return picoparse.text.run_text_parser(*args)

class TestTextSeparatorCombinators(core_parsers.TestSeparatorCombinators):
    def run_parser(self, *args):
		return picoparse.text.run_text_parser(*args)

class TestTextSequencingCombinators(core_parsers.TestSequencingCombinators):
    def run_parser(self, *args):
		return picoparse.text.run_text_parser(*args)

class TestTextFuture(core_parsers.TestFuture):
    def run_parser(self, *args):
		return picoparse.text.run_text_parser(*args)

class TestWhitespaceParsers(TextParserTestCase):
    def testnewline(self):
        self.assertMatch(newline, '\n', '\n', [])
    
"""
quote
whitespace_char
whitespace
whitespace1
newline
build_string
caseless_string
lexeme
quoted
TextDiagnostics
"""

if __name__ == '__main__':
    unittest.main()

__all__ = [cls.__name__ for name, cls in locals().items()
                        if isinstance(cls, type) 
                        and name.startswith('Test')]
