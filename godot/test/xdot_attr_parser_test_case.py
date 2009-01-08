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

stroke_color = "c 3 -red"
stroke_hex = "c 7 -#2B52CB"
stroke_hsv = "c 17 -0.482 0.714 0.878"

ellipse_draw = "c 5 -black e 27 18 27 18 "
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

    def test_stroke_color(self):
        """ Test parsing of a stroke color attribute. """

        self.parser.parse_xdot_data(stroke_color)
        self.assertEqual(str(self.parser.pen.color), "(255, 0, 0, 255)")
#        self.parser.parse_xdot_data(stroke_hex)
#        self.assertEqual(self.parser.pen.color, "(255, 0, 0, 255)")
#        self.parser.parse_xdot_data(stroke_hsv)
#        self.assertEqual(self.parser.pen.color, "(255, 0, 0, 255)")


#    def test_ellipse(self):
#        """ Test parsing of an unfilled ellipse. """
#
#        components = self.parser.parse_xdot_data(ellipse_draw)


if __name__ == "__main__":
    unittest.main()

# EOF -------------------------------------------------------------------------
