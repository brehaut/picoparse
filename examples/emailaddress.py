#!/usr/bin/env python
# encoding: utf-8

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
"""
emailaddress.py

An implentation of rfc 5322 email address checking. 

See http://tools.ietf.org/html/rfc5322 for the full specification. This program
implements the grammer for email address validation in sections 3.4 and 3.4.1 and related
grammers requird by those sections. This is an example of translating a grammer verbatim

Copyright (c) 2009 Andrew Brehaut. All rights reserved.
"""
from string import ascii_letters, digits

from picoparse import one_of, many, many1, not_one_of, run_parser, tri, commit, optional, fail
from picoparse import choice, string, peek, string, eof, many_until, any_token, satisfies
from picoparse import sep, sep1, compose, cue, seq
from picoparse.text import run_text_parser
from picoparse import partial


# generic parsers
def char_range(lower, upper):
    satisfies(lambda c: lower <= ord(c) <= upper)

# character parsers
comma = partial(one_of, ",")
colon = partial(one_of, ":")
semi = partial(one_of, ";")
angle = partial(one_of, "<")
unangle = partial(one_of, ">")
square = partial(one_of, "[")
unsquare = partial(one_of, "]")
paren = partial(one_of, "(")
unparen = partial(one_of, ")")
at = partial(one_of, "@")
dot = partial(one_of, ".")
slash = partial(one_of, "/")
backslash = partial(one_of, "\\")

# common rfc grammers
DQUOTE = partial(one_of, '"') # Double quote
VCHAR = partial(char_range, int('21', 16), int('7E', 16)) # visible (printing) characters
WSP = partial(one_of, " \t") # whitespace
CR = partial(one_of, chr(int('0D', 16))) # carriage return
LF = partial(one_of, chr(int('0A', 16))) # line feed
CRLF = partial(seq, CR, LF) # internet standard new line

# set the obsolete methods to fail
obs_dtext = fail
obs_domain = fail
obs_qtext = fail
obs_qp = fail
obs_local_part = fail
obs_addr_list = fail
obs_mbox_list = fail
obs_group_list = fail
obs_angle_addr = fail
obs_FWS = fail
obs_ctext = fail
obs_phrase = fail

# placeholders
CFWS = None
FWS = None


# Section 3.2.4 Parsers - http://tools.ietf.org/html/rfc5322#section-3.2.3
# qtext           =   %d33 /             ; Printable US-ASCII
#                     %d35-91 /          ;  characters not including
#                     %d93-126 /         ;  "\" or the quote character
#                     obs-qtext
qtext = partial(choice, partial(one_of, chr(33)), 
                        partial(char_range, 35, 91), 
                        partial(char_range, 93, 126),
                        obs_qtext)

# quoted-pair     =   ("\" (VCHAR / WSP)) / obs-qp
quoted_pair = partial(choice, partial(seq, backslash, partial(choice, VCHAR, WSP))
                            , obs_qp)

# qcontent        =   qtext / quoted-pair
qcontent = partial(choice, qtext, quoted_pair)

# quoted-string   =   [CFWS]
#                    DQUOTE *([FWS] qcontent) [FWS] DQUOTE
#                    [CFWS]
def quoted_string():
    optional(CFWS)
    DQUOTE()
    many(partial(seq, partial(optional, FWS), qcontent))
    optional(FWS)
    DQUOTE()
    optional(CFWS)
    

# Section 3.2.2 Parsers - http://tools.ietf.org/html/rfc5322#section-3.2.2
# FWS             =   ([*WSP CRLF] 1*WSP) /  obs-FWS ; Folding white space
FWS = partial(choice, partial(seq, partial(optional, partial(seq, partial(many, WSP), CRLF))
                                 , partial(many1, WSP))
                    , obs_FWS)
# ctext           =   %d33-39 /          ; Printable US-ASCII
#                     %d42-91 /          ;  characters not including
#                     %d93-126 /         ;  "(", ")", or "\"
#                     obs-ctext
ctext = partial(choice, partial(char_range, 33, 39)
                      , partial(char_range, 42, 91)
                      , partial(char_range, 93, 126)
                      , obs_ctext)


# comment         =   "(" *([FWS] ccontent) [FWS] ")"
def comment():
    paren()
    many(partial(seq, partial(optional, FWS), ccontent))
    optional(FWS)

# ccontent        =   ctext / quoted-pair / comment
ccontent = partial(choice, ctext, quoted_pair, comment)

# CFWS            =   (1*([FWS] comment) [FWS]) / FWS    
CFWS = partial(choice, partial(seq, partial(many1, partial(seq, partial(optional, FWS)
                                                              , comment))
                                  , partial(optional, FWS))
                     , FWS)

