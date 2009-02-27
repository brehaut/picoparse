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
