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

""" Tests for creating, reading, updating and deleting nodes, edges,
subgraphs etc from a graph. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from unittest import TestCase

from godot.graph import Graph
from godot.node import Node

#------------------------------------------------------------------------------
#  "CRUDTestCase" class:
#------------------------------------------------------------------------------

class CRUDTestCase(TestCase):
    """ Tests for object mappings """

    parser = None

    #--------------------------------------------------------------------------
    #  "TestCase" interface
    #--------------------------------------------------------------------------

    def setUp(self):
        """ Prepares the test fixture before each test method is called. """

        self.parser = GodotDataParser()

    #--------------------------------------------------------------------------
    #  Tests:
    #--------------------------------------------------------------------------

    def test_add_node(self):
        """ Adding nodes. """

        g = Graph()
        v = Node(name="node")
        g.nodes.append(v)

        self.assertTrue(len(g.nodes) == 1)
        self.assertTrue(g.nodes[0] == v)


    def test_add_edge(self):
        """ Adding edges. """

        g = Graph()
        v1, v2 = Node(name="v1"), Node(name="v2")
        g.nodes.extend([v1, v2])
        g.edges.append(Edge(v1, v2))


    def test_remove_node(self):
        """ Removing nodes. """

        g = Graph()
        v1, v2 = Node(name="v1"), Node(name="v2")
        g.nodes.extend([v1, v2])
        g.edges.append(Edge(v1, v2))

# EOF -------------------------------------------------------------------------
