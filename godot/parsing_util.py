#------------------------------------------------------------------------------
#  Copyright (c) 2008 Richard W. Lincoln
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#  IN THE SOFTWARE.
#------------------------------------------------------------------------------

""" Defines convenience pyparsing constructs and token converters.

References:
    sparser.py by Tim Cera timcera@earthlink.net

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import re

from itertools import izip

from pyparsing import \
    TokenConverter, oneOf, string, Literal, Group, Word, Optional, Combine, \
    sglQuotedString, dblQuotedString, restOfLine, nums, removeQuotes, Regex, \
    OneOrMore

#------------------------------------------------------------------------------
#  "ToBoolean" class:
#------------------------------------------------------------------------------

class ToBoolean(TokenConverter):
    """ Converter to make token boolean """

    def postParse(self, instring, loc, tokenlist):
        """ Converts the first token to boolean """

        return bool(tokenlist[0])

#------------------------------------------------------------------------------
#  "ToInteger" class:
#------------------------------------------------------------------------------

class ToInteger(TokenConverter):
    """ Converter to make token into an integer """

    def postParse(self, instring, loc, tokenlist):
        """ Converts the first token to an integer """

        return int(tokenlist[0])

#------------------------------------------------------------------------------
#  "ToFloat" class:
#------------------------------------------------------------------------------

class ToFloat(TokenConverter):
    """ Converter to make token into a float """

    def postParse(self, instring, loc, tokenlist):
        """ Converts the first token into a float """

        return float(tokenlist[0])

# punctuation
colon  = Literal(":")
lbrace = Literal("{")
rbrace = Literal("}")
lbrack = Literal("[")
rbrack = Literal("]")
lparen = Literal("(")
rparen = Literal(")")
equals = Literal("=")
comma  = Literal(",")
dot    = Literal(".")
slash  = Literal("/")
bslash = Literal("\\")
star   = Literal("*")
semi   = Literal(";")
at     = Literal("@")
minus  = Literal("-")
pluss  = Literal("+")

#------------------------------------------------------------------------------
#  Convenience pyparsing constructs
#------------------------------------------------------------------------------

decimal_sep = "."

sign = oneOf("+ -")

scolon = Literal(";").suppress()

matlab_comment = Group(Literal('%') + restOfLine).suppress()
psse_comment = Literal('@!') + Optional(restOfLine)

# part of printables without decimal_sep, +, -
special_chars = string.replace(
    '!"#$%&\'()*,./:;<=>?@[\\]^_`{|}~', decimal_sep, ""
)

boolean = ToBoolean(ToInteger(Word("01", exact=1))).setName("bool")

integer = ToInteger(
    Combine(Optional(sign) + Word(nums))
).setName("integer")

positive_integer = ToInteger(
    Combine(Optional("+") + Word(nums))
).setName("integer")

negative_integer = ToInteger(
    Combine("-" + Word(nums))
).setName("integer")

real = ToFloat(
    Combine(
        Optional(sign) + Word(nums) + Optional(decimal_sep + Word(nums)) +
        Optional(oneOf("E e") + Word(nums))
    )
).setName("real")

positive_real = ToFloat(
    Combine(
        Optional("+") + Word(nums) + decimal_sep + Optional(Word(nums)) +
        Optional(oneOf("E e") + Word(nums))
    )
).setName("real")

negative_real = ToFloat(
    Combine(
        "-" + Word(nums) + decimal_sep + Optional(Word(nums)) +
        Optional(oneOf("E e") + Word(nums))
    )
).setName("real")

q_string = (sglQuotedString | dblQuotedString).setName("q_string")

#double_quoted_string = QuotedString('"', multiline=True,escChar="\\",
#    unquoteResults=True) # dblQuotedString
double_quoted_string = Regex(r'\"(?:\\\"|\\\\|[^"])*\"', re.MULTILINE)
double_quoted_string.setParseAction(removeQuotes)
quoted_string = Combine(
    double_quoted_string+
    Optional(OneOrMore(pluss+double_quoted_string)), adjacent=False
)

# add other characters we should skip over between interesting fields
#integer_junk = Optional(
#    Suppress(Word(alphas + special_chars + decimal_sep))
#).setName("integer_junk")
#
#real_junk = Optional(
#    Suppress(Word(alphas + special_chars))
#).setName("real_junk")
#
#q_string_junk = SkipTo(q_string).setName("q_string_junk")

#------------------------------------------------------------------------------
#  A convenient function for calculating a unique name given a list of
#  existing names.
#------------------------------------------------------------------------------

def make_unique_name(base, existing=[], format="%s_%s"):
    """
    Return a name, unique within a context, based on the specified name.

    base: the desired base name of the generated unique name.
    existing: a sequence of the existing names to avoid returning.
    format: a formatting specification for how the name is made unique.

    """

    count = 2
    name = base
    while name in existing:
        name = format % (base, count)
        count += 1

    return name

#------------------------------------------------------------------------------
#  "nsplit" function:
#------------------------------------------------------------------------------

def nsplit(seq, n=2):
    """ Split a sequence into pieces of length n

    If the length of the sequence isn't a multiple of n, the rest is discarded.
    Note that nsplit will split strings into individual characters.

    Examples:
    >>> nsplit("aabbcc")
    [("a", "a"), ("b", "b"), ("c", "c")]
    >>> nsplit("aabbcc",n=3)
    [("a", "a", "b"), ("b", "c", "c")]

    # Note that cc is discarded
    >>> nsplit("aabbcc",n=4)
    [("a", "a", "b", "b")]

    """

    return [xy for xy in izip(*[iter(seq)]*n)]

#------------------------------------------------------------------------------
#  "windows" function:
#------------------------------------------------------------------------------

def windows(iterable, length=2, overlap=0, padding=True):
    """ Code snippet from Python Cookbook, 2nd Edition by David Ascher,
    Alex Martelli and Anna Ravenscroft; O'Reilly 2005

    """

    it = iter(iterable)
    results = list(itertools.islice(it, length))
    while len(results) == length:
        yield results
        results = results[length-overlap:]
        results.extend(itertools.islice(it, length-overlap))
    if padding and results:
        results.extend(itertools.repeat(None, length-len(results)))
        yield results

# EOF -------------------------------------------------------------------------
