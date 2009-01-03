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
    OneOrMore, hexnums, alphas, alphanums, CaselessLiteral

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

#------------------------------------------------------------------------------
#  Convenience pyparsing constructs
#------------------------------------------------------------------------------

decimal_sep = "."

sign = oneOf("+ -")

scolon = Literal(";").suppress()

string = Word(alphanums)

matlab_comment = Group(Literal('%') + restOfLine).suppress()
psse_comment = Literal('@!') + Optional(restOfLine)

# part of printables without decimal_sep, +, -
special_chars = string.replace(
    '!"#$%&\'()*,./:;<=>?@[\\]^_`{|}~', decimal_sep, ""
)

#boolean = ToBoolean(ToInteger(Word("01", exact=1))).setName("bool")
true = CaselessLiteral("True") | And(integer, NotAny(Literal("0")))
false = CaselessLiteral("False") | Literal("0")
boolean = ToBoolean(true | false).setResultsName("boolean")

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

# TODO: Positive real number between zero and one.
decimal = real

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

rect = real.setResultsName("llx") + real.setResultsName("lly") + \
    real.setResultsName("urx") + real.setResultsName("ury")

hex_color = Word(hexnums, exact=2) #TODO: Optional whitespace
rgb = Literal("#") + hex_color.setResultsName("red") + \
    hex_color.setResultsName("green") + hex_color.setResultsName("blue")
rgba = rgb + hex_color.setResultsName("alpha")
hsv = decimal.setResultsName("hue") + decimal.setResultsName("saturation") + \
    decimal.setResultsName("value")
color_name = Word(alphas)
color = rgb | rgba | hsv | color_name

cluster_mode = Literal("local") | Literal("global") | Literal("none")

color_scheme = Or([Literal(scheme) for scheme in color_schemes])

