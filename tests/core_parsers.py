import unittest

from functools import partial as p
from picoparse import run_parser, NoMatch
from picoparse import one_of, not_one_of

def run(parser, input):
    tokens, remaining = run_parser(parser, input)
    return tokens

def runp(parser, input):
    """returns a callable to run the parser with the input provided"""
    return p(run, parser, input)

# some simple parsers
one_a = p(one_of, 'a')
not_a = p(not_one_of, 'a')
one_a_or_b = p(one_of, 'ab')
not_a_or_b = p(not_one_of, 'ab')
    
class TestTokenConsumers(unittest.TestCase):
    def testone_of(self):
        # matches
        self.assertEquals(run(one_a, 'a'), 'a')
        self.assertEquals(run(one_a_or_b, 'a'), 'a')
        self.assertEquals(run(one_a_or_b, 'b'), 'b')
        # no match
        self.assertRaises(NoMatch, runp(one_a, 'b'))
        self.assertRaises(NoMatch, runp(one_a_or_b, 'c'))

    def testnot_one_of(self):
        # matches
        self.assertEquals(run(not_a, 'b'), 'b')
        self.assertEquals(run(not_a_or_b, 'c'), 'c')
        # no match
        self.assertRaises(NoMatch, runp(not_a, 'a'))
        self.assertRaises(NoMatch, runp(not_a_or_b, 'a'))
        self.assertRaises(NoMatch, runp(not_a_or_b, 'b'))

if __name__ == '__main__':
    unittest.main()