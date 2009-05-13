#!/usr/bin/env python
"""A simple paren-expression parser."""
# Copyright (c) 2009, Steven Ashley
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

from picoparse import partial
from picoparse import one_of, optional, many, choice, p, cue
from picoparse.text import run_text_parser, whitespace
import sys


def bracketed():
    one_of('[')
    v = expression()
    one_of(']')
    return ['bracket', v]

def braced():
    one_of('{')
    v = expression()
    one_of('}')
    return ['brace', v]

def parened():
    one_of('(')
    v = expression()
    one_of(')')
    return ['paren', v]

part = p(choice, bracketed, braced, parened)
expression = p('expression', many, part)

if __name__ == "__main__":
    text = ''
    if len(sys.argv) > 1:
        text = sys.argv[1]
    print run_text_parser(p(cue, whitespace, part), text)

