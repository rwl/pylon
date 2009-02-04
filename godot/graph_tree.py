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
        TreeNode(node_for=[Graph], auto_open=True, children="", label="ID",
            icon_item="graph", rename_me=True),
        TreeNode(node_for=[Graph], auto_open=False, children="subgraphs",
            label="=Subgraphs", add=[Subgraph]),
        TreeNode(node_for=[Graph], auto_open=False, children="clusters",
            label="=Clusters", add=[Cluster]),
        TreeNode(node_for=[Graph], auto_open=True, children="nodes",
            label="=Nodes", add=[Node]),
        TreeNode(node_for=[Graph], auto_open=True, children="edges",
            label="=Edges"),

        TreeNode(node_for=[Subgraph], label="ID", icon_item="subgraph"),
        TreeNode(node_for=[Subgraph], auto_open=False, children="subgraphs",
            label="=Subgraphs", add=[Subgraph]),
        TreeNode(node_for=[Subgraph], auto_open=False, children="clusters",
            label="=Clusters", add=[Cluster]),
        TreeNode(node_for=[Subgraph], auto_open=False, children="nodes",
            label="=Nodes", add=[Node]),
        TreeNode(node_for=[Subgraph], children="edges", label="=Edges"),

        TreeNode(node_for=[Cluster], label="ID", icon_item="cluster"),
        TreeNode(node_for=[Cluster], auto_open=False, children="subgraphs",
            label="=Subgraphs", add=[Subgraph]),
        TreeNode(node_for=[Cluster], auto_open=False, children="clusters",
            label="=Clusters", add=[Cluster]),
        TreeNode(node_for=[Cluster], auto_open=False, children="nodes",
            label="=Nodes", add=[Node]),
        TreeNode(node_for=[Cluster], children="edges", label="=Edges"),

        TreeNode(node_for=[Node], label="ID", icon_item="node"),
        TreeNode(node_for=[Edge], label="ID", icon_item="edge")
    ],
    orientation="vertical", editable=False, hide_root=True
)

# EOF -------------------------------------------------------------------------
