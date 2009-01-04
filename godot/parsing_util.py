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

""" Defines convenient pyparsing constructs and token converters.

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
    OneOrMore, hexnums, alphas, alphanums, CaselessLiteral, And, NotAny, Or, \
    White, QuotedString

#from enthought.enable.colors import color_table

from godot.common import color_schemes

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
dquote = Literal('"')

#------------------------------------------------------------------------------
#  Convenient pyparsing constructs.
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

# Integer ---------------------------------------------------------------------

integer = ToInteger(
    Combine(Optional(sign) + Word(nums))
).setName("integer")

positive_integer = ToInteger(
    Combine(Optional("+") + Word(nums))
).setName("integer")

negative_integer = ToInteger(
    Combine("-" + Word(nums))
).setName("integer")

# Boolean ---------------------------------------------------------------------

#boolean = ToBoolean(ToInteger(Word("01", exact=1))).setName("bool")
true = CaselessLiteral("True")# | And(integer, NotAny(Literal("0")))
false = CaselessLiteral("False") | Literal("0")
boolean = ToBoolean(true | false).setResultsName("boolean")

# Real ------------------------------------------------------------------------

real = ToFloat(
    Combine(
        Optional(dquote).suppress() + Optional(sign) + Word(nums) +
        Optional(decimal_sep + Word(nums)) +
        Optional(oneOf("E e") + Word(nums)) + Optional(dquote).suppress()
    )
).setName("real")

# TODO: Positive real number between zero and one.
decimal = real

# String ----------------------------------------------------------------------

q_string = (sglQuotedString | dblQuotedString).setName("q_string")

#double_quoted_string = QuotedString('"', multiline=True,escChar="\\",
#    unquoteResults=True) # dblQuotedString
double_quoted_string = Regex(r'\"(?:\\\"|\\\\|[^"])*\"', re.MULTILINE)
double_quoted_string.setParseAction(removeQuotes)
quoted_string = Combine(
    double_quoted_string+
    Optional(OneOrMore(pluss+double_quoted_string)), adjacent=False
)
word = quoted_string#Word(alphanums)

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

rect = real.setResultsName("llx") + real.setResultsName("lly") + \
    real.setResultsName("urx") + real.setResultsName("ury")

hex_color = Word(hexnums, exact=2) #TODO: Optional whitespace
rgb = Literal("#") + hex_color.setResultsName("red") + \
    hex_color.setResultsName("green") + hex_color.setResultsName("blue")
rgba = rgb + hex_color.setResultsName("alpha")
hsv = decimal.setResultsName("hue") + decimal.setResultsName("saturation") + \
    decimal.setResultsName("value")
color_name = double_quoted_string | Word(alphas)
color = rgb | rgba | hsv | color_name

cluster_mode = CaselessLiteral("local") | CaselessLiteral("global") | \
    CaselessLiteral("none")

color_scheme = Or([CaselessLiteral(scheme) for scheme in color_schemes])

esc_string = html_label = quoted_string
lbl_string = esc_string | html_label

point = Optional(dquote).suppress() + real.setResultsName("x") + \
    comma.suppress() + real.setResultsName("y") + \
    Optional((comma + real.setResultsName("z"))) + \
    Optional(dquote).suppress() + Optional(Literal("!").setResultsName("!"))

pointf = Optional(dquote).suppress() + real.setResultsName("x") + \
    comma.suppress() + real.setResultsName("y") + Optional(dquote).suppress()

bb = rect.setResultsName("bb")
bgcolor = color.setResultsName("bgcolor")
center = boolean.setResultsName("center")
charset = word.setResultsName("charset")
clusterrank = cluster_mode.setResultsName("clusterrank")
colorscheme = color_scheme.setResultsName("colorscheme")
comment = word.setResultsName("comment")
compound = boolean.setResultsName("compound")
concentrate = boolean.setResultsName("concentrate")
Damping = real.setResultsName("Damping")
defaultdist = real.setResultsName("defaultdist")
dim = Word("23456789", exact=1).setResultsName("dim")
diredgeconstraints = (boolean |
    CaselessLiteral("heir")).setResultsName("diredgeconstraints")
dpi = real.setResultsName("dpi")
epsilon = real.setResultsName("epsilon")
esep = integer.setResultsName("esep")
fontcolor = color.setResultsName("fontcolor")
fontname = word.setResultsName("fontname")
fontnames = (CaselessLiteral("svg") | CaselessLiteral("ps") |
    CaselessLiteral("gd")).setResultsName("fontnames")
fontpath = word.setResultsName("fontpath")
fontsize = real.setResultsName("fontsize")
K = real.setResultsName("K")
label = lbl_string.setResultsName("label")
labeljust = (CaselessLiteral("c") | CaselessLiteral("r") |
    CaselessLiteral("l")).setResultsName("labeljust")
labelloc = (CaselessLiteral("b") |
    CaselessLiteral("t")).setResultsName("labelloc")
landscape = boolean.setResultsName("landscape")
layers = word.setResultsName("layers")
layersep = (Literal(":\t") | Literal("\t")# | White
).setResultsName("layersep")
levelsgap = real.setResultsName("levelsgap")
lp = point.setResultsName("lp")
margin = (real | pointf).setResultsName("margin")
maxiter = integer.setResultsName("maxiter")
mclimit = real.setResultsName("mclimit")
mindist = real.setResultsName("mindist")
mode = (CaselessLiteral("major") | CaselessLiteral("KK") |
    CaselessLiteral("heir") | CaselessLiteral("ipsep")).setResultsName("mode")
model = (CaselessLiteral("shortpath") | CaselessLiteral("circuit") |
    CaselessLiteral("subset")).setResultsName("model")
mosek = boolean.setResultsName("mosek")
nodesep = real.setResultsName("nodesep")
nojustify = boolean.setResultsName("nojustify")
normalize = boolean.setResultsName("normalize")
nslimit = real.setResultsName("nslimit")
nslimit1 = real.setResultsName("nslimit1")
ordering = (CaselessLiteral("out") |
    CaselessLiteral("in")).setResultsName("ordering")
outputorder = (CaselessLiteral("breadthfirst") | CaselessLiteral("nodesfirst")|
    CaselessLiteral("edgesfirst")).setResultsName("outputorder")
overlap = (true | false | CaselessLiteral("scale") |
    CaselessLiteral("scalexy") | CaselessLiteral("prism") |
    CaselessLiteral("compress") | CaselessLiteral("vpsc") |
    CaselessLiteral("ipsep")).setResultsName("overlap")
pack = boolean.setResultsName("pack")
packmode = (CaselessLiteral("node") | CaselessLiteral("cluster") |
    CaselessLiteral("graph")).setResultsName("packmode")
pad = real.setResultsName("pad")
page = pointf.setResultsName("page")
pagedir = (
    CaselessLiteral("BL") | CaselessLiteral("BR") | CaselessLiteral("TL") |
    CaselessLiteral("TR") | CaselessLiteral("RB") | CaselessLiteral("RT") |
    CaselessLiteral("LB") | CaselessLiteral("LT")
).setResultsName("pagedir")
quantum = real.setResultsName("quantum")
rank = (CaselessLiteral("same") | CaselessLiteral("min") |
    CaselessLiteral("source") | CaselessLiteral("max") |
    CaselessLiteral("sink")).setResultsName("rank")
rankdir = (CaselessLiteral("TB") | CaselessLiteral("LR") |
    CaselessLiteral("BT") | CaselessLiteral("RL")).setResultsName("rankdir")
ranksep = real.setResultsName("ranksep")
ratio = (real | CaselessLiteral("fill") |
    CaselessLiteral("compress") | CaselessLiteral("expand") |
    CaselessLiteral("auto")).setResultsName("ratio")
remincross = boolean.setResultsName("remincross")
resolution = real.setResultsName("resolution")
root = word.setResultsName("root")
rotate = integer.setResultsName("rotate")
searchsize = integer.setResultsName("searchsize")
sep = integer.setResultsName("sep")
showboxes = (Literal("1") | Literal("2")).setResultsName("showboxes")
size = pointf.setResultsName("size")
splines = boolean.setResultsName("splines")
start = (CaselessLiteral("regular") | CaselessLiteral("self") |
    CaselessLiteral("random")).setResultsName("start")
stylesheet = word.setResultsName("stylesheet")
target = word.setResultsName("target")
truecolor = boolean("truecolor")
URL = word.setResultsName("URL")
viewport = (real.setResultsName("W") + real.setResultsName("H") +
    Optional("Z") +
    (Optional((real.setResultsName("x") + real.setResultsName("y"))) |
    word.setResultsName("N"))).setResultsName("viewport")
voro_margin = real.setResultsName("voro_margin")

graph_attr = [bb, bgcolor, center, charset, clusterrank, colorscheme, comment,
    compound, concentrate, Damping, defaultdist, dim, diredgeconstraints, dpi,
    epsilon, esep, fontcolor, fontname, fontnames, fontpath, fontsize, K,
    label, labeljust, labelloc, landscape, layers, layersep, levelsgap, lp,
    margin, maxiter, mclimit, mindist, mode, model, mosek, nodesep, nojustify,
    normalize, nslimit, nslimit1, ordering, outputorder, overlap, pack,
    packmode, pad, page, pagedir, quantum, rank, rankdir, ranksep, ratio,
    remincross, resolution, root, rotate, searchsize, sep, showboxes, size,
    splines, start, stylesheet, target, truecolor, URL, viewport, voro_margin]

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


if __name__ == "__main__":
    print hexnums

# EOF -------------------------------------------------------------------------
