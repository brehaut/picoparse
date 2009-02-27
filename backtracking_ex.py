from picoparse import next, prev, peek, attempt, fail, commit, cut, choice, run_parser, optional, many, remaining, tri

def char(cs):
    c = peek()
    if c is not None and c not in cs:
        fail()
    next()

def parser1():
    return many(parser2)

def parser2():
    return choice(parser3, parser4)

def parser3():
    return choice(parser5, parser6)

def parser4():
    return choice(parser7, parser8)

@tri
def parser5():
    char('a')
    char('a')
    commit()
    return 'aa'

@tri
def parser6():
    char('b')
    char('a')
    commit()
    return 'ba'

@tri
def parser7():
    char('a')
    char('b')
    commit()
    return 'ab'

@tri
def parser8():
    char('b')
    char('b')
    commit()
    return 'bb'

print run_parser(parser1, "aaabbbba")
