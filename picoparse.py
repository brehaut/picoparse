from functools import partial

class NoMatch(Exception): pass

class BufferWalker(object):
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
        self.index += 1
        return self.peek()
    
    def prev(self):
        self.index -= 1
        if self.index < 0:
            self.index = 0
        return self.peek()
        
    def peek(self):
        if self.index >= self.len:
            self._fill((self.index - self.len) + 1) 
        return self.buffer[self.index] if self.index < self.len else None

    def push(self):
        self.stack.append(self.index)
        
    def pop(self):
        if self.stack:
            self.index = self.stack.pop()
        
    def accept(self):
        """Refresh the stack. from now on, the current index is the start
        """
        self.buffer = self.buffer[self.index:]
        self.len = len(self.buffer)
        self.stack = []
        self.index = 0

def generate_lexer(tokenisers):
    def lexer(input):
        for result in choice(BufferWalker(input), tokenisers):
            yield result
    return lexer
    
def choice(remainder, tokenisers):
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

def in_set(ch, set):
    return  (ch is not None) and (ch in set)

def not_in_set(ch, set):
    return  (ch is not None) and (ch not in set)

def scan_char(charset, chars):
    ch = chars.peek()
    if not_in_set(ch, charset):
        raise NoMatch()
    chars.next()
    return ch

def scan_nchar(charset, chars):
    ch = chars.peek()
    if in_set(ch, charset):
        raise NoMatch()
    chars.next()
    return ch

def scan_collect(scanner, charset, chars):
    try: 
        match = []
        while chars.peek():
            match.append(scanner(charset, chars))
    except NoMatch:
        return match

scan_while = partial(scan_collect, scan_char)
scan_until = partial(scan_collect, scan_nchar)
scan_whitespace = partial(scan_while, ' \t\n\r')
