#!/usr/bin/env python
"""A simple dice-expression parser."""
# Copyright (c) 2009, Matt Wilson
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
from picoparse.text import build_string, whitespace
from picoparse import one_of, many, many1, not_one_of, run_parser, tri, commit, optional, fail
from picoparse import choice, string, peek, string, eof, many_until, any_token, satisfies
from picoparse import sep, sep1, compose, cue

import sys
from random import randint

OPERATORS = {
    '+': 'OP_ADD',
    '-': 'OP_SUB',
    '*': 'OP_MUL',
    '/': 'OP_DIV',
}

CODES = {
    'OP_ADD': lambda x,y: x+y,
    'OP_SUB': lambda x,y: x-y,
    'OP_MUL': lambda x,y: x*y,
    'OP_DIV': lambda x,y: x/y,
    'OP_DICE': lambda x: sum(randint(1, x['SIDES']) for i in x['ROLLS']),
    # 'OP_NUM': int,
}

decimal_digit = partial(one_of, '0123456789')

make_number = compose(int, build_string)

def number():
    whitespace()
    digits = many1(decimal_digit)
    whitespace()
    return make_number(digits)

def operator():
    whitespace()
    op = one_of("+-/*")
    whitespace()
    return OPERATORS[op]

@tri
def dice_expression():
    whitespace()
    dice = number()
    one_of("dD")
    commit()
    sides = number() or 6
    whitespace()
    return ('OP_DICE', {'ROLLS': dice, 'SIDES': sides})

def separator():
    whitespace()
    one_of(',')
    whitespace()

def parenthesised_expression():
    whitespace()
    one_of('(')
    whitespace()
    e = expression()
    whitespace()
    one_of(')')
    whitespace()
    return e

token = partial(choice, dice_expression, number, operator, parenthesised_expression)

expression = partial(many1, token)

def expressions():
    return sep(partial(choice, parenthesised_expression, expression), separator)

parse_exp = partial(run_parser, expressions)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        EXP = sys.argv[1]
    else:
        EXP = "2D6+3"
    
    print parse_exp(EXP)
