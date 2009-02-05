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

""" Defines a class for writing a Godot graph to file in the Dot language.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from godot.base_graph import BaseGraph

from godot.graph import Graph

from godot.subgraph import Subgraph

from godot.cluster import Cluster

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

GRAPH_ATTRIBUTES = ["Damping", "K", "URL", "bb", "bgcolor", "center",
    "charset", "clusterrank", "colorscheme", "comment", "compound",
    "concentrate", "defaultdist", "dim", "diredgeconstraints", "dpi",
    "epsilon", "esep", "fontcolor", "fontname", "fontnames", "fontpath",
    "fontsize", "label", "labeljust", "labelloc", "landscape", "layers",
    "layersep", "levelsgap", "lp", "margin", "maxiter", "mclimit", "mindist",
    "mode", "model", "mosek", "nodesep", "nojustify", "normalize", "nslimit",
    "nslimit1", "ordering", "outputorder", "overlap", "pack", "packmode",
    "pad", "page", "pagedir", "quantum", "rankdir", "ranksep",
    "ratio", "remincross", "resolution", "root", "rotate", "searchsize",
    "sep", "showboxes", "size", "splines", "start", "stylesheet", "target",
    "truecolor", "viewport", "voro_margin"]

SUBGRAPH_ATTRIBUTES = ["rank"]

CLUSTER_ATTRIBUTES = ["bgcolor", "color", "colorscheme", "fillcolor",
    "fixedsize", "fontcolor", "fontname", "fontsize", "K", "label",
    "labeljust", "labelloc", "lp", "nojustify", "pencolor", "style", "target",
    "tooltip", "URL"]

NODE_ATTRIBUTES = ['URL', 'color', 'colorscheme', 'comment', 'distortion',
    'fillcolor', 'fixedsize', 'fontcolor', 'fontname', 'fontsize', 'group',
    'height', 'image', 'imagescale', 'label', 'label_drawing', 'layer',
    'margin', 'nojustify', 'orientation', 'peripheries', 'pin', 'pos', 'rects',
    'regular', 'root', 'samplepoints', 'shape', 'shapefile', 'showboxes',
    'sides', 'skew', 'style', 'target', 'tooltip', 'vertices', 'width', 'z']

EDGE_ATTRIBUTES = ['URL', 'arrowhead', 'arrowsize', 'arrowtail', 'color',
    'colorscheme', 'comment', 'constraint', 'decorate', 'dir', 'edgeURL',
    'edgehref', 'edgetarget', 'edgetooltip', 'fontcolor', 'fontname',
    'fontsize', 'headURL', 'headclip', 'headhref', 'headlabel', 'headport',
    'headtarget', 'headtooltip', 'href', 'label', 'labelURL', 'labelangle',
    'labeldistance', 'labelfloat', 'labelfontcolor', 'labelfontname',
    'labelfontsize', 'labelhref', 'labeltarget', 'labeltooltip', 'layer',
    'len', 'lhead', 'lp', 'ltail', 'minlen', 'nojustify', 'pos', 'samehead',
    'sametail', 'showboxes', 'style', 'tailURL', 'tailclip', 'tailhref',
    'taillabel', 'tailport', 'tailtarget', 'tailtooltip', 'target', 'tooltip',
    'weight']

#------------------------------------------------------------------------------
#  "write_dot_graph" function:
#------------------------------------------------------------------------------

def _dot_node_str(node, padding="    "):
    """ Returns a string representation of the given node in the Dot language.
    """
    attrs = []
    for trait_name in NODE_ATTRIBUTES:
        value = getattr(node, trait_name)
        if value != node.trait(trait_name).default:
            attrs.append('%s="%s"' % (trait_name, str(value)))

    if attrs:
        attrstr = "[%s]" % ", ".join(attrs)
        return "%s%s %s;\n" % (padding, node.ID, attrstr)
    else:
        return "%s;\n" % node.ID


def _dot_edge_str(edge, padding="    "):
    """ Returns a string representation of the given edge in the Dot language.
    """
    attrs = []
    for trait_name in EDGE_ATTRIBUTES:
        value = getattr(edge, trait_name)
        default = edge.trait(trait_name).default
        # FIXME: Alias/Synced traits default to None.
        if (value != default) and (default is not None):
            valstr = str(value)
            if isinstance(value, basestring):
                valstr = '"%s"' % valstr
            attrs.append('%s=%s' % (trait_name, valstr))

    if attrs:
        attrstr = "[%s]" % ", ".join(attrs)
        return "%s%s%s %s %s%s %s;\n" % \
            (padding, edge.from_node.ID, edge.tailport, edge.conn, \
             edge.to_node.ID, edge.headport, attrstr)
    else:
        return "%s%s%s %s %s%s;\n" % \
            (padding, edge.from_node.ID, edge.tailport, edge.conn, \
             edge.to_node.ID, edge.headport)


def write_dot_graph(graph, level=0, padding="    "):
    """ Returns a string representation of the given graph in the Dot language.
    """
    root_padding = padding * level
    nested_padding = root_padding + padding

    if isinstance(graph, Graph):
        s = ""
        if graph.strict:
            s = "%s%s " % (s, "strict")

        if graph.directed:
            s = "%s%s" % (s, "digraph")
        else:
            s = "%s%s" % (s, "graph")
    else:
        s = "%ssubgraph" % root_padding

    if graph.ID:
        s = "%s %s {\n" % (s, graph.ID)
    else:
        s = "%s {\n" % s

    # Graph attributes.
    if isinstance(graph, Subgraph):
        attrs = SUBGRAPH_ATTRIBUTES
    elif isinstance(graph, Cluster):
        attrs = CLUSTER_ATTRIBUTES
    elif isinstance(graph, Graph):
        attrs = GRAPH_ATTRIBUTES
    else:
        raise ValueError

    for trait_name in attrs:
        value = getattr(graph, trait_name)
        default = graph.trait(trait_name).default
        # FIXME: Alias/Synced traits default to None.
        if (value != default) and (default is not None):
            valstr = str(value)
            if isinstance(value, basestring):
                valstr = '"%s"' % valstr
                s = "%s%s%s=%s;\n" % (s, nested_padding, trait_name, valstr)

    for node in graph.nodes:
        s += _dot_node_str(node, nested_padding)
    for edge in graph.edges:
        s += _dot_edge_str(edge, nested_padding)
    for subgraph in graph.subgraphs:
        s += write_dot_graph(subgraph, level+1)
    for cluster in graph.clusters:
        s += write_dot_graph(cluster, level+1)

    s = "%s%s}\n" % (s, root_padding)

    return s

# EOF -------------------------------------------------------------------------
