import unittest

from functools import partial as p
from picoparse import run_parser, NoMatch
from picoparse import any_token, one_of, not_one_of, satisfies

def run(parser, input):
    tokens, remaining = run_parser(parser, input)
    return tokens

def runp(parser, input):
    """returns a callable to run the parser with the input provided"""
    return p(run, parser, input)

# some simple parsers
nothing = p(one_of, '')
everything= p(not_one_of, '')
one_a = p(one_of, 'a')
not_a = p(not_one_of, 'a')
one_a_or_b = p(one_of, 'ab')
not_a_or_b = p(not_one_of, 'ab')

always_satisfies = p(satisfies, lambda i: True)
never_satisfies = p(satisfies, lambda i: False)
one_b_to_d = p(satisfies, lambda i: 'b' <= i <= 'd')

class TestTokenConsumers(unittest.TestCase):
    """This TestCase checks that all the primative token consumers work as expected.
    """
    def testany_token(self):
        self.assertEquals(run(any_token, 'a'), 'a')
        self.assertEquals(run(any_token, 'b'), 'b')
        self.assertEquals(run(any_token, 'ab'), 'a')
                
        self.assertRaises(NoMatch, runp(any_token, ''))
    
    def testone_of(self):
        # matches
        self.assertEquals(run(one_a, 'a'), 'a')
        self.assertEquals(run(one_a_or_b, 'a'), 'a')
        self.assertEquals(run(one_a_or_b, 'b'), 'b')
        self.assertEquals(run(one_a, 'ac'), 'a')
        self.assertEquals(run(one_a_or_b, 'ac'), 'a')
        self.assertEquals(run(one_a_or_b, 'bc'), 'b')
        
        # no match
        self.assertRaises(NoMatch, runp(one_a, 'b'))
        self.assertRaises(NoMatch, runp(one_a_or_b, 'c'))
        self.assertRaises(NoMatch, runp(one_a, ''))
        self.assertRaises(NoMatch, runp(one_a_or_b, ''))
        self.assertRaises(NoMatch, runp(nothing, 'a'))
        
    def testnot_one_of(self):
        # matches
        self.assertEquals(run(not_a, 'b'), 'b')
        self.assertEquals(run(not_a_or_b, 'c'), 'c')
        self.assertEquals(run(everything, 'a'), 'a')
        self.assertEquals(run(everything, 'b'), 'b')
        self.assertEquals(run(everything, 'ab'), 'a')
        
        # no match
        self.assertRaises(NoMatch, runp(not_a, 'a'))
        self.assertRaises(NoMatch, runp(not_a_or_b, 'a'))
        self.assertRaises(NoMatch, runp(not_a_or_b, 'b'))
    
    def testsatisfies(self):
        self.assertEquals(run(always_satisfies, 'a'), 'a')
        self.assertEquals(run(always_satisfies, 'b'), 'b')
        self.assertRaises(NoMatch, runp(always_satisfies, ''))

        self.assertRaises(NoMatch, runp(never_satisfies, 'a'))
        self.assertRaises(NoMatch, runp(never_satisfies, 'b'))
        self.assertRaises(NoMatch, runp(never_satisfies, ''))

        self.assertEquals(run(one_b_to_d, 'b'), 'b')
        self.assertEquals(run(one_b_to_d, 'c'), 'c')
        self.assertEquals(run(one_b_to_d, 'd'), 'd')
        self.assertEquals(run(one_b_to_d, 'bc'), 'b')
        self.assertRaises(NoMatch, runp(one_b_to_d, ''))
        self.assertRaises(NoMatch, runp(one_b_to_d, 'a'))
        self.assertRaises(NoMatch, runp(one_b_to_d, 'e'))



if __name__ == '__main__':
    unittest.main()

__all__ = ['TestTokenConsumers', ]