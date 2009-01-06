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

""" Tests for parsing Graphviz dot language. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from unittest import TestCase

from godot.dot_parsing import GodotDataParser
from godot.graph import Graph
from godot.dot_parser import DotParser

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
strict digraph G {
    center=true // Bool
    truecolor = 1; // Bool as integer
    remincross=TRUE; // Bool case insensitive
    label="foobar"; // String
    labeljust = r; // Mapped
    lp = "1.5,2.0"; // Point/Tuple
    maxiter=250; // Int
    nodesep=0.1; // Float
    pad = .05 // 0 < Float <= 1
    ranksep="0.6" // Float with quotes
    mode=KK; // Enum
}
"""

node_stmt_graph = r"""
digraph G {
    node1 // Node ID only
    node2 [fixedsize] // Equivalent to fixedsize=true
    node3 [shape=box]; // Assign attribute
    node4 [fixedsize=true, height="0.6", width=.8] // Multiple
    node5 [sides="5" samplepoints=10] // No comma separator
}
"""

edge_stmt_graph = r"""
digraph G {
    node1 -> node2 -> node3;
    node1 -> node3 [label="foo"];
}
"""

fancy_graph = r"""
digraph G {
    size ="4,4";
    main [shape=box];    /* this is a comment */
    main -> parse [weight=8];
    parse -> execute;
    main -> init [style=dotted];
    main -> cleanup;
    execute -> { make_string; printf}
    init -> make_string;
    edge [color=red];    // so is this
    main -> printf [style=bold,label="100 times"];
    make_string [label="make a\nstring"];
    node [shape=box,style=filled,color=".7 .3 1.0"];
    execute -> compare;
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

#        self.parser = GodotDataParser()
        self.parser = DotParser()

    #--------------------------------------------------------------------------
    #  Tests
    #--------------------------------------------------------------------------

    def test_graph_attributes(self):
        """ Test graph attribute value assignment. """

        graph = self.parser.parse_dot_data(graph_attr_graph)

        self.assertTrue(isinstance(graph, Graph))
        self.assertTrue(graph.strict)
        self.assertTrue(graph.directed)
        self.assertEqual(graph.ID, "G")

        self.assertTrue(graph.center) # Bool
        self.assertTrue(graph.truecolor) # Bool as integer
        self.assertTrue(graph.remincross) # Bool case insensitive
        self.assertEqual(graph.label, "foobar") # Str
        self.assertEqual(graph.labeljust, "Right") # Mapped
        self.assertEqual(graph.lp, (1.5, 2.0)) # Tuple
        self.assertEqual(graph.maxiter, 250) # Int
        self.assertEqual(graph.nodesep, 0.1) # Float
        self.assertEqual(graph.pad, 0.05) # 0 < Float <= 1
        self.assertEqual(graph.ranksep, 0.6) # Float with quotes
        self.assertEqual(graph.mode, "KK") # Enum


    def test_node_stmt(self):
        """ Test parsing of node statements. """

        graph = self.parser.parse_dot_data(node_stmt_graph)

        self.assertEqual(len(graph.nodes), 5)
        self.assertTrue(graph.nodes[1].fixedsize)
        self.assertEqual(graph.nodes[2].shape, "box")
        self.assertTrue(graph.nodes[3].fixedsize)
        self.assertEqual(graph.nodes[3].height, 0.6)
        self.assertEqual(graph.nodes[3].width, 0.8)
        self.assertEqual(graph.nodes[4].sides, 5)
        self.assertEqual(graph.nodes[4].samplepoints, 10)


    def test_edge_stmt(self):
        """ Test parsing of edge statements. """

        graph = self.parser.parse_dot_data(edge_stmt_graph)


#    def test_color(self):
#        """ Parsing color attributes """
#
#        graph = self.parser.parse_dot_data(color_graph)
#
#        self.assertTrue(graph is not None)
#        self.assertTrue(graph.bgcolor, (0.0, 0.0, 1.0))


# EOF -------------------------------------------------------------------------
