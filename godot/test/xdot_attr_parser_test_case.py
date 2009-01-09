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

""" Tests for parsing Graphviz Xdot output attributes. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import unittest

from godot.xdot_attr_parser import XdotAttrParser
from godot.component.api import Ellipse, Polygon

fill_color = "C 4 -blue"
fill_rgb = "C 7 -#000080"
fill_rgba = "C 9 -#00008080"
fill_hsv = "C 17 -0.482 0.714 0.878"

font_default = "F 10.000000 5 -Arial"

stroke_color = "c 3 -red"
stroke_rgb = "c 7 -#008000"
stroke_rgba = "c 9 -#00800080"
stroke_hsv = "c 17 -0.482 0.714 0.878"

style_single = "S 6 -filled"
style_list = "S 4 -bold S 6 -dotted"

unfilled_ellipse = "e 27 18 27 18 "
filled_ellipse = "E 27 18 27 18 "

filled_polygon = "P 8 54 11 54 25 38 36 16 36 0 25 0 11 16 0 38 0"
unfilled_polygon = "p 5 54 24 27 36 0 24 10 3 44 3"

polyline_three = "L 3 47 55 27 55 27 63"

foo_ldraw = "F 14.000000 11 -Times-Roman c 5 -black T 27 13 0 20 3 -foo "

#------------------------------------------------------------------------------
#  "XDotAttrParserTestCase" class:
#------------------------------------------------------------------------------

class XdotAttrParserTestCase(unittest.TestCase):
    """ Tests for the Xdot attribute parser. """

    parser = None

    #--------------------------------------------------------------------------
    #  "TestCase" interface:
    #--------------------------------------------------------------------------

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        self.parser = XdotAttrParser()

    #--------------------------------------------------------------------------
    #  Tests:
    #--------------------------------------------------------------------------

    def test_fill_color(self):
        """ Test parsing of a fill color attribute. """

        parser = self.parser

        parser.parse_xdot_data(fill_color)
        self.assertEqual(str(parser.pen.fill_color), "(0, 0, 255, 255)")
        parser.parse_xdot_data(fill_rgb)
        self.assertEqual(str(parser.pen.fill_color), "(0, 0, 128, 255)")
        parser.parse_xdot_data(fill_rgba)
        self.assertEqual(str(parser.pen.fill_color), "(0, 0, 128, 128)")
        parser.parse_xdot_data(fill_hsv)
        self.assertEqual(str(parser.pen.fill_color), "(64, 223, 206, 255)")


    def test_stroke_color(self):
        """ Test parsing of a stroke color attribute. """

        parser = self.parser

        parser.parse_xdot_data(stroke_color)
        self.assertEqual(str(parser.pen.color), "(255, 0, 0, 255)")
        parser.parse_xdot_data(stroke_rgb)
        self.assertEqual(str(parser.pen.color), "(0, 128, 0, 255)")
        parser.parse_xdot_data(stroke_rgba)
        self.assertEqual(str(parser.pen.color), "(0, 128, 0, 128)")
        parser.parse_xdot_data(stroke_hsv)
        self.assertEqual(str(parser.pen.color), "(64, 223, 206, 255)")


    def test_font(self):
        """ Test font attribute parsing. """

        parser = self.parser

        parser.parse_xdot_data(font_default)
        self.assertEqual(str(parser.pen.font), "10 point Arial")


#    def test_style(self):
#        """ Test style attribute parsing. """
#
#        parser = self.parser
#        parser.parse_xdot_data(style_single)
#        parser.parse_xdot_data(style_list)


    def test_ellipse(self):
        """ Test ellipse directive parsing. """

        parser = self.parser

        components = parser.parse_xdot_data(filled_ellipse)
        ellipse = components[0]

        self.assertTrue(isinstance(ellipse, Ellipse))
        self.assertEqual(ellipse.x_origin, 27)
        self.assertEqual(ellipse.y_origin, 18)
        self.assertEqual(ellipse.e_width, 27)
        self.assertEqual(ellipse.e_height, 18)
        self.assertTrue(ellipse.filled)

        components = parser.parse_xdot_data(unfilled_ellipse)
        ellipse = components[0]
        self.assertFalse(ellipse.filled)


    def test_polygon(self):
        """ Test polygon directive parsing. """

        parser = self.parser

        components = parser.parse_xdot_data(filled_polygon)
        polygon = components[0]

        self.assertTrue(isinstance(polygon, Polygon))
        self.assertEqual(len(polygon.points), 8)
        self.assertTrue(polygon.filled)

        components = parser.parse_xdot_data(unfilled_polygon)
        polygon = components[0]
        self.assertFalse(polygon.filled)


if __name__ == "__main__":
    unittest.main()

# EOF -------------------------------------------------------------------------
