"""Text parsing utilities for picoparse.

These functions exist for convenience; they implement common ideas about text syntax
for instance the quote and quoted parsers assume quotes can be ' or "
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

from picoparse import string, one_of, many, many1, many_until, any_token
from functools import partial

quote = partial(one_of, "\"'")
whitespace_char = partial(one_of, ' \t\n\r')
whitespace = partial(many, whitespace_char)
whitespace1 = partial(many1, whitespace_char)

def build_string(iterable):
    """A utility function to wrap up the converting a list of characters back into a string.
    """
    return u''.join(iterable)
    
def caseless_string(s):
    """Attempts to match input to the letters in the string, without regard for case.
    """
    return string(zip(s.lower(), s.upper()))

def lexeme(parser):
    """Ignores any whitespace surrounding parser.
    """
    whitespace()
    v = parser()
    whitespace()
    return v
    
def quoted(parser=any_token):
    """Parses as much as possible until it encounters a matching closing quote.
    
    By default matches any_token, but can be provided with a more specific parser if required.
    Returns a string
    """
    quote_char = quote()
    value, _ = many_until(parser, partial(one_of, quote_char))
    return build_string(value)

