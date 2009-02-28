"""picoparse -- a small lexer and parser library. Regular expression free.
"""
# Copyright (c) 2008, Andrew Brehaut, Steven Ashley
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
import pdb

class NoMatch(Exception): pass



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
    
    def prev(self):
        """Returns the previous item, or None
        """
        self.index -= 1
        if self.index < 0:
            self.index = 0
            return None
        return self.peek()
    
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
        #print "Cutting", self.offset
    
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

################################################################

local_ps = threading.local()

def ps_fun(name):
    def fun(*args, **kwargs):
        return getattr(local_ps.value, name)(*args, **kwargs)
    return fun

################################################################

next    = ps_fun('next')
prev    = ps_fun('prev')
peek    = ps_fun('peek')
attempt = ps_fun('attempt')
fail    = ps_fun('fail')
commit  = ps_fun('commit')
cut     = ps_fun('cut')
choice  = ps_fun('choice')

def is_eof(): return bool(local_ps.value)

def run_parser(parser, input):
    old = getattr(local_ps, 'value', None)
    local_ps.value = BufferWalker(input)
    try:
      result = parser(), remaining()
    except NoMatch:
      print remaining()
      raise
    finally:
      local_ps.value = old
    return result

def any_token():
    ch = next()
    if not ch:
        fail()
    return ch

def one_of(these):
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
    ch = peek()
    try:
        if (ch is None) or (ch in these):
            fail()
    except TypeError:
        if ch != these:
            fail()
    next()
    return ch

def optional(parser, default):
    return choice(parser, lambda: default)

def notfollowedby(parser):
    failed = object()
    result = optional(tri(parser), failed)
    if result != failed:
        fail()

eof = partial(notfollowedby, any_token)

def tri(parser):
    def tri_block(*args, **kwargs):
        depth = attempt()
        result = parser(*args, **kwargs)
        commit(depth)
        return result
    return tri_block

def many(parser):
    results = []
    terminate = object()
    while local_ps.value:
        result = optional(parser, terminate)
        if result == terminate:
            break
        results.append(result)
    return results

def tag(t, parser):
    def tagged():
        return t, parser()
    return tagged

def many_until(these, term):
    results = []
    while True:
        stop, result = choice(tag(True, term),
                              tag(False, these))
        if stop:
            return result, results
        else:
            results.append(result)

def many1(parser):
    return [parser()] + many(parser)

def n_of(parser, n):
    return [parser() for i in range(n)]

def string(string):
    for c in string:
        one_of(c)
    return string

def remaining():
    tokens = []
    while peek():
        tokens.append(peek())
        next()
    return tokens

