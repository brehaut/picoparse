"""picoparse -- a small lexer and parser library. Regular expression free.
"""

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


def generate_parsers(parsers):
    """Given a list of top level parsers (in order), generates a top level parser.
    """
    def lexer(input):
        for result in choice(BufferWalker(input), parsers):
            yield result
    return lexer
    
# parser implementation functions
def choice(remainder, parsers):
    """Trys the parsers passed in order, returning the result of the first successful.
    """
    while remainder:
        for tokeniser in tokenisers:
            try:
                remainder.push()
                token = tokeniser(remainder)
                print token
                remainder.accept()
                yield token
                break
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
