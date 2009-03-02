"""picoparse -- a small lexer and parser library. Regular expression free.
"""
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

from functools import partial
import threading

class NoMatch(Exception):
    def __str__(self):
        return getattr(self, 'message', '')

class BufferWalker(object):
    """BufferWalker wraps up an iterable and provides an API for infinite lookahead
    but retains laziness. 
    
    BufferWalker will work on anything iterable, and provides an expanded iterator style
    interface.
     - next acts like an iterators next.
     - peek lets you access the current value
     - prev steps backward one item and returns it.
    
    The current index can be saved with the push method, and can be restored with pop. 
    This is to enable trying multiple parsers options. Once a piece of input has been 
    successfully processed, calling 'accept' will clear the internal stack and free up 
    the buffer.
    
    You can test the BufferWalker for Truthiness; if there is still parsable input then 
    it will be truthy, if not, falsy.
    """
    def __init__(self, source):
        self.source = iter(source)
        self.buffer = [self.source.next()]
        self.index = 0
        self.len = len(self.buffer)
        self.depth = 0
        self.offset = 0
    
    def __nonzero__(self):
        return self.peek() is not None
    
    def _fill(self, size):
        """fills the internal buffer from the source iterator"""
        try:
            for i in range(size):
                self.buffer.append(self.source.next())
        except StopIteration:
            self.buffer.append(None)
        self.len = len(self.buffer)
    
    def next(self):
        """Returns the next item or None"""
        self.index += 1
        t = self.peek()
        if self.depth == 0:
            cut()
        return t
    
    def peek(self):
        """Returns the current item or None"""
        if self.index >= self.len:
            self._fill((self.index - self.len) + 1) 
        return self.buffer[self.index] if self.index < self.len else None
    
    def attempt(self):
        result = self.depth
        self.depth += 1
        return result
    
    def fail(self):
        raise NoMatch()
    
    def commit(self, depth = None):
        if self.depth < 0:
            raise Exception("commit without corresponding attempt")
        if depth is None:
            self.depth -= 1
        elif self.depth > depth:
            self.depth = depth
        if self.depth == 0:
            self.cut()
    
    def cut(self):
        self.buffer = self.buffer[self.index:]
        self.len = len(self.buffer)
        self.offset += self.index
        self.index = 0
        self.depth = 0
    
    def choice(self, *parsers):
        if not parsers:
            raise NoMatch()
        start_offset = self.offset
        start_index = self.index
        start_depth = self.depth
        for parser in parsers:
            try:
                return parser()
            except NoMatch:
                if self.offset != start_offset or self.depth < start_depth:
                    if self.depth < start_depth:
                        raise Exception("Commit / cut called")
                    raise
                if self.depth > start_depth:
                    self.depth = start_depth
                self.index = start_index
        else:
            raise NoMatch()

local_ps = threading.local()

################################################################
# Picoparse core API

next = lambda: local_ps.value.next()
peek = lambda: local_ps.value.peek()
fail = lambda: local_ps.value.fail()
commit = lambda: local_ps.value.commit()
cut = lambda: local_ps.value.cut()
choice = lambda *options: local_ps.value.choice(*options)
is_eof = lambda: bool(local_ps.value)

def tri(parser):
    def tri_block(*args, **kwargs):
        depth = local_ps.value.attempt()
        result = parser(*args, **kwargs)
        local_ps.value.commit(depth)
        return result
    return tri_block

def run_parser(parser, input):
    old = getattr(local_ps, 'value', None)
    local_ps.value = BufferWalker(input)
    try:
      result = parser(), remaining()
    except NoMatch, e:
      e.message = "Remaining: %r" %  (remaining())
      raise
    finally:
      local_ps.value = old
    return result

################################################################
# Picoparse additional API

def compose(f, g):
    """Compose returns a two functions composed as a new function.
    
    The first is called with the result of the second as its argument. Any arguments 
    are passed to the second.
    """
    return lambda *args, **kwargs: f(g(*args, **kwargs))

