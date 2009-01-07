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
/* This is a
   multiple line
   comment. */
strict digraph G {
    /* C++-style comment */
    # C preprocessor output
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
    node1 -> node2
    node1 -> node3 [label="foo"]; // Line properties
    node2 -> node3 -> node4 -> node1; // Multiple edges
    node2 -> node4 -> node5 [color="blue"] // Multiple blue edges
}
"""

cluster_graph = r"""
digraph G {
    {n1}
}
"""
#    subgraph cluster_small {
#        a -> b;
#        label=small;
#    }
#    subgraph cluster_big {
#        p -> q -> r -> s -> t;
#        label=big;
#        t -> p;
#    }
#    t -> a;
#    b -> q;
#}
#"""

attr_stmt_graph = r"""
/* If a default attribute is defined using a node, edge, or graph statement,
   or by an attribute assignment not attached to a node or edge, any object of
   the appropriate type defined afterwards will inherit this attribute value.
   This holds until the default attribute is set to a new value, from which
   point the new value is used. */
graph G {
    node [shape=box label="foo"]
    n1
    n2
    node [shape=circle label="bar"]
    n3
    n4
    edge [color="red"]
    n1 -- n2
    n2 -- n3
    edge [color="green"]
    n3 -- n4
    n4 -- n1 [color="blue"]
    graph [rankdir=LR nodesep=0]
    subgraph cluster1 {a -- b}
    n2 -- b
    subgraph cluster_big {p -- q -- r}
    n4 -- q
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

records_graph = r"""
/* These nodes represent recursive lists of fields, which are drawn as
   alternating horizontal and vertical rows of boxes. The recursive structure
   is determined by the node's label, which has the following schema:

  rlabel : field ( '|' field )*
  field : boxLabel | ''rlabel''
  boxLabel : ['<'string'>'] [string]

   Literal braces, vertical bars and angle brackets must be escaped. Spaces are
   interpreted as separators between tokens, so they must be escaped if they
   are to appear literally in the text. The first string in a boxLabel gives a
   name to the field, and serves as a port name for the box. The second string
   is used as a label for the field; it may contain the same escape sequences
   as multi-line labels.

   References:
       E. Gansner, E. Koutsofios and S. North, "Drawing graphs with dot", dot
       User's Manual, graphviz-X.XX.tar.gz, January 26, 2006
*/
digraph structs {
node [shape=record];
    struct1 [shape=record,label="<f0> left|<f1> mid\ dle|<f2> right"];
    struct2 [shape=record,label="<f0> one|<f1> two"];
    struct3 [shape=record,label="hello\nworld |{ b |{c|<here> d|e}| f}| g | h"];
    struct1 -> struct2;
    struct1 -> struct3;
}
"""

port_graph = r"""
digraph G {
    node [shape=record];
    a [label = "<f0> foo | x | <f1> bar"];
    b [label = "a | { <f0> foo | x | <f1> bar } | b"];
    a:f0 -> b:f1
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

        self.assertEqual(len(graph.edges), 7)

        self.assertEqual(graph.edges[0].from_node.ID, "node1")
        self.assertEqual(graph.edges[0].to_node.ID, "node2")

        self.assertEqual(graph.edges[1].label, "foo")

        self.assertEqual(graph.edges[5].color, "blue")
        self.assertEqual(graph.edges[6].color, "blue")


    def test_subgraph(self):
        """ Test parsing of subgraph statements. """

        graph = self.parser.parse_dot_data(cluster_graph)


#    def test_attr_stmt(self):
#        """ Test parsing of default attribute statements. """
#
#        graph = self.parser.parse_dot_data(attr_stmt_graph)


#    def test_color(self):
#        """ Parsing color attributes """
#
#        graph = self.parser.parse_dot_data(color_graph)
#
#        self.assertTrue(graph is not None)
#        self.assertTrue(graph.bgcolor, (0.0, 0.0, 1.0))


# EOF -------------------------------------------------------------------------
