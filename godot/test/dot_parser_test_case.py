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

""" Tests for parsing Graphviz dot language """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from unittest import TestCase

from godot.dot_parsing import GodotDataParser

#------------------------------------------------------------------------------
#  Test graph:
#------------------------------------------------------------------------------

testgraph = r"""
/* Test that the various id types are parsed correctly */
digraph G {

    "aa\\" -> b [label="12"];
}
"""

graph_attr_graph = r"""
digraph G {
    center=true // Bool
    truecolor=0 // Bool as integer
    remincross=TRUE // Bool case insensitive
    label="foobar"; // String
//    labeljust=r; // Mapped
//    lp=(1.5, 2.0); // Point/Tuple
    maxiter=250; // Int
    nodesep=.05; // Float
    mode=KK; // Enum
}
"""

color_graph = r"""
digraph G {
    bgcolor="blue"; // string
    n1 [color="0.650 0.700 0.700"]; // HSV
    n2 [color="#40e0d0"]; // RGB
    n1 -> n2 [color="#a0522d92"]; // RGBA
}
"""

#------------------------------------------------------------------------------
#  "DotParserTestCase" class:
#------------------------------------------------------------------------------

class DotParserTestCase(TestCase):
    """ Tests for object mappings """

    parser = None

    #--------------------------------------------------------------------------
    #  "TestCase" interface
    #--------------------------------------------------------------------------

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        self.parser = GodotDataParser()

    #--------------------------------------------------------------------------
    #  Tests
    #--------------------------------------------------------------------------

    def test_graph_attributes(self):
        """ Parsing graph attributes """

        graph = self.parser.parse_dot_data(graph_attr_graph)

        self.assertTrue(graph is not None)
        self.assertTrue(graph.center) # Bool
        self.assertFalse(graph.truecolor) # Bool as integer
        self.assertTrue(graph.remincross) # Bool case insensitive
#        self.assertEqual(graph.label, "foobar") # Str
#        self.assertEqual(graph.labeljust, "r") # Mapped
#        self.assertEqual(graph.lp, (1.5, 2.0)) # Tuple
#        self.assertEqual(graph.maxiter, 250) # Int
#        self.assertEqual(graph.nodesep, 0.05) # Float
#        self.assertEqual(graph.mode, "KK") # Enum


#    def test_color(self):
#        """ Parsing color attributes """
#
#        graph = self.parser.parse_dot_data(color_graph)
#
#        self.assertTrue(graph is not None)
#        self.assertTrue(graph.bgcolor, (0.0, 0.0, 1.0))


# EOF -------------------------------------------------------------------------