def chain(*args):
    """Runs a series of parsers in sequence passing the result of each parser to the next.
    The result of the last parser is returned.
    """
    def chain_block(*args, **kwargs):
        v = args[0](*args, **kwargs)
        for p in args[1:]:
            v = p(v)
        return v
    return chain_block

def any_token():
    """Will accept any token in the input stream and step forward.
    
    Fails if there is no more tokens
    """
    ch = peek()
    if not ch:
        fail()
    next()
    return ch

def one_of(these):
    """Returns the current token if is found in the collection provided.
    
    Fails otherwise.
    """
    ch = peek()
    try:
        if (ch is None) or (ch not in these):
            fail()
    except TypeError:
        if ch != these:
            fail()
    next()
    return ch

def not_one_of(these):
    """Returns the current token if it is not found in the collection provided.
    
    The negative of one_of. 
    """
    ch = peek()
    try:
        if (ch is None) or (ch in these):
            fail()
    except TypeError:
        if ch != these:
            fail()
    next()
    return ch

def satisfies(guard):
    """Returns the current token if it satisfies the guard function provided.
    
    Fails otherwise.
    This is the a generalisation of one_of.
    """
    i = peek()
    if not guard(i):
        fail()
    next()
    return i

def optional(parser, default):
    """Tries to apply the provided parser, returning default if the parser fails.
    """
    return choice(parser, lambda: default)

def not_followed_by(parser):
    """Succeeds if the given parser cannot consume input"""
    @tri
    def not_followed_by_block():
        failed = object()
        result = optional(tri(parser), failed)
        if result != failed:
            fail()
    choice(not_followed_by_block)

eof = partial(not_followed_by, any_token)

def many(parser):
    """Applies the parser to input zero or more times.
    
    Returns a list of parser results.
    """
    results = []
    terminate = object()
    while local_ps.value:
        result = optional(parser, terminate)
        if result == terminate:
            break
        results.append(result)
    return results

def many1(parser):
    """Like many, but must consume at least one of parser"""
    return [parser()] + many(parser)

def _tag(t, parser):
    def tagged():
        return t, parser()
    return tagged

def many_until(these, term):
    """Consumes as many of these as it can until it term is encountered.
    
    Returns a tuple of the list of these results and the term result 
    """
    results = []
    while True:
        stop, result = choice(_tag(True, term),
                              _tag(False, these))
        if stop:
            return results, result
        else:
            results.append(result)

def many_until1(these, term):
    """Like many_until but must consume at least one of these.
    """
    first = [these()]
    these_results, term_result = many_until(these, term)
    return (first + these_results, term_result)

def sep1(parser, seperator):
    """Like sep but must consume at least one of parser.
    """
    first = [parser()]
    def inner():
        seperator()
        return parser()
    return first + many(inner)

def sep(parser, seperator):
    """Consumes zero or more of parser, seperated by seperator.
    
    Returns a list of parser's results
    """
    return optional(partial(sep1, parser, seperator), [])

def n_of(parser, n):
    """Consumes n of parser, returning a list of the results.
    """
    return [parser() for i in range(n)]

def string(string):
    """Iterates over string, matching input to the items provided.
    
    The most obvious usage of this is to accept an entire string of characters,
    However this is function is more general than that. It takes an iterable
    and for each item, it tries one_of for that set. For example, 
       string(['aA','bB','cC'])
    will accept 'abc' in either case. 
    
    note, If you wish to match caseless strings as in the example, use 
    picoparse.text.caseless_string.
    """
    found = []
    for c in string:
        found.append(one_of(c))
    return found

def cue(cue, parser):
    """Returns the result of parser if it cue preceeds it.
    """
    cue()
    return parser()

def follow(parser, following):
    v = parser()
    following()
    return v

def remaining():
    """Returns the remaining input that has not been parsed.
    """
    tokens = []
    while peek():
        tokens.append(peek())
        next()
    return tokens

def seq(*sequence):
    """Runs a series of parsers in sequence optionally storing results in a returned dictionary.
    
    For example:
    seq(whitespace, ('phone', digits), whitespace, ('name', remaining))
    """
    results = {}
    for p in sequence:
        if callable(p): 
            p()
            continue
        k, v = p
        results[k] = v()
    return results
    
    
    
    
