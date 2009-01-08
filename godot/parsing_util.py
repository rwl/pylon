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

import itertools

from pyparsing import \
    TokenConverter, oneOf, string, Literal, Group, Word, Optional, Combine, \
    sglQuotedString, dblQuotedString, restOfLine, nums, removeQuotes, Regex, \
    OneOrMore, hexnums, alphas, alphanums, CaselessLiteral, And, NotAny, Or, \
    White, QuotedString

#from enthought.enable.colors import color_table

from godot.common import color_schemes
from godot.node import node_shapes
from godot.edge import arrow_styles

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
#  "ToTuple" class:
#------------------------------------------------------------------------------

class ToTuple(TokenConverter):
    """ Converter to make token sequence into a tuple. """

    def postParse(self, instring, loc, tokenlist):
        """ Returns a tuple initialised from the token sequence. """

        return tuple(tokenlist)

#------------------------------------------------------------------------------
#  "ToList" class:
#------------------------------------------------------------------------------

class ToList(TokenConverter):
    """ Converter to make token sequence into a list. """

    def postParse(self, instring, loc, tokenlist):
        """ Returns a list initialised from the token sequence. """

        return list(tokenlist)

#------------------------------------------------------------------------------
#  Punctuation:
#------------------------------------------------------------------------------

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
quote = Literal('"')# | Literal("'")

#------------------------------------------------------------------------------
#  Compass point:
#------------------------------------------------------------------------------

north = CaselessLiteral("n")
northeast = CaselessLiteral("ne")
east = CaselessLiteral("e")
southeast = CaselessLiteral("se")
south = CaselessLiteral("s")
southwest = CaselessLiteral("sw")
west = CaselessLiteral("w")
northwest = CaselessLiteral("nw")
middle = CaselessLiteral("c")
underscore = CaselessLiteral("_")

compass_pt = (north | northeast | east | southeast | south | southwest |
    west | northwest | middle | underscore)

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
    Optional(quote).suppress() +
    Combine(Optional(sign) + Word(nums)) +
    Optional(quote).suppress()
).setName("integer")

positive_integer = ToInteger(
    Combine(Optional("+") + Word(nums))
).setName("integer")

negative_integer = ToInteger(
    Combine("-" + Word(nums))
).setName("integer")

# Boolean ---------------------------------------------------------------------

#boolean = ToBoolean(ToInteger(Word("01", exact=1))).setName("bool")
true = CaselessLiteral("True") | Literal("1") #And(integer, NotAny(Literal("0")))
false = CaselessLiteral("False") | Literal("0")
boolean = ToBoolean(true | false).setResultsName("boolean")

# Real ------------------------------------------------------------------------

