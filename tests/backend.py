import unittest

from picoparse import NoMatch, DefaultDiagnostics, BufferWalker
from functools import partial as p
from itertools import count, izip

class TestDefaultDiagnostics(unittest.TestCase):
    """Checks some basic operations on the DefaultDiagnostics class
    Eventually this will report errors. For now, there isn't much to test.
    """
    def setUp(self):
        self.diag = DefaultDiagnostics()
        self.i = self.diag.wrap(xrange(1, 6))

    def test_wrap(self):
        for ((a, b), c) in izip(self.i, xrange(1, 6)):
             self.assertEquals(a, c)
             self.assertEquals(b, c)
    
    def test_wrap_len(self):
        self.assertEquals(len(list(self.i)), 5)
    
    def test_tokens(self):
        self.assertEquals(self.diag.tokens, [])
        for (a, b) in self.i:
             self.assertEquals(self.diag.tokens, zip(range(1, a+1),range(1, a+1)))
    
    def test_cut(self):
        self.i.next()
        self.i.next()
        c, p = self.i.next()
        self.diag.cut(p)
        self.assertEquals(self.diag.tokens, [(3,3)])


class TestBufferWalker(unittest.TestCase):
    """Checks all backend parser operations work as expected
    """
    def setUp(self):
        self.input = "abcdefghi"
        self.bw = BufferWalker(self.input, None)

    def test_next(self):
        for c in self.input[1:]:
            self.assertEquals(self.bw.next(), c)
    
    def test_peek(self):
        for c in self.input:
            self.assertEquals(self.bw.peek(), c)
            self.bw.next()
    
    def test_current(self):
        for c, pos in izip(self.input, count(1)):
            self.assertEquals(self.bw.current(), (c, pos))
            self.bw.next()
    
    def test_pos(self):
        for c, pos in izip(self.input, count(1)):
            self.assertEquals(self.bw.pos(), pos)
            self.bw.next()
    
    def test_fail(self):
        self.assertRaises(NoMatch, self.bw.fail)
        self.assertEquals(self.bw.peek(), 'a')
    
    def test_tri_accept(self):
        self.bw.tri(self.bw.next)
        self.assertEquals(self.bw.peek(), 'b')
    
    def test_tri_fail(self):
        def fun():
            self.bw.next()
            self.bw.fail()
        self.assertRaises(NoMatch, p(self.bw.tri, fun))

    def test_commit_multiple(self):
        def multiple_commits():
            self.bw.commit()
            self.bw.commit()
        multiple_commits()
        self.bw.tri(multiple_commits)

    def test_commit_accept(self):
        def fun():
            self.bw.next()
            self.bw.commit()
        self.bw.tri(fun)
        self.assertEquals(self.bw.peek(), 'b')
    
    def test_commit_fail(self):
        def fun():
            self.bw.next()
            self.bw.commit()
            self.bw.fail()
        self.assertRaises(NoMatch, p(self.bw.tri, fun))
        self.assertEquals(self.bw.peek(), 'b')
    
    def test_choice_null(self):
        self.bw.choice()
    
    def test_choice_accept(self):
        self.bw.choice(self.bw.fail, self.bw.next)
        self.bw.choice(self.bw.next, self.bw.fail)
        self.bw.choice(self.bw.next, self.bw.next)
        self.assertEquals(self.bw.peek(), 'd')
    
    def test_choice_fail(self):
        self.assertRaises(NoMatch, p(self.bw.choice, self.bw.fail, self.bw.fail))
    
    def test_choice_commit_fail(self):
        def fun():
            self.bw.next()
            self.bw.commit()
            self.bw.fail()
        self.assertRaises(NoMatch, p(self.bw.choice, fun))
        self.assertEquals(self.bw.peek(), 'b')

if __name__ == '__main__':
    unittest.main()

__all__ = ['TestDefaultDiagnostics', 'TestBufferWalker', ]
