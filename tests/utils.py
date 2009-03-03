import unittest
from functools import partial as p
from picoparse import run_parser, NoMatch

def run(parser, input):
    tokens, remaining = run_parser(parser, input)
    return tokens

def runp(parser, input):
    """returns a callable to run the parser with the input provided"""
    return p(run, parser, input)
    
class ParserTestCase(unittest.TestCase):
    """Handles the common case that a parser doesnt match input.
    """
    def assertNoMatch(self, parser, input, *args):
        self.assertRaises(NoMatch, runp(parser, input), *args)