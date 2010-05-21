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

from picoparse import partial as p
from picoparse import run_parser as run, NoMatch
from picoparse import any_token, one_of, not_one_of, satisfies, eof
from picoparse import many, many1, many_until, many_until1, n_of, optional
from picoparse import sep, sep1
from picoparse import cue, follow, seq, string
from picoparse import not_followed_by, remaining

from utils import ParserTestCase

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

class TestTokenConsumers(ParserTestCase):
    """This TestCase checks that all the primative token consumers work as expected.
    """
    def testany_token(self):
        self.assertMatch(any_token, 'a', 'a', '')
        self.assertMatch(any_token, 'b', 'b', '')
        self.assertMatch(any_token, 'ab', 'a', 'b')
                
        self.assertNoMatch(any_token, '')
    
    def testone_of(self):
        # matches
        self.assertMatch(one_a, 'a', 'a', '')
        self.assertMatch(one_a_or_b, 'a', 'a', '')
        self.assertMatch(one_a_or_b, 'b', 'b', '')
        self.assertMatch(one_a, 'ac', 'a', 'c')
        self.assertMatch(one_a_or_b, 'ac', 'a', 'c')
        self.assertMatch(one_a_or_b, 'bc', 'b', 'c')
        
        # no match
        self.assertNoMatch(one_a, 'b')
        self.assertNoMatch(one_a_or_b, 'c')
        self.assertNoMatch(one_a, '')
        self.assertNoMatch(one_a_or_b, '')
        self.assertNoMatch(nothing, 'a')
        
    def testnot_one_of(self):
        # matches
        self.assertMatch(not_a, 'b', 'b', '')
        self.assertMatch(not_a_or_b, 'c', 'c', '')
        self.assertMatch(everything, 'a', 'a', '')
        self.assertMatch(everything, 'b', 'b', '')
        self.assertMatch(everything, 'ab', 'a', 'b')
        
        # no match
        self.assertNoMatch(not_a, '')
        self.assertNoMatch(not_a, 'a')
        self.assertNoMatch(not_a_or_b, '')
        self.assertNoMatch(not_a_or_b, 'a')
        self.assertNoMatch(not_a_or_b, 'b')
    
    def testsatisfies(self):
        self.assertMatch(always_satisfies, 'a', 'a', '')
        self.assertMatch(always_satisfies, 'b', 'b', '')
        self.assertNoMatch(always_satisfies, '')

        self.assertNoMatch(never_satisfies, 'a')
        self.assertNoMatch(never_satisfies, 'b')
        self.assertNoMatch(never_satisfies, '')

        self.assertMatch(one_b_to_d, 'b', 'b', '')
        self.assertMatch(one_b_to_d, 'c', 'c', '')
        self.assertMatch(one_b_to_d, 'd', 'd', '')
        self.assertMatch(one_b_to_d, 'bc', 'b', 'c')
        self.assertNoMatch(one_b_to_d, '')
        self.assertNoMatch(one_b_to_d, 'a')
        self.assertNoMatch(one_b_to_d, 'e')

    def testeof(self):
        self.assertMatch(eof, '', None, [])
        self.assertNoMatch(eof, 'a')
        

many_as = p(many, one_a)
at_least_one_a = p(many1, one_a)
one_b = p(one_of, 'b')
some_as_then_b = p(many_until, one_a, one_b)
at_least_one_a_then_b = p(many_until1, one_a, one_b)
three_as = p(n_of, one_a, 3)
zero_or_one_a = p(optional, one_a, None)


