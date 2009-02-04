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

""" Defines a tree editor for Godot graphs. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.ui.api import TreeEditor, TreeNode, View, Item

from godot.api import Graph, Subgraph, Cluster, Node, Edge

#------------------------------------------------------------------------------
#  Graph tree editor:
#------------------------------------------------------------------------------

no_view = View()

graph_tree_editor = TreeEditor(
    nodes = [
        TreeNode(node_for=[Graph], auto_open=True, children="", label="ID"),
        TreeNode(node_for=[Graph], auto_open=True, children="subgraphs",
            label="=Subgraphs", add=[Subgraph]),
        TreeNode(node_for=[Graph], auto_open=True, children="nodes",
            label="=Nodes", add=[Node]),

        TreeNode(node_for=[Subgraph], label="ID"),
        TreeNode(node_for=[Subgraph], auto_open=False, children="subgraphs",
            label="=Subgraphs", add=[Subgraph]),
        TreeNode(node_for=[Subgraph], auto_open=False, children="nodes",
            label="=Nodes", add=[Node]),

        TreeNode(node_for=[Node], label="ID"),
    ],
    orientation="horizontal", editable=False
)

# EOF -------------------------------------------------------------------------
