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

try:
    from functools import partial
except ImportError:
    def __merged(d1,d2):
        """Dictionary merge"""
        d = d1.copy()
        d.update(d2)
        return d

    def partial(*args,**kw):
        """Return a version of a function with some arguments already supplied.
        """
        fn = args[0]
        args = args[1:]
        return lambda *args2,**kw2: fn(*(args+args2),**__merged(kw,kw2))

from itertools import izip, count
from operator import add
import threading

class NoMatch(Exception):
    def __init__(self, token, pos, expecting, flags=[]):
        self.token = token
        self.pos = pos
        self.expecting = expecting
        self.flags = flags
        self.message = None
    
    @classmethod
    def join(cls, failures):
        token = failures[0].token
        pos = failures[0].pos
        expecting = sorted(set(reduce(add, [f.expecting for f in failures], [])))
        return NoMatch(token, pos, expecting)

    @property
    def default_message(self):
        return "\nParse error at " + str(self.pos) \
               + "\nexpecting one of " + ', '.join(map(lambda x:repr(x), self.expecting)) \
               + "\ngot " + repr(self.token) \
               + ( self.flags and "\nwith " + ', '.join(map(lambda x:str(x), self.flags)) or '' )
    
    def __repr__(self):
        return self.message or self.default_message
    
    def __str__(self):
        return repr(self)


FailedAfterCutting = "FailedAfterCutting"


class DefaultDiagnostics(object):
    def __init__(self):
        self.tokens = []
        self.offset = 1
    
    def generate_error_message(self, noMatch):
        return noMatch.default_message \
               + "\n" + repr(self.tokens)
    
    def cut(self, col):
        if col is EndOfFile:
            col = self.offset + len(self.tokens)
        to_cut = col - self.offset
        self.tokens = self.tokens[to_cut:]
        self.offset += to_cut
    
    def wrap(self, stream):
        for r in izip(stream, count(1)):
            self.tokens.append(r)
            yield r


class EOF(object):
    def __str__(self): return "EOF"
    def __repr__(self): return "EOF()"
    def __nonzero__(self): return False


EndOfFile = EOF()


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
    def __init__(self, source, diag=None):
        if diag is None:
            diag = DefaultDiagnostics()
        self.source = diag.wrap(iter(source))
        try:
            self.buffer = [self.source.next()]
        except StopIteration:
            self.buffer = []
        self.index = 0
        self.len = len(self.buffer)
        self.depth = 0
        self.offset = 0
        self.commit_depth = 0
        self.diag = diag
    
    def __nonzero__(self):
        return self.peek() is not EndOfFile
    
    def _fill(self, size):
        """fills the internal buffer from the source iterator"""
        try:
            for i in range(size):
                self.buffer.append(self.source.next())
        except StopIteration:
            self.buffer.append((EndOfFile, EndOfFile))
        self.len = len(self.buffer)
    
    def next(self):
        """Advances to and returns the next token or returns EndOfFile"""
        self.index += 1
        t = self.peek()
        if not self.depth:
            self._cut()
        return t
    
    def current(self):
        """Returns the current (token, position) or (EndOfFile, EndOfFile)"""
        if self.index >= self.len:
            self._fill((self.index - self.len) + 1)
        return self.index < self.len and self.buffer[self.index] or (EndOfFile, EndOfFile)
    
    def peek(self):
        """Returns the current token or EndOfFile"""
        return self.current()[0]
    
    def pos(self):
        """Returns the current position or EndOfFile"""
        return self.current()[1]
    
    def fail(self, expecting=[]):
        raise NoMatch(self.peek(), self.pos(), expecting)
    
    def tri(self, parser, *args, **kwargs):
        old_depth = self.commit_depth
        self.commit_depth = self.depth
        self.depth += 1
        result = parser(*args, **kwargs)
        self.commit()
        self.commit_depth = old_depth
        return result
    
    def commit(self):
        self.depth = self.commit_depth
        if not self.depth:
            self._cut()
    
    def _cut(self):
        self.buffer = self.buffer[self.index:]
        self.len = len(self.buffer)
        self.offset += self.index
        self.index = 0
        self.depth = 0
        self.diag.cut(self.pos())
    
    def choice(self, *parsers):
        if not parsers:
            return
        start_offset = self.offset
        start_index = self.index
        start_depth = self.depth
        start_token = self.peek()
        start_pos = self.pos()
        failures = []
        for parser in parsers:
            try:
                return parser()
            except NoMatch, e:
                if self.depth < start_depth:
                    raise Exception("Picoparse: Internal error")
                if not failures or e.pos > failures[0].pos:
                    failures = [e]
                elif e.pos == failures[0].pos:
                    failures.append(e)
                if self.offset != start_offset:
                    if FailedAfterCutting not in e.flags:
                        e.flags.append(FailedAfterCutting)
                    break
                if self.depth > start_depth:
                    self.depth = start_depth
                self.index = start_index
        raise NoMatch.join(failures)