class TestManyCombinators(ParserTestCase):
    """Tests the simple many* parser combinators.
    """
    
    def testmany(self):
        self.assertMatch(many_as, '', [], '')
        self.assertMatch(many_as, 'a', ['a'], '')
        self.assertMatch(many_as, 'aa', ['a','a'], '')
        self.assertMatch(many_as, 'aaa', ['a','a', 'a'], '')
    
        self.assertMatch(many_as, 'b', [], 'b')
        self.assertMatch(many_as, 'ab', ['a'], 'b')
        self.assertMatch(many_as, 'aab', ['a','a'], 'b')
        self.assertMatch(many_as, 'aaab', ['a','a','a'], 'b')

    def testmany1(self):
        self.assertNoMatch(at_least_one_a, '')
        self.assertMatch(at_least_one_a, 'a', ['a'], '')
        self.assertMatch(at_least_one_a, 'aa', ['a','a'], '')
        self.assertMatch(at_least_one_a, 'aaa', ['a','a','a'], '')

        self.assertNoMatch(at_least_one_a, 'b')
        self.assertMatch(at_least_one_a, 'ab', ['a'], 'b')
        self.assertMatch(at_least_one_a, 'aab', ['a','a'], 'b')
        self.assertMatch(at_least_one_a, 'aaab', ['a','a','a'], 'b')
    
    def testmany_until(self):
        self.assertMatch(some_as_then_b, 'b', ([], 'b'), '')
        self.assertMatch(some_as_then_b, 'ab', (['a'], 'b'), '')
        self.assertMatch(some_as_then_b, 'aab', (['a','a'], 'b'), '')
        self.assertMatch(some_as_then_b, 'aaab', (['a','a','a'], 'b'), '')
        
        self.assertNoMatch(some_as_then_b, '')
        self.assertNoMatch(some_as_then_b, 'a')
        self.assertNoMatch(some_as_then_b, 'aa')
        
    def testmany_until1(self):
        self.assertNoMatch(at_least_one_a_then_b, 'b')
        self.assertMatch(at_least_one_a_then_b, 'ab', (['a'], 'b'), '')
        self.assertMatch(at_least_one_a_then_b, 'aab', (['a','a'], 'b'), '')
        self.assertMatch(at_least_one_a_then_b, 'aaab', (['a','a','a'], 'b'), '')

        self.assertNoMatch(at_least_one_a_then_b, '')
        self.assertNoMatch(at_least_one_a_then_b, 'a')
        self.assertNoMatch(at_least_one_a_then_b, 'aa')
    
    def testn_of(self):
        self.assertNoMatch(three_as, '')
        self.assertNoMatch(three_as, 'a')
        self.assertNoMatch(three_as, 'aa')
        self.assertMatch(three_as, 'aaa', ['a','a','a'], '')
        self.assertMatch(three_as, 'aaaa', ['a', 'a', 'a'], 'a')
        
        self.assertNoMatch(three_as, 'b')        
        self.assertNoMatch(three_as, 'ab')
        self.assertNoMatch(three_as, 'aab')
    
    def testoptional(self):
        self.assertMatch(zero_or_one_a, '', None, '')
        self.assertMatch(zero_or_one_a, 'a', 'a', '')
        self.assertMatch(zero_or_one_a, 'aa', 'a', 'a')
        self.assertMatch(zero_or_one_a, 'b', None, 'b')


as_sep_by_b = p(sep, one_a, one_b)
one_or_more_as_sep_by_b = p(sep1, one_a, one_b)


class TestSeparatorCombinators(ParserTestCase):
    def testsep(self):
        self.assertMatch(as_sep_by_b, '', [], '')
        self.assertMatch(as_sep_by_b, 'a', ['a'], '')
        self.assertMatch(as_sep_by_b, 'ab', ['a'], 'b')
        self.assertMatch(as_sep_by_b, 'aba', ['a','a'], '')
        self.assertMatch(as_sep_by_b, 'abab', ['a', 'a'], 'b')
        self.assertMatch(as_sep_by_b, 'ababa', ['a','a','a'], '')
        self.assertMatch(as_sep_by_b, 'b', [], 'b')
        self.assertMatch(as_sep_by_b, 'ba', [], 'ba')
        self.assertMatch(as_sep_by_b, 'bab', [], 'bab')
        
    def testsep1(self):
        self.assertNoMatch(one_or_more_as_sep_by_b, '')
        self.assertMatch(one_or_more_as_sep_by_b, 'a', ['a'], '')
        self.assertMatch(one_or_more_as_sep_by_b, 'ab', ['a'], 'b')
        self.assertMatch(one_or_more_as_sep_by_b, 'aba', ['a','a'], '')
        self.assertMatch(one_or_more_as_sep_by_b, 'abab', ['a', 'a'], 'b')
        self.assertMatch(one_or_more_as_sep_by_b, 'ababa', ['a','a','a'], '')
        self.assertNoMatch(one_or_more_as_sep_by_b, 'b')
        self.assertNoMatch(one_or_more_as_sep_by_b, 'ba')
        self.assertNoMatch(one_or_more_as_sep_by_b, 'bab')