# Section 3.2.3 Parsers - http://tools.ietf.org/html/rfc5322#section-3.2.3

# atext           =   ALPHA / DIGIT /    ; Printable US-ASCII
#                     "!" / "#" /        ;  characters not including
#                     "$" / "%" /        ;  specials.  Used for atoms.
#                     "&" / "'" /
#                     "*" / "+" /
#                     "-" / "/" /
#                     "=" / "?" /
#                     "^" / "_" /
#                     "`" / "{" /
#                     "|" / "}" /
#                     "~"
atext = partial(one_of, ascii_letters + digits + "!#$%&'*+-/=?^_`{|}~")
atext_string = partial(many1, atext)

# atom            =   [CFWS] 1*atext [CFWS]
def atom():
    optional(CFWS)
    atext_string()
    optional(CFWS)

# dot-atom-text   =   1*atext *("." 1*atext)
dot_atom_text = partial(sep1, atext_string, dot)
    
# dot-atom        =   [CFWS] dot-atom-text [CFWS]
def dot_atom():
    optional(CFWS)
    dot_atom_text()
    optional(CFWS)

# specials        =   "(" / ")" /        ; Special characters that do
#                     "<" / ">" /        ;  not appear in atext
#                     "[" / "]" /
#                     ":" / ";" /
#                     "@" / "\" /
#                     "," / "." /
#                     DQUOTE
specials = partial(one_of, '()<>[]:;@\,."')


# Section 3.2.5 Parsers - http://tools.ietf.org/html/rfc5322#section-3.2.5

# word            =   atom / quoted-string
word = partial(choice, tri(atom), quoted_string)

# phrase          =   1*word / obs-phrase
phrase = partial(choice, tri(partial(many1, word)), obs_phrase)

# Section 3.4.1 Parsers - http://tools.ietf.org/html/rfc5322#section-3.4.1

# dtext           =   %d33-90 /          ; Printable US-ASCII
#                     %d94-126 /         ;  characters not including
#                     obs-dtext          ;  "[", "]", or "\"
dtext = partial(choice, partial(char_range, 33, 99), partial(char_range, 94, 126), obs_dtext)

# domain-literal  =   [CFWS] "[" *([FWS] dtext) [FWS] "]" [CFWS]
def domain_literal():
    optional(CFWS)
    square()
    many(partial(seq, partial(optional, FWS), dtext))
    optional(FWS)
    unsquare()
    optional(CFWS)

# domain          =   dot-atom / domain-literal / obs-domain
domain = partial(choice, dot_atom, domain_literal, obs_domain)

# local-part      =   dot-atom / quoted-string / obs-local-part
local_part = partial(choice, dot_atom, quoted_string, obs_local_part)

# addr-spec       =   local-part "@" domain
addr_spec = partial(seq, local_part, at, domain)



# Section 3.4 Parsers - http://tools.ietf.org/html/rfc5322#section-3.4
address = None # define the reference, allows circular definition
mailbox = None

# address-list    =   (address *("," address)) / obs-addr-list
address_list = tri(partial(choice, partial(seq, address, comma), obs_addr_list))

# mailbox-list    =   (mailbox *("," mailbox)) / obs-mbox-list
mailbox_list = tri(partial(choice, partial(sep, mailbox, comma), obs_mbox_list))

# group-list      =   mailbox-list / CFWS / obs-group-list
group_list = tri(partial(choice, mailbox_list, CFWS, obs_group_list))

# display-name    =   phrase
display_name = tri(phrase)

# group           =   display-name ":" [group-list] ";" [CFWS]
@tri
def group():
    display_name()
    colon()
    optional(group_list)
    semi()  

# angle-addr      =   [CFWS] "<" addr-spec ">" [CFWS] /
#                     obs-angle-addr
@tri
def angle_addr_nonobs():
    optional(CFWS)
    angle()
    addr_spec()
    unangle()
    optional(CFWS)
angle_addr = partial(choice, angle_addr_nonobs, obs_angle_addr)

# name-addr       =   [display-name] angle-addr
@tri
def name_addr():
    optional(display_name)
    angle_addr()

# mailbox         =   name-addr / addr-spec    
mailbox = partial(choice, name_addr, addr_spec)

# address         =   mailbox / group
address = partial(choice, mailbox, group)
 
 
def validate_address(text):
    try: 
        run_text_parser(partial(seq, address, partial(one_of, '\n')), text)
        return True
    except Exception, e:
        print e
        return False
    
import sys
print "address is valid" if validate_address(sys.argv[1]) else "address is not valid"
