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

from enthought.enable.api import Component

from pyparsing import __version__ as pyparsing_version

from colorsys import hsv_to_rgb

from pyparsing import \
    Literal, CaselessLiteral, Word, Upcase, OneOrMore, ZeroOrMore, Forward, \
    NotAny, delimitedList, oneOf, Group, Optional, Combine, alphas, nums, \
    restOfLine, cppStyleComment, nums, alphanums, printables, empty, \
    quotedString, CharsNotIn, _noncomma, Suppress, nestedExpr, Suppress, Or

from godot.parsing_util import \
    real, integer, minus, quote, equals, colour, nsplit, ToInteger

from godot.component.api import Pen, Ellipse, Polygon, Polyline, BSpline, Text

#------------------------------------------------------------------------------
#  "XdotAttrParser" class:
#------------------------------------------------------------------------------

class XdotAttrParser:
    """ Defines a Graphviz Xdot language parser. """

    parser = None

    pen = None

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self):
        """ Initialises the Xdot output parser. """

        self.parser = self.define_parser()
        self.pen = Pen()

    #--------------------------------------------------------------------------
    #  Public interface:
    #--------------------------------------------------------------------------

    def parse_xdot_data(self, data):
        """ Parses xdot data and returns the associated components. """

        parser = self.parser

#        if pyparsing_version >= "1.2":
#            parser.parseWithTabs()

        tokens = parser.parseString(data)

#        print "COMPONENTS:", tokens

        return tokens#[tok for tok in tokens if isinstance(tok, Component)]

    #--------------------------------------------------------------------------
    #  Define the dot parser
    #--------------------------------------------------------------------------

    def define_parser(self):
        """ Defines xdot grammar.

        @see: http://graphviz.org/doc/info/output.html#d:xdot """

        # Common constructs.
        point = Group(integer.setResultsName("x") +
                      integer.setResultsName("y"))
        n_points = (integer.setResultsName("n") +
            OneOrMore(point).setResultsName("points"))
        n_bytes = Suppress(integer) + Suppress(minus) + \
            Word(printables).setResultsName("b")
        justify = ToInteger(
            Literal("-1") | Literal("0") | Literal("1")
        ).setResultsName("j")

        # Attributes ----------------------------------------------------------

        # Set fill color. The color value consists of the n bytes following
        # the '-'.
        fill = (Literal("C").suppress() + Suppress(integer) + Suppress(minus) +
            colour.setResultsName("color")).setResultsName("fill")

        # Set pen color. The color value consists of the n bytes following '-'.
        stroke = (Literal("c").suppress() + Suppress(integer) +
            Suppress(minus) + colour.setResultsName("color")
        ).setResultsName("stroke")

        # Set font. The font size is s points. The font name consists of the
        # n bytes following '-'.
        font = (Literal("F").suppress() + real.setResultsName("s") +
            n_bytes).setResultsName("font")

        # Set style attribute. The style value consists of the n bytes
        # following '-'. The syntax of the value is the same as specified for
        # a styleItem in style.
        style = (Literal("S").suppress() + n_bytes).setResultsName("style")

        # Shapes --------------------------------------------------------------

        # Filled ellipse ((x-x0)/w)^2 + ((y-y0)/h)^2 = 1
        filled_ellipse = (Literal("E").suppress() +
            integer.setResultsName("x0") + integer.setResultsName("y0") +
            integer.setResultsName("w") + integer.setResultsName("h")
        ).setResultsName("filled_ellipse")

        # Unfilled ellipse ((x-x0)/w)^2 + ((y-y0)/h)^2 = 1
        ellipse = (Literal("e").suppress() +
            integer.setResultsName("x0") + integer.setResultsName("y0") +
            integer.setResultsName("w") + integer.setResultsName("h")
        ).setResultsName("ellipse")

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

        # Text drawn using the baseline point (x,y). The text consists of the
        # n bytes following '-'. The text should be left-aligned (centered,
        # right-aligned) on the point if j is -1 (0, 1), respectively. The
        # value w gives the width of the text as computed by the library.
        text = (Literal("T").suppress() + integer.setResultsName("x") +
            integer.setResultsName("y") + justify +
            integer.setResultsName("w") + n_bytes).setResultsName("text")

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
        value = (Optional(quote).suppress() + OneOrMore(filled_ellipse |
            ellipse | filled_polygon | polygon | polyline | bspline |
            filled_bspline | text | fill | stroke | font | style | image) +
            Optional(quote).suppress()).setResultsName("value")

        # Drawing operation.
#        draw_ = Literal("_draw_") + Suppress(equals) + value
#        # Label drawing.
#        ldraw_ = Literal("_ldraw_") + Suppress(equals) + value
#        # Edge head arrowhead drawing.
#        hdraw_ = Literal("_hdraw_") + Suppress(equals) + value
#        # Edge tail arrowhead drawing.
#        tdraw_ = Literal("_tdraw_") + Suppress(equals) + value
#        # Edge head label drawing.
#        hldraw_ = Literal("_hldraw_") + Suppress(equals) + value
#        # Edge tail label drawing.
#        tldraw_ = Literal("_tldraw_") + Suppress(equals) + value

        # Parse actions.
#        n_points.setParseAction(self.proc_points)

        # Attribute parse actions.
        fill.setParseAction(self.proc_fill_color)
        stroke.setParseAction(self.proc_stroke_color)
        font.setParseAction(self.proc_font)
