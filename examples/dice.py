#!/usr/bin/env python
"""A simple dice-expression parser."""
from functools import partial
from picoparse.text import build_string, whitespace
from picoparse import one_of, many, many1, not_one_of, run_parser, tri, commit, optional, fail
from picoparse import choice, string, peek, cut, string, eof, many_until, any_token, satisfies
from picoparse import sep, sep1, compose, cue

import sys

decimal_digit = partial(one_of, '0123456789')

number = compose(int, build_string)

def dice_exp():
    multiplier = number(many1(decimal_digit))
    one_of("dD")
    sides = number(many(decimal_digit)) or 6
    return multiplier, "D", sides

parse_exp = partial(run_parser, dice_exp)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        EXP = sys.argv[1]
    else:
        EXP = "2D6+3"
    
    print parse_exp(EXP)
