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

""" Defines a Graphviz xdot language parser.

References:
    XDot by Jose.R.Fonseca (http://code.google.com/p/jrfonseca/wiki/XDot)

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from pyparsing import __version__ as pyparsing_version

from pyparsing import \
    Literal, CaselessLiteral, Word, Upcase, OneOrMore, ZeroOrMore, Forward, \
    NotAny, delimitedList, oneOf, Group, Optional, Combine, alphas, nums, \
    restOfLine, cppStyleComment, nums, alphanums, printables, empty, \
    quotedString, ParseException, ParseResults, CharsNotIn, _noncomma, \
    dblQuotedString, QuotedString, ParserElement, Suppress, Regex, \
    removeQuotes, nestedExpr, Suppress, Or

from godot.parsing_util import real, integer, minus, quote, equals


xdot_graph = """
graph {
    node [label="\N"];
    graph [bb="0,0,54,36",
        _draw_="c 5 -white C 5 -white P 4 0 0 0 36 54 36 54 0 ",
        xdotversion="1.2"];
    foo [pos="27,18", width="0.75", height="0.50",
        _draw_="c 5 -black e 27 18 27 18 ",
        _ldraw_="F 14.000000 11 -Times-Roman c 5 -black T 27 13 0 20 3 -foo "];
}
"""

#------------------------------------------------------------------------------
#  "XDotParser" class:
#------------------------------------------------------------------------------

class XDotParser:
    """ Defines a Graphviz xdot language parser. """

    parser = None

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self):
        self.parser = self.define_parser()

    #--------------------------------------------------------------------------
    #  Public interface:
    #--------------------------------------------------------------------------

    def parse_dot_data(self, data):
        """ Parses dot data and returns a godot.Graph instance. """

        parser = self.parser

        if pyparsing_version >= "1.2":
            parser.parseWithTabs()

#        self.graph = graph = Graph()

        tokens = parser.parseString(data)
        graph = tokens[0]

#        print "TOKENS:", tokens

        return graph

    #--------------------------------------------------------------------------
    #  Define the dot parser
    #--------------------------------------------------------------------------

    def define_parser(self):
        """ Defines xdot grammar.

        @see: http://graphviz.org/doc/info/output.html#d:xdot """

        # Filled ellipse ((x-x0)/w)^2 + ((y-y0)/h)^2 = 1
        filled_ellipse = (Literal("E") + integer.setResultsName("x0") +
            integer.setResultsName("y0") + integer.setResultsName("w") +
            integer.setResultsName("h")).setResultsName("filled_ellipse")

        # Unfilled ellipse ((x-x0)/w)^2 + ((y-y0)/h)^2 = 1
        ellipse = (Literal("e") + integer.setResultsName("x0") +
            integer.setResultsName("y0") + integer.setResultsName("w") +
            integer.setResultsName("h")).setResultsName("ellipse")

        point = (integer.setName("x") + integer.setName("y"))
        n_points = (integer.setResultsName("n") +
            OneOrMore(point).setResultsName("points"))

        # Filled polygon using the given n points.
        filled_polygon = (Literal("P").suppress() +
            n_points).setResultsName("filled_polygon")

        # Unfilled polygon using the given n points.
        polygon = (Literal("p").suppress() +
            n_points).setResultsName("polygon")

        # Polyline using the given n points.
        polyline = (Literal("L").suppress() +
            n_points).setResultsName("polyline")

        # B-spline using the given n control points.
        bspline = (Literal("B").suppress() +
            n_points).setResultsName("bspline")

        # Filled B-spline using the given n control points.
        filled_bspline = (Literal("b").suppress() +
            n_points).setResultsName("filled_bspline")

        n_bytes = Suppress(minus) + Word(alphanums).setResultsName("b")

        # Text drawn using the baseline point (x,y). The text consists of the
        # n bytes following '-'. The text should be left-aligned (centered,
        # right-aligned) on the point if j is -1 (0, 1), respectively. The
        # value w gives the width of the text as computed by the library.
        text = (Literal("T").suppress() + integer.setResultsName("x") +
            integer.setResultsName("y") + justification +
            integer.setResultsName("w") + integer.setResultsName("n") +
            n_bytes).setResultsName("text")

        # Set fill color. The color value consists of the n bytes following
        # the '-'.
        fill = (Literal("C").suppress() + n_bytes).setResultsName("fill")

        # Set pen color. The color value consists of the n bytes following '-'.
        pen = (Literal("c").suppress() + n_bytes).setResultsName("pen")

        # Set font. The font size is s points. The font name consists of the
        # n bytes following '-'.
        font = (Literal("F").suppress() + integer.setResultsName("s") +
            n_bytes).setResultsName("font")

        # Set style attribute. The style value consists of the n bytes
        # following '-'. The syntax of the value is the same as specified for
        # a styleItem in style.
        style = (Literal("S").suppress() + n_bytes).setResultsName("style")

        # Externally-specified image drawn in the box with lower left corner
        # (x,y) and upper right corner (x+w,y+h). The name of the image
        # consists of the n bytes following '-'. This is usually a bitmap
        # image. Note that the image size, even when converted from pixels to
        # points, might be different from the required size (w,h). It is
        # assumed the renderer will perform the necessary scaling.
        image = (Literal("I").suppress() + integer.setResultsName("x") +
            integer.setResultsName("y") + integer.setResultsName("w") +
            integer.setResultsName("h") + n_bytes).setResultsName("image")

        # The value of the drawing attributes consists of the concatenation of
        # some (multi-)set of the 13 rendering or attribute operations.
        value = (Optional(quote).suppress() + filled_ellipse | ellipse |
            filled_polygon | polygon | polyline | bspline | filled_bspline |
            text | fill | pen | font | style | image).setResultsName("value")

        # Drawing operation.
        draw_ = Literal("_draw_") + Suppress(equals) + value
        # Label drawing.
        ldraw_ = Literal("_ldraw_") + Suppress(equals) + value
        # Edge head arrowhead drawing.
        hdraw_ = Literal("_hdraw_") + Suppress(equals) + value
        # Edge tail arrowhead drawing.
        tdraw_ = Literal("_tdraw_") + Suppress(equals) + value
        # Edge head label drawing.
        hldraw_ = Literal("_hldraw_") + Suppress(equals) + value
        # Edge tail label drawing.
        tldraw_ = Literal("_tldraw_") + Suppress(equals) + value

# EOF -------------------------------------------------------------------------