#        style.setParseAction(self.proc_style)

        # Shape parse actions.
        filled_ellipse.setParseAction(self.proc_filled_ellipse)
        ellipse.setParseAction(self.proc_unfilled_ellipse)
        filled_polygon.setParseAction(self.proc_filled_polygon)
        polygon.setParseAction(self.proc_unfilled_polygon)
        polyline.setParseAction(self.proc_polyline)
        bspline.setParseAction(self.proc_unfilled_bspline)
        filled_bspline.setParseAction(self.proc_filled_bspline)
        text.setParseAction(self.proc_text)
        image.setParseAction(self.proc_image)

        return value

    #--------------------------------------------------------------------------
    #  Parse actions:
    #--------------------------------------------------------------------------

#    def proc_points(self, tokens):
#        """ Returns a list of tuples of the form (x, y). """
#
#        print "N POINTS:", tokens, tokens.keys()
#
#        return tokens["points"]#[(p["x"], p["y"]) for p in tokens["points"]]

    #--------------------------------------------------------------------------
    #  Attribute parse actions:
    #--------------------------------------------------------------------------

    def proc_fill_color(self, tokens):
        """ Sets the pen fill color. """

        self.pen.fill_color = self._proc_color(tokens)

        return []


    def proc_stroke_color(self, tokens):
        """ Sets the pen stroke color. """

        self.pen.color = self._proc_color(tokens)

        return []


    def _proc_color(self, tokens):
        """ The color traits of a Pen instance must be a string of the form
        (r,g,b) or (r,g,b,a) where r, g, b, and a are integers from 0 to 255,
        a wx.Colour instance, an integer which in hex is of the form 0xRRGGBB,
        where RR is red, GG is green, and BB is blue or a valid color name. """

        print "COLOR:", tokens, tokens.keys()

        keys = tokens.keys()
        if "red" in keys: # RGB(A)
            rr, gg, bb = tokens["red"], tokens["green"], tokens["blue"]
            hex2int = lambda h: int(h, 16)
            if "alpha" in keys:
                a = tokens["alpha"]
                c = str((hex2int(rr), hex2int(gg), hex2int(bb), hex2int(a)))
            else:
                c = str((hex2int(rr), hex2int(gg), hex2int(bb)))
        elif "hue" in keys: # HSV
            r, g, b = hsv_to_rgb(tokens["hue"],
                                 tokens["saturation"],
                                 tokens["value"])
            c = str((int(r*255), int(g*255), int(b*255)))
        else:
            c = tokens["color"]

        return c


    def proc_font(self, tokens):
        """ Sets the font. """

        size = int(tokens["s"])
        self.pen.font = "%s %d" % (tokens["b"], size)


    def proc_style(self, tokens):
        """ Sets the style.  At present, the recognized style names are
        "dashed", "dotted", "solid", "invis" and "bold" for nodes and edges,
        and "filled", "diagonals" and "rounded" for nodes only. The styles
        "filled" and "rounded" are recognized for clusters. Additional styles
        are available in device-dependent form."""

        raise NotImplementedError

    #--------------------------------------------------------------------------
    #  Ellipse:
    #--------------------------------------------------------------------------

    def proc_filled_ellipse(self, tokens):
        """ Returns the components of a filled ellipse. """

        return self._proc_ellipse(tokens, filled=True)


    def proc_unfilled_ellipse(self, tokens):
        """ Returns the components of an unfilled ellipse. """

        return self._proc_ellipse(tokens, filled=False)


    def _proc_ellipse(self, tokens, filled):
        """ Returns the components of an ellipse. """

        component = Ellipse(pen=self.pen,
                            x_origin=tokens["x0"],
                            y_origin=tokens["y0"],
                            e_width=tokens["w"],
                            e_height=tokens["h"],
                            filled=filled)

        return component

    #--------------------------------------------------------------------------
    #  Polygon:
    #--------------------------------------------------------------------------

    def proc_filled_polygon(self, tokens):
        """ Returns the components of a filled polygon. """

        return self._proc_polygon(tokens, filled=True)


    def proc_unfilled_polygon(self, tokens):
        """ Returns the components of an unfilled polygon. """

        return self._proc_polygon(tokens, filled=False)


    def _proc_polygon(self, tokens, filled):
        """ Returns the components of a polygon. """

        pts = [(p["x"], p["y"]) for p in tokens["points"]]
        component = Polygon(pen=self.pen, points=pts, filled=filled)

        return component

    #--------------------------------------------------------------------------
    #  Polyline:
    #--------------------------------------------------------------------------

    def proc_polyline(self, tokens):
        """ Returns the components of a polyline. """

        pts = [(p["x"], p["y"]) for p in tokens["points"]]
        component = Polyline(pen=self.pen, points=pts)

        return component

    #--------------------------------------------------------------------------
    #  B-spline (Bezier curve):
    #--------------------------------------------------------------------------

    def proc_filled_bspline(self, tokens):
        """ Returns the components of a filled B-spline. """

        return self._proc_bspline(tokens, filled=True)


    def proc_unfilled_bspline(self, tokens):
        """ Returns the components of an unfilled B-spline. """

        return self._proc_bspline(tokens, filled=False)


    def _proc_bspline(self, tokens, filled):
        """ Returns the components of a B-spline (Bezier curve). """

        pts = [(p["x"], p["y"]) for p in tokens["points"]]
        component = BSpline(pen=self.pen, points=pts, filled=filled)

        return component

    #--------------------------------------------------------------------------
    #  Text:
    #--------------------------------------------------------------------------

    def proc_text(self, tokens):
        """ Returns text components. """

        component = Text(pen=self.pen,
                         text_x=tokens["x"],
                         text_y=tokens["y"],
                         justify=tokens["j"],
                         text_w=tokens["w"],
                         text=tokens["b"])

        return component

    #--------------------------------------------------------------------------
    #  Image:
    #--------------------------------------------------------------------------

    def proc_image(self, tokens):
        """ Returns the components of an image. """

        print "IMAGE:", tokens, tokens.asList(), tokens.keys()

        raise NotImplementedError

# EOF -------------------------------------------------------------------------
