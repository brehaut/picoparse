def runparser(parser, input):
    buf = BufferWalker(input)
    result = parser(buf)
    print 'result:', result
    print 'remaining:', rest(buf)

def parser1(ps):
    return many(ps, parser2)

def parser2(ps):
    return choice(ps, [parser3, parser4])

def parser3(ps):
    return choice(ps, [parser5, parser6])

def parser4(ps):
    return choice(ps, [parser7, parser8])

def parser5(ps):
    scan_char('a', ps)
    scan_char('b', ps)
    return 'ab'

def parser6(ps):
    scan_char('b', ps)
    scan_char('a', ps)
    return 'ba'

def parser7(ps):
    scan_char('a', ps)
    scan_char('a', ps)
    return 'aa'

def parser8(ps):
    scan_char('b', ps)
    scan_char('b', ps)
    return 'bb'

runparser(parser1, "abacadaae")
