#------------------------------------------------------------------------------
#  Copyright (c) 2009 Richard W. Lincoln
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

""" Defines a representation of a subgraph in Graphviz's dot language.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    HasTraits, Enum, List, Instance, Str

from enthought.traits.ui.api import \
    View, Item, Group, Tabbed

from node import Node
from edge import Edge

#------------------------------------------------------------------------------
#  "Subgraph" class:
#------------------------------------------------------------------------------

class Subgraph(HasTraits):
    """ Defines a representation of a subgraph in Graphviz's dot language.
    """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # Subgraph nodes.
    nodes = List(Instance(Node))

    # Subgraph edges.
    edges = List(Instance(Edge))

    # Parent graph in the graph heirarchy.
    parent = Instance("godot.graph:Graph")

    # Root graph instance.
    root = Instance("godot.graph:Graph")

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
    #  Dot trait definitions.
    #--------------------------------------------------------------------------

    # Rank constraints on the nodes in a subgraph. If rank="same", all nodes
    # are placed on the same rank. If rank="min", all nodes are placed on the
    # minimum rank. If rank="source", all nodes are placed on the minimum rank,
    # and the only nodes on the minimum rank belong to some subgraph whose rank
    # attribute is "source" or "min". Analogous criteria hold for rank="max"
    # and rank="sink". (Note: the minimum rank is topmost or leftmost, and the
    # maximum rank is bottommost or rightmost.)
    rank = Enum("same", "min", "source", "max", "sink",
        desc="rank constraints on the nodes in a subgraph")

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(["rank"], title="Subgraph", id="godot.subgraph",
        buttons=["OK", "Cancel", "Help"], resizable=True)

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    Subgraph().configure_traits()

# EOF +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