local_ps = threading.local()

################################################################
# Picoparse core API

def desc(name):
    def decorator(parser):
        def decorated(*args, **kwargs):
            cur_pos = pos()
            try:
                return parser(*args, **kwargs)
            except NoMatch, e:
                if e.pos == cur_pos:
                    e.expecting = [name]
                raise
        return decorated
    return decorator

def p(name, parser, *args1, **kwargs1):
    if callable(name):
        return partial(name, parser, *args1, **kwargs1)
    
    def p_desc(*args2, **kwargs2):
        cur_pos = pos()
        try:
            args = args1 + args2
            kwargs = {}
            kwargs.update(kwargs1)
            kwargs.update(kwargs2)
            return parser(*args, **kwargs)
        except NoMatch, e:
            if e.pos == cur_pos:
                e.expecting = [name]
            raise
    return p_desc

next = lambda: local_ps.value.next()
peek = lambda: local_ps.value.peek()
fail = lambda expecting=[]: local_ps.value.fail(expecting)
commit = lambda: local_ps.value.commit()
choice = lambda *options: local_ps.value.choice(*options)
is_eof = lambda: bool(local_ps.value)
pos = lambda: local_ps.value.pos()
diag = lambda: local_ps.value.diag

def tri(parser):
    def tri_block(*args, **kwargs):
        return local_ps.value.tri(parser, *args, **kwargs)
    return tri_block

def run_parser(parser, input, wrapper=None):
    old = getattr(local_ps, 'value', None)
    local_ps.value = BufferWalker(input, wrapper)
    try:
        result = parser(), remaining()
    except NoMatch, e:
        e.message = getattr(local_ps.value.diag, 'generate_error_message', lambda x: None)(e)
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
    if ch is EndOfFile:
        fail(["not eof"])
    next()
    return ch

def one_of(these):
    """Returns the current token if is found in the collection provided.
    
    Fails otherwise.
    """
    ch = peek()
    try:
        if (ch is EndOfFile) or (ch not in these):
            fail(list(these))
    except TypeError:
        if ch != these:
            fail([these])
    next()
    return ch

def not_one_of(these):
    """Returns the current token if it is not found in the collection provided.
    
    The negative of one_of. 
    """
    ch = peek()
    desc = "not_one_of" + repr(these)
    try:
        if (ch is EndOfFile) or (ch in these):
            fail([desc])
    except TypeError:
        if ch != these:
            fail([desc])
    next()
    return ch

def _fun_to_str(f):
    name = getattr(f, "__name__", "???")
    pos = getattr(f, "func_code", False)
    if pos:
        pos = pos.co_filename + ":" + str(pos.co_firstlineno)
    else:
        pos = "???"
    return name + " at " + pos

def satisfies(guard):
    """Returns the current token if it satisfies the guard function provided.
    
    Fails otherwise.
    This is the a generalisation of one_of.
    """
    i = peek()
    if (i is EndOfFile) or (not guard(i)):
        fail(["<satisfies predicate " + _fun_to_str(guard) + ">"])
    next()
    return i

def optional(parser, default=None):
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
            fail(["not " + _fun_to_str(parser)])
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

def sep1(parser, separator):
    """Like sep but must consume at least one of parser.
    """
    first = [parser()]
    def inner():
        separator()
        return parser()
    return first + many(tri(inner))

def sep(parser, separator):
    """Consumes zero or more of parser, separated by separator.
    
    Returns a list of parser's results
    """
    return optional(partial(sep1, parser, separator), [])

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

def cue(*parsers):
    """"Runs multiple parsers and returns the result of the last.
    """
    if not parsers:
        return None
    for p in parsers[:-1]:
        p()
    return parsers[-1]()

def follow(*parsers):
    """Runs multiple parsers and returns the result of the first.
    """
    if not parsers:
        return None
    v = parsers[0]()
    for p in parsers[1:]:
        p()
    return v

def remaining():
    """Returns the remaining input that has not been parsed.
    """
    tokens = []
    while peek() is not EndOfFile:
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
    
    
    
    