real = ToFloat(
    Optional(quote).suppress() +
    Combine(
        Optional(sign) +
        (Word(nums) + Optional(decimal_sep + Word(nums))) |
        (decimal_sep + Word(nums)) +
        Optional(oneOf("E e") + Word(nums))
    ) +
    Optional(quote).suppress()
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
word = quoted_string.setName("word") # Word(alphanums)

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

# Graph attributes ------------------------------------------------------------

rect = real.setResultsName("llx") + real.setResultsName("lly") + \
    real.setResultsName("urx") + real.setResultsName("ury")

hex_color = Word(hexnums, exact=2) #TODO: Optional whitespace
rgb = Literal("#") + hex_color.setResultsName("red") + \
    hex_color.setResultsName("green") + hex_color.setResultsName("blue")
rgba = rgb + hex_color.setResultsName("alpha")
hsv = decimal.setResultsName("hue") + decimal.setResultsName("saturation") + \
    decimal.setResultsName("value")
color_name = double_quoted_string | Word(alphas)
colour = rgb | rgba | hsv | color_name

cluster_mode = CaselessLiteral("local") | CaselessLiteral("global") | \
    CaselessLiteral("none")

color_scheme = Or([CaselessLiteral(scheme) for scheme in color_schemes])

esc_string = html_label = quoted_string
lbl_string = esc_string | html_label

point = ToTuple(Optional(quote).suppress() + real.setResultsName("x") + \
    comma.suppress() + real.setResultsName("y") + \
    Optional((comma + real.setResultsName("z"))) + \
    Optional(quote).suppress() + Optional(Literal("!").setResultsName("!")))

pointf = Optional(quote).suppress() + real.setResultsName("x") + \
    comma.suppress() + real.setResultsName("y") + Optional(quote).suppress()

class ToLabelJust(TokenConverter):
    def postParse(self, instring, loc, tokenlist):
        token = tokenlist[0]
        if token == "c":
            return "Cerntre"
        elif token == "r":
            return "Right"
        elif token == "l":
            return "Left"
        else:
            return token

class ToLabelLoc(TokenConverter):
    def postParse(self, instring, loc, tokenlist):
        token = tokenlist[0]
        if token == "b":
            return "Bottom"
        elif token == "t":
            return "Top"
        else:
            return token

bb = rect.setResultsName("bb")
bgcolor = colour.setResultsName("bgcolor")
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
fontcolor = colour.setResultsName("fontcolor")
fontname = word.setResultsName("fontname")
fontnames = (CaselessLiteral("svg") | CaselessLiteral("ps") |
    CaselessLiteral("gd")).setResultsName("fontnames")
fontpath = word.setResultsName("fontpath")
fontsize = real.setResultsName("fontsize")
K = real.setResultsName("K")
label = lbl_string.setResultsName("label")
labeljust = ToLabelJust(CaselessLiteral("c") | CaselessLiteral("r") |
    CaselessLiteral("l")).setResultsName("labeljust")
labelloc = ToLabelLoc(CaselessLiteral("b") |
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

# Node attributes -------------------------------------------------------------

node_shape = Or([CaselessLiteral(shape) for shape in node_shapes])

color = colour.setResultsName("color")
distortion = real.setResultsName("distortion")
fillcolor = colour.setResultsName("fillcolor")
fixedsize = boolean.setResultsName("fixedsize")
group = word.setResultsName("group")
height = real.setResultsName("height")
image = word.setResultsName("image")
imagescale = word.setResultsName("imagescale")
layer = word.setResultsName("layer")
orientation = real.setResultsName("orientation") # TODO: 0.0 < orien < 360.0
peripheries = integer.setResultsName("peripheries")
pin = boolean.setResultsName("pin")
pos = real.setResultsName("pos")
rects = rect.setResultsName("rects")
regular = boolean.setResultsName("regular")
samplepoints = integer.setResultsName("samplepoints")
shape = node_shape.setResultsName("shape")
shapefile = word.setResultsName("shapefile")
sides = integer.setResultsName("sides")
skew = real.setResultsName("skew")
style = ToList(word).setResultsName("style")
tooltip = word.setResultsName("tooltip")
vertices = ToList(pointf).setResultsName("vertices")
width = real.setResultsName("width")
z = real.setResultsName("z")

draw = word.setResultsName("_draw_") # Xdot drawing directive.
ldraw = word.setResultsName("_ldraw_") # Xdot label drawing directive.

node_attr = [color, colorscheme, comment, distortion, fillcolor, fixedsize,
    fontcolor, fontname, fontsize, group, height, image, imagescale, label,
    layer, margin, nojustify, orientation, peripheries, pin, pos, rects,
    regular, root, samplepoints, shape, shapefile, showboxes, sides, skew,
    style, target, tooltip, URL, vertices, width, z] + [draw, ldraw]

# Edge specific attributes ----------------------------------------------------

arrow = Or([CaselessLiteral(arrow_style) for arrow_style in arrow_styles])

arrowhead = arrow.setResultsName("arrowhead")
arrowsize = real.setResultsName("arrowsize")
arrowtail = arrow.setResultsName("arrowtail")
constraint = boolean.setResultsName("constraint")
decorate = boolean.setResultsName("decorate")
dir = (CaselessLiteral("forward") | CaselessLiteral("back") |
    CaselessLiteral("both") | CaselessLiteral("none")).setResultsName("dir")
edgehref = word.setResultsName("edgehref")
edgetarget = word.setResultsName("edgetarget")
edgetooltip = word.setResultsName("edgetooltip")
edgeURL = word.setResultsName("edgeURL")
headclip = boolean.setResultsName("headclip")
headhref = word.setResultsName("headhref")
headlabel = word.setResultsName("headlabel")
headport = word.setResultsName("headport")
headtarget = word.setResultsName("headtarget")
headtooltip = word.setResultsName("headtooltip")
headURL = word.setResultsName("headURL")
href = word.setResultsName("href")
labelangle = real.setResultsName("labelangle")
labeldistance = real.setResultsName("labeldistance")
labelfloat = boolean.setResultsName("labelfloat")
labelfontcolor = colour.setResultsName("labelfontcolor")
labelfontname = word.setResultsName("labelfontname")
labelfontsize = real.setResultsName("labelfontsize")
labelhref = word.setResultsName("labelhref")
labeltarget = word.setResultsName("labeltarget")
labeltooltip = word.setResultsName("labeltooltip")
labelURL = word.setResultsName("labelURL")
lenn = real.setResultsName("len")
lhead = word.setResultsName("lhead")
ltail = word.setResultsName("ltail")
minlen = integer.setResultsName("minlen")
samehead = word.setResultsName("samehead")
sametail = word.setResultsName("sametail")
tailclip = boolean.setResultsName("tailclip")
tailhref = word.setResultsName("tailhref")
taillabel = word.setResultsName("taillabel")
tailport = word.setResultsName("tailport")
tailtarget = word.setResultsName("tailtarget")
tailtooltip = word.setResultsName("tailtooltip")
tailURL = word.setResultsName("tailURL")
weight = real.setResultsName("weight")

# Xdot drawing directives.
hdraw = word.setResultsName("_hdraw_") # Edge head arrowhead drawing.
tdraw = word.setResultsName("_tdraw_") # Edge tail arrowhead drawing.
hldraw = word.setResultsName("_hldraw_") # Edge head label drawing.
tldraw = word.setResultsName("_tldraw_") # Edge tail label drawing.

edge_attr = [arrowhead, arrowsize, arrowtail, color, colorscheme, comment,
    constraint, decorate, dir, edgehref, edgetarget, edgetooltip, edgeURL,
    fontcolor, fontname, fontsize, headclip, headhref, headlabel, headport,
    headtarget, headtooltip, headURL, href, label, labelangle, labeldistance,
    labelfloat, labelfontcolor, labelfontname, labelfontsize, labelhref,
    labeltarget, labeltooltip, labelURL, layer, lenn, lhead, lp, ltail, minlen,
    nojustify, pos, samehead, sametail, showboxes, style, tailclip, tailhref,
    taillabel, tailport, tailtarget, tailtooltip, tailURL, target, tooltip,
    URL, weight] + [draw, ldraw, hdraw, tdraw, hldraw, tldraw]

# All dot attributes ----------------------------------------------------------

d = {} # Remove duplicated constructs.
for x in (graph_attr + node_attr + edge_attr): d[x]=x
all_attr = d.values()

#all_attr = graph_attr + node_attr + edge_attr
#reduce(lambda l, x: x not in l and l.append(x) or l, all_attr, [])

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

    return [xy for xy in itertools.izip(*[iter(seq)]*n)]

#------------------------------------------------------------------------------
#  "windows" function:
#------------------------------------------------------------------------------

def windows(iterable, length=2, overlap=0, padding=True):
    """ Code snippet from Python Cookbook, 2nd Edition by David Ascher,
    Alex Martelli and Anna Ravenscroft; O'Reilly 2005

    Problem: You have an iterable s and need to make another iterable whose
    items are sublists (i.e., sliding windows), each of the same given length,
    over s' items, with successive windows overlapping by a specified amount.

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
    l = [1,2,3]
    for j, k in windows(l, length=2, overlap=1, padding=False):
        print j, k

# EOF -------------------------------------------------------------------------
