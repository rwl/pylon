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

""" Defines a Graphviz dot language parser. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Str, Int, Float, Bool, Color

from dot2tex.dotparsing import \
    DotDataParser, ADD_NODE, ADD_EDGE, ADD_GRAPH_TO_NODE_EDGE, \
    ADD_GRAPH_TO_GRAPH_EDGE, ADD_NODE_TO_GRAPH_EDGE, ADD_NODE_TO_GRAPH_EDGE, \
    ADD_GRAPH_TO_NODE_EDGE, SET_GRAPH_ATTR, SET_DEF_NODE_ATTR, \
    SET_DEF_EDGE_ATTR, SET_DEF_GRAPH_ATTR, ADD_SUBGRAPH

from godot.graph import Graph as GodotGraph
from godot.node import Node as GodotNode
from godot.edge import Edge as GodotEdge

from godot.parsing_util import q_string, real, integer, boolean

#------------------------------------------------------------------------------
#  "GodotDataParser" class:
#------------------------------------------------------------------------------

class GodotDataParser(DotDataParser):
    """ Defines a Graphviz dot language parser that builds a Godot graph """


    def build_graph(self, graph, tokens):
        """ Builds a Godot Graph instance """

        subgraph = None
        for element in tokens:
            cmd = element[0]
            if cmd == ADD_NODE:
                cmd, nodename, opts = element
                print cmd, nodename, opts
                node = GodotNode(name=nodename, **opts)
                graph.nodes.append(node)

            elif cmd == ADD_EDGE:
                cmd, src, dest, opts = element
                print cmd, src, dest, opts
                srcport = destport = ""
                if isinstance(src, tuple):
                    srcport = src[1]
                    src = src[0]
                if isinstance(dest, tuple):
                    destport = dest[1]
                    dest = dest[0]
                edge = GodotEdge(
                    from_node=src, to_node=dest, headport=srcport,
                    tailport=destport, **opts
                )
                graph.edges.append(edge)

#            elif cmd in [ADD_GRAPH_TO_NODE_EDGE,
#            ADD_GRAPH_TO_GRAPH_EDGE,ADD_NODE_TO_GRAPH_EDGE]:
#                cmd, src, dest, opts = element
#                srcport = destport = ""
#                if isinstance(src,tuple):
#                    srcport = src[1]
#                if isinstance(dest,tuple):
#                    destport = dest[1]
#                if not (cmd == ADD_NODE_TO_GRAPH_EDGE):
#                    if cmd == ADD_GRAPH_TO_NODE_EDGE:
#                        src = subgraph
#                    else:
#                        src = prev_subgraph
#                        dest = subgraph
#                else:
#                    dest = subgraph
#
#                edges = graph.add_special_edge(src,dest,srcport,destport,**opts)
#                graph.allitems.extend(edges)

            elif cmd == SET_GRAPH_ATTR:
                graph_attr = element[1]
                print cmd, graph_attr
                for each_key, each_value in graph_attr.items():
                    value = self.coerce_token(graph, each_key, each_value)
                    setattr(graph, each_key, value)

            elif cmd == SET_DEF_NODE_ATTR:
                print cmd, element[1]
#                graph.add_default_node_attr(**element[1])
#                defattr = DotDefaultAttr("node",**element[1])
#                graph.allitems.append(defattr)

            elif cmd == SET_DEF_EDGE_ATTR:
                print cmd, element[1]
#                graph.add_default_edge_attr(**element[1])
#                defattr = DotDefaultAttr("edge",**element[1])
#                graph.allitems.append(defattr)

            elif cmd == SET_DEF_GRAPH_ATTR:
                print cmd, element[1]
#                graph.add_default_graph_attr(**element[1])
#                defattr = DotDefaultAttr("graph",**element[1])
#                graph.allitems.append(defattr)

            elif cmd == ADD_SUBGRAPH:
                cmd, name, elements = element
                print cmd, name, elements
#                if subgraph:
#                    prev_subgraph = subgraph
#                subgraph = graph.add_subgraph(name)
#                subgraph = self.build_graph(subgraph,elements)
#                graph.allitems.append(subgraph)

        return graph


    def build_top_graph(self, tokens):
        """ Builds a Godot Graph instance from parsed data """

        # Get basic graph information
        strict = tokens[0] == "strict"
        graphtype = tokens[1]
        directed = graphtype == "digraph"
        graphname = tokens[2]

        # Build the graph
        graph = GodotGraph(name=graphname, strict=strict, directed=directed)
        self.graph = self.build_graph(graph, tokens[3])


    def coerce_token(self, obj, trait_name, token):
        """ Coerces the token according to the trait type to which it is
        to be assigned.

        """

        trait = obj.trait(trait_name)
        if trait.is_trait_type(Str):
            return token
        elif trait.is_trait_type(Float):
            return float(token)
        elif trait.is_trait_type(Bool):
            if token.lower() in ["true", "false"]:
                return bool(token)
            else:
                return bool(int(token))
        elif trait.is_trait_type(Int):
            return int(token)
#        elif trait.is_trait_type(Color):
#            return token
        else:
            return token


    def _get_node_attr_list_construct(self):
        """ Returns a construct for a node attribute list """

        URL = q_string.setResultsName("URL")
        color = q_string.setResultsName("color")
        colorscheme = q_string.setResultsName("colorscheme")
        comment = q_string.setResultsName("comment")
        distortion = real.setResultsName("distortion")
        fillcolor = q_string.setResultsName("fillcolor")
        fixedsize = bool.setResultsName("fixedsize")
        fontcolor = q_string.setResultsName("fontcolor")
        fontname = q_string.setResultsName("fontname")
        fontsize = real.setResultsName("fontsize")
        group = q_string.setResultsName("group")
        height = real.setResultsName("height")
        image = q_string.setResultsName("image")
        imagescale = q_string.setResultsName("imagescale")
        label = q_string.setResultsName("label")
        layer = q_string.setResultsName("layer")
        margin = real.setResultsName("margin")
        nojustify = boolean.setResultsName("nojustify")
        orientation = real.setResultsName("orientation")
        peripheries = integer.setResultsName("peripheries")
        pin = boolean.setResultsName("pin")
        pos = real.setResultsName("pos")
        rects = real.setResultsName("rects")
        regular = boolean.setResultsName("regular")
        root = integer.setResultsName("root")
        samplepoints = integer.setResultsName("samplepoints")
        shape = q_string.setResultsName("shape")
        shapefile = q_string.setResultsName("shapefile")
        showboxes = boolean.setResultsName("showboxes")
        sides = integer.setResultsName("sides")
        skew = real.setResultsName("skew")
        style = q_string.setResultsName("style")
        target = q_string.setResultsName("target")
        tooltip = q_string.setResultsName("tooltip")
        vertices = real.setResultsName("vertices")
        width = real.setResultsName("width")
        z = real.setResultsName("z")



#------------------------------------------------------------------------------
#  Test graph:
#------------------------------------------------------------------------------

testgraph = r"""
/* Test that the various id types are parsed correctly */
digraph G {

    "aa\\" -> b [label="12"];
}
"""

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == '__main__':
    import pprint

    gp = GodotDataParser()
    tok = gp.parse_dot_data_debug(testgraph)
    #dg = parse_dot_data(testgraph)

    pprint.pprint(tok)
#    print gp.graph
#    gp.graph.configure_traits()

# EOF -------------------------------------------------------------------------
