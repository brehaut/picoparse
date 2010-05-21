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

from picoparse import partial, NoMatch, run_parser
from picoparse.text import run_text_parser

class ParserTestCase(unittest.TestCase):
    """Allow test cases to specialize
    """
    def run_parser(self, parser, input):
        return run_parser(parser, input)

    """Handles a match
    """
    def assertMatch(self, parser, input, expected, remaining, *args):
        self.assertEquals(self.run_parser(parser, input), (expected, list(remaining)), *args)

    """Handles the common case that a parser doesnt match input.
    """
    def assertNoMatch(self, parser, input, *args):
        self.assertRaises(NoMatch, partial(self.run_parser, parser, input), *args)

class TextParserTestCase(ParserTestCase):
    """Allow test cases to specialize
    """
    def run_parser(self, parser, input):
        return run_text_parser(parser, input)