bb = rect.setResultsName("bb")
bgcolor = color.setResultsName("bgcolor")
center = boolean.setResultsName("center")
charset = string.setResultsName("charset")
clusterrank = cluster_mode.setResultsName("clusterrank")
colorscheme = color_scheme.setResultsName("colorscheme")
comment = string.setResultsName("comment")
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
fontcolor = fontcolor_trait
fontname = fontname_trait
fontnames = Enum(
    "svg", "ps", "gd", label="Font names",
    desc="how basic fontnames are represented in SVG output"
)
fontpath = List(Directory, label="Font path")
fontsize = fontsize_trait
K = Float(0.3, desc="spring constant used in virtual physical model")
label = label_trait
labeljust = Trait(
    "c", {"Centre": "c", "Right": "r", "Left": "l"},
    desc="justification for cluster labels", label="Label justification"
)
labelloc = Trait(
    "b", {"Bottom": "b", "Top":"t"},
    desc="placement of graph and cluster labels",
    label="Label location"
)
landscape = Bool(False, desc="rendering in landscape mode")
layers = Str(desc="a linearly ordered list of layer names")
layersep = Enum(
    ":\t", "\t", " ", label="Layer separation",
    desc="separator characters used to split layer names"
)
levelsgap = Float(
    0.0, desc="strictness of level constraints in neato",
    label="Levels gap"
)
lp = point_trait
margin = Either(Float, pointf_trait, desc="x and y margins of canvas")
maxiter = Int(desc="number of iterations used", label="Maximum iterations")
mclimit = Float(
    1.0, desc="Multiplicative scale factor used to alter the MinQuit "
    "(default = 8) and MaxIter (default = 24) parameters used during "
    "crossing minimization", label="Multiplicative scale factor"
)
mindist = Float(
    1.0, desc="minimum separation between all nodes",
    label="Minimum separation"
)
mode = Enum(
    "major", "KK", "heir", "ipsep",
    desc="Technique for optimizing the layout"
)
model = Enum(
    "shortpath", "circuit", "subset",
    desc="how the distance matrix is computed for the input graph"
)
mosek = Bool(False, desc="solve the ipsep constraints with MOSEK")
nodesep = Float(
    0.25, desc="minimum space between two adjacent nodes in the same rank",
    label="Node separation"
)
nojustify = nojustify_trait
normalize = Bool(
    False, desc="If set, normalize coordinates of final layout so that "
    "the first point is at the origin, and then rotate the layout so that "
    "the first edge is horizontal"
)
nslimit = Float(
    desc="iterations in network simplex applications",
    label="x-coordinate limit"
)
nslimit1 = Float(
    desc="iterations in network simplex applications",
    label="Ranking limit"
)
ordering = Enum(
    "out", "in", desc="If 'out' for a graph G, and n is a node in G, then "
    "edges n->* appear left-to-right in the same order in which they are "
    "defined. If 'in', the edges *->n appear left-to-right in the same "
    "order in which they are defined for all nodes n."
)
outputorder = Enum(
    "breadthfirst", "nodesfirst", "edgesfirst",
    desc="order in which nodes and edges are drawn",
    label="Output order"
)
overlap = Enum(
    "True", "False", "scale", "scalexy", "prism", "compress", "vpsc", "ipsep",
    desc="determines if and how node overlaps should be removed"
)
pack = Bool #Either(
#        Bool, Int, desc="If true, each connected component of the graph is "
#        "laid out separately, and then the graphs are packed tightly"
#    )
packmode = Enum(
    "node", "cluster", "graph", label="Pack mode",
    desc="granularity and method used for packing"
)
# the boundary of the drawn region.
pad = Float(
    0.0555, desc="how much to extend the drawing area around the minimal "
    "area needed to draw the graph"
)
page = pointf_trait
pagedir = Enum(
    "BL", "BR", "TL", "TR", "RB", "RT", "LB", "LT",
    desc="If the page attribute is set and applicable, this attribute "
    "specifies the order in which the pages are emitted",
    label="Page direction"
)
quantum = Float(
    0.0, desc="If quantum > 0.0, node label dimensions will be rounded to "
    "integral multiples of the quantum."
)
rank = Enum(
    "same", "min", "source", "max", "sink",
    desc="rank constraints on the nodes in a subgraph"
)
rankdir = Enum(
    "TB", "LR", "BT", "RL", desc="direction of graph layout",
    label="Rank direction"
)
ranksep = Float(
    0.5, desc="In dot, this gives the desired rank separation.  In twopi, "
    "specifies radial separation of concentric circles",
    label="Rank separation"
)
ratio = Either(
    Float, Enum("fill", "compress", "expand", "auto"),
    desc="aspect ratio (drawing height/drawing width) for the drawing"
)
remincross = Bool(
    False, desc="If true and there are multiple clusters, run cross "
    "minimization a second", label="Re-cross minimization"
)
resolution = Alias("dpi", desc="a synonym for the dpi attribute")
root = root_trait
rotate = Range(0, 360, desc="drawing orientation")
searchsize = Int(
    30, desc="maximum number of edges with negative cut values to search "
    "when looking for one with minimum cut value", label="Search size"
)
sep = Int(
    4, desc="Fraction to increase polygons (multiply coordinates by "
    "1 + sep) for purposes of determining overlap", label="Separation"
)
showboxes = showboxes_trait
size = pointf_trait
splines = Enum(
    "True", "False", "", desc="how, and if, edges are represented"
)
start = start_trait
stylesheet = Str(
    desc="URL or pathname specifying an XML style sheet",
    label="Style sheet"
)
target = target_trait
truecolor = Bool(True)
URL = Str(
    desc="hyperlinks incorporated into device-dependent output",
    label="URL"
)
viewport = Tuple(Float, Float, Float, Float, Float)
#    Either(
#        Tuple(Float, Float, Float, Float, Float),
#        Tuple(Float, Float, Float, Str),
#        desc="clipping window on final drawing"
#    )

voro_margin = Float(
    0.05, desc="Factor to scale up drawing to allow margin for expansion "
    "in Voronoi technique. dim' = (1+2*margin)*dim.",
    label="Voronoi margin"
)

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
