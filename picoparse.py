"""picoparse -- a small lexer and parser library. Regular expression free.
"""
# Copyright (c) 2008, Andrew Brehaut
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
        self.stack = []
    
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
        return self.peek()
    
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

    def push(self):
        """Remember the current location."""
        self.stack.append(self.index)
        
    def pop(self):
        """Return to the previously remember location."""
        if self.stack:
            self.index = self.stack.pop()
        
    def accept(self):
        """Refresh the stack. 
        the current index is the start of the buffer, processed data is released.
        """
        self.buffer = self.buffer[self.index:]
        self.len = len(self.buffer)
        self.stack = []
        self.index = 0

def many(remainder, parser):
    """Tries one parser over and over until it fails. Returns sucessive results in a generator.
    """
    result = []
    while remainder:
        try:
            remainder.push()
            result.append(parser(remainder))
            remainder.accept()
        except NoMatch:
            remainder.pop()
            return result

def choice(remainder, parsers):
    """Tries the parsers passed in order, returning the result of the first successful.
    """
    for parser in parsers:
        try:
            remainder.push()
            token = parser(remainder)
            remainder.accept()
            return token
        except NoMatch:
            remainder.pop()
    else:
        raise NoMatch()


def in_set(item, possibles):
    """is the given item not None and in the set of possibles.
    """
    return  (item is not None) and (item in possibles)

def not_in_set(item, possibles):
    """Is the given item not None and not in the set of possibles.
    """
    return  (item is not None) and (item not in possibles)

def scan_char(possibles, items):
    """returns the current item if in the set of possibles, and steps forward,
    otherwise raises NoMatch
    """
    ch = items.peek()
    if not_in_set(ch, possibles):
        raise NoMatch()
    items.next()
    return ch

def scan_nchar(possibles, items):
    """returns the current item if not in the set of possibles, and steps forward,
    otherwise raises NoMatch. The inverse of scan_char
    """
    ch = items.peek()
    if in_set(ch, possibles):
        raise NoMatch()
    items.next()
    return ch

def scan_collect(scanner, possibles, items):
    """Applies a scanner to items repeatedly with possibles as its first arg"""
    try: 
        match = []
        while items.peek():
            match.append(scanner(possibles, items))
    except NoMatch:
        return match

scan_while = partial(scan_collect, scan_char)
scan_until = partial(scan_collect, scan_nchar)
scan_whitespace = partial(scan_while, ' \t\n\r')

def rest(buf):
    result = []
    while True:
        token = buf.next()
        if token:
            result.append(token)
        else:
            break
    return u''.join(result)


