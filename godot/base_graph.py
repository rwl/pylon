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

""" Defines a base class for many graphs. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api \
    import HasTraits, Str, List, Instance, Bool, Property, Constant, ReadOnly

from node import Node
from edge import Edge
from common import id_trait, Alias

#------------------------------------------------------------------------------
#  "BaseGraph" class:
#------------------------------------------------------------------------------

class BaseGraph(HasTraits):
    """ Defines a representation of a graph in Graphviz's dot language """

    #--------------------------------------------------------------------------
    #  Trait definitions.
    #--------------------------------------------------------------------------

    # Optional unique identifier.
    ID = id_trait

    # Synonym for ID.
    name = Alias("ID", desc="synonym for ID") # Used by InstanceEditor

    # Main graph nodes.
    nodes = List(Instance(Node))

    # Graph edges.
    edges = List(Instance(Edge))

    # Separate layout regions.
    subgraphs = List(Instance("godot.subgraph.Subgraph"))

    # Clusters are encoded as subgraphs whose names have the prefix 'cluster'.
    clusters = List(Instance("godot.cluster.Cluster"))

    # Tab width to use for string representation.
    padding = Str("    ")

    #--------------------------------------------------------------------------
    #  Xdot trait definitions:
    #--------------------------------------------------------------------------

    # For a given graph object, one will typically a draw directive before the
    # label directive. For example, for a node, one would first use the
    # commands in _draw_ followed by the commands in _ldraw_.
    _draw_ = Str(desc="xdot drawing directive")

    # Label draw directive.
    _ldraw_ = Str(desc="xdot label drawing directive")

    #--------------------------------------------------------------------------
    #  Trait initialisers:
    #--------------------------------------------------------------------------

    def __len__(self):
        """ Return the order of the graph when requested by len().

        @rtype:  number
        @return: Size of the graph.

        """

        return len(self.nodes)


    def __iter__(self):
        """ Return a iterator passing through all nodes in the graph.

        @rtype:  iterator
        @return: Iterator passing through all nodes in the graph.

        """

        for each in self.nodes:
            yield each


    def __getitem__(self, node):
        """ Return a iterator passing through all neighbours of the given node.

        @rtype:  iterator
        @return: Iterator passing through all neighbours of the given node.

        """

        for each_edge in self.edges:
            if (each_edge.from_node == node) or (each_edge.to_node == node):
                yield each_edge

# EOF -------------------------------------------------------------------------
