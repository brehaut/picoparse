from functools import partial as p
from picoparse import run_parser

def run(parser, input):
    tokens, remaining = run_parser(parser, input)
    return tokens

def runp(parser, input):
    """returns a callable to run the parser with the input provided"""
    return p(run, parser, input)