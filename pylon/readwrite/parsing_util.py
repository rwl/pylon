#------------------------------------------------------------------------------
# Copyright (C) 2010 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------

""" Defines convenience pyparsing constructs and token converters.

    References:
        sparser.py by Tim Cera timcera@earthlink.net
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from pyparsing import \
    TokenConverter, oneOf, string, Literal, Group, Word, Optional, Combine, \
    sglQuotedString, dblQuotedString, restOfLine, nums

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
        Optional(sign) +
        Word(nums) +
        Optional(decimal_sep + Word(nums)) +
        Optional(oneOf("E e") + Optional(sign) + Word(nums))
    )
).setName("real")

#real = ToFloat(
#       Combine(Optional(sign) +
#               Word(nums) +
#               decimal_sep +
#               Optional(Word(nums)) +
#               Optional(oneOf("E e") +
#                        Word(nums)))).setName("real")

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

comma_sep = comma.suppress()

#------------------------------------------------------------------------------
#  A convenient function for calculating a unique name given a list of
#  existing names.
#------------------------------------------------------------------------------

def make_unique_name(base, existing=[], format="%s_%s"):
    """ Return a name, unique within a context, based on the specified name.

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

# EOF -------------------------------------------------------------------------