a_then_ret_b = p(cue, one_a, one_b)
ret_a_then_b = p(follow, one_a, one_b)
a_then_ab_then_b = p(seq, ('A', one_a), one_a, one_b, ('B', one_b))
abc = p(string, 'abc')
abc_caseless = p(string, ['aA','bB', 'cC'])


class TestSequencingCombinators(ParserTestCase):
    def testcue(self):
        self.assertMatch(a_then_ret_b, 'ab', 'b', [])
        self.assertNoMatch(a_then_ret_b, '')
        self.assertNoMatch(a_then_ret_b, 'a')
        self.assertNoMatch(a_then_ret_b, 'b')
        self.assertMatch(a_then_ret_b, 'aba', 'b', 'a')

    def testfollow(self):
        self.assertMatch(ret_a_then_b, 'ab', 'a', '')
        self.assertNoMatch(ret_a_then_b, '')
        self.assertNoMatch(ret_a_then_b, 'a')
        self.assertNoMatch(ret_a_then_b, 'b')
        self.assertMatch(ret_a_then_b, 'aba', 'a', 'a')

    def testseq(self):
        self.assertNoMatch(a_then_ab_then_b, '')
        self.assertNoMatch(a_then_ab_then_b, 'a')
        self.assertNoMatch(a_then_ab_then_b, 'ab')
        self.assertNoMatch(a_then_ab_then_b, 'aa')
        self.assertNoMatch(a_then_ab_then_b, 'aab')
        self.assertNoMatch(a_then_ab_then_b, 'aaa')
        self.assertNoMatch(a_then_ab_then_b, 'aaba')
        self.assertMatch(a_then_ab_then_b, 'aabb', {'A':'a', 'B':'b'}, '')
        self.assertMatch(a_then_ab_then_b, 'aabba', {'A':'a', 'B':'b'}, 'a')
    
    def teststring(self):
        self.assertMatch(abc, 'abc', ['a','b','c'], '')
        self.assertMatch(abc, 'abca', ['a','b','c'], 'a')
        self.assertNoMatch(abc, '')
        self.assertNoMatch(abc, 'a')
        self.assertNoMatch(abc, 'ab')        
        self.assertNoMatch(abc, 'aa')
        self.assertNoMatch(abc, 'aba')
        self.assertNoMatch(abc, 'abb')
    
        for triple in [(a, b, c) for a in 'aA' for b in 'bB' for c in 'cC']:
            s = u''.join(triple)
            l = list(triple)
            self.assertMatch(abc_caseless, s, l, '')
            s += 'a'
            self.assertMatch(abc_caseless, s, l, 'a')
        self.assertNoMatch(abc_caseless, '')
        

as_then_remaining = p(cue, many_as, remaining)
as_then_not_b = p(follow, many_as, p(not_followed_by, one_b))

        
class TestFuture(ParserTestCase):
    def testremaining(self):
        self.assertMatch(remaining, '', [], '')
        self.assertMatch(as_then_remaining, '', [], '')
        self.assertMatch(as_then_remaining, 'a', [], '')
        self.assertMatch(as_then_remaining, 'aa', [], '')
        self.assertMatch(as_then_remaining, 'b', ['b'], '')
        self.assertMatch(as_then_remaining, 'ab', ['b'], '')
        self.assertMatch(as_then_remaining, 'abb', ['b','b'], '')
        self.assertMatch(as_then_remaining, 'aabb', ['b','b'], '')

    def testnot_followed_By(self):
        self.assertMatch(as_then_not_b, '', [], '')
        self.assertMatch(as_then_not_b, 'a', ['a'], '')
        self.assertMatch(as_then_not_b, 'aa', ['a','a'], '')
        self.assertMatch(as_then_not_b, 'c', [], 'c')
        self.assertMatch(as_then_not_b, 'ac', ['a'], 'c')
        self.assertMatch(as_then_not_b, 'aac', ['a','a'], 'c')
                
        self.assertNoMatch(as_then_not_b, 'b')
        self.assertNoMatch(as_then_not_b, 'ab')
        self.assertNoMatch(as_then_not_b, 'aab')

                        
if __name__ == '__main__':
    unittest.main()

__all__ = [cls.__name__ for name, cls in locals().items()
                        if isinstance(cls, type) 
                        and name.startswith('Test')]
