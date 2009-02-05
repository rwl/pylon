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

""" Defines a representation of a cluster subgraph in Graphviz's dot language.
    Clusters are encoded as subgraphs whose names have the prefix 'cluster'.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    HasTraits, Any, Instance, Trait, Tuple, Color, Bool, Str, Enum, Float, \
    Either, Range, Int, Font, List, Directory, ListInstance, This, ListStr

from enthought.traits.ui.api import \
    View, Item, Group, Tabbed, HGroup, VGroup

from common import \
    color_scheme_trait, comment_trait, fontcolor_trait, fontname_trait, \
    fontsize_trait, label_trait, layer_trait, margin_trait, nojustify_trait, \
    peripheries_trait, pos_trait, rectangle_trait, root_trait, \
    showboxes_trait, target_trait, tooltip_trait, url_trait, pointf_trait, \
    color_trait, Alias, point_trait

from godot.base_graph import BaseGraph
from godot.node import Node
from godot.edge import Edge

from graph_view import nodes_item, edges_item

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

CLUSTER_ATTRIBUTES = ["bgcolor", "color", "colorscheme", "fillcolor",
    "fixedsize", "fontcolor", "fontname", "fontsize", "K", "label",
    "labeljust", "labelloc", "lp", "nojustify", "pencolor", "style", "target",
    "tooltip", "URL"]

#------------------------------------------------------------------------------
#  "Cluster" class:
#------------------------------------------------------------------------------

class Cluster(BaseGraph):
    """ Defines a representation of a subgraph in Graphviz's dot language.
    """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

#    ID = Str("cluster", desc="that clusters are encoded as subgraphs whose "
#        "names have the prefix 'cluster'")
#
#    name = Alias("ID", desc="synonym for ID")
#
#    # Nodes in the cluster.
#    nodes = List(Instance(Node))
#
#    # Edges in the cluster.
#    edges = List(Instance(Edge))
#
#    # Subgraphs of the cluster.
#    subgraphs = List(Instance("godot.subgraph.Subgraph"))
#
#    # Separate rectangular layout regions.
#    clusters = List(Instance("godot.cluster.Cluster"))

    # Parent graph in the graph heirarchy.
#    parent = Instance("godot.graph:Graph")

    # Root graph instance.
#    root = Instance("godot.graph:Graph")

    #--------------------------------------------------------------------------
    #  Xdot trait definitions:
    #--------------------------------------------------------------------------

    # For a given graph object, one will typically a draw directive before the
    # label directive. For example, for a node, one would first use the
    # commands in _draw_ followed by the commands in _ldraw_.
#    _draw_ = Str(desc="xdot drawing directive")
#
#    # Label draw directive.
#    _ldraw_ = Str(desc="xdot label drawing directive")

    #--------------------------------------------------------------------------
    #  Graphviz dot language trait definitions:
    #--------------------------------------------------------------------------

    # When attached to the root graph, this color is used as the background for
    # entire canvas. When a cluster attribute, it is used as the initial
    # background for the cluster. If a cluster has a filled
    # <html:a rel="attr">style</html:a>, the
    # cluster's <html:a rel="attr">fillcolor</html:a> will overlay the
    # background color.
    #
    # If no background color is specified for the root graph, no graphics
    # operation are performed on the background. This works fine for
    # PostScript but for bitmap output, all bits are initialized to something.
    # This means that when the bitmap output is included in some other
    # document, all of the bits within the bitmap's bounding box will be
    # set, overwriting whatever color or graphics where already on the page.
    # If this effect is not desired, and you only want to set bits explicitly
    # assigned in drawing the graph, set <html:a rel="attr">bgcolor</html:a>="transparent".
    bgcolor = Color("white", desc="color used as the background for the "
        "entire canvas", label="Background Color")

    # Basic drawing color for graphics, not text. For the latter, use the
    # <html:a rel="attr">fontcolor</html:a> attribute.
    #
    # For edges, the value can either be a single
    # <html:a rel="type">color</html:a> or a
    # <html:a rel="type">colorList</html:a>.
    # In the latter case, the edge is drawn using parallel splines or lines,
    # one for each color in the list, in the order given.
    # The head arrow, if any, is drawn using the first color in the list,
    # and the tail arrow, if any, the second color. This supports the common
    # case of drawing opposing edges, but using parallel splines instead of
    # separately routed multiedges.
    color = color_trait

    # This attribute specifies a color scheme namespace. If defined, it
    # specifies the context for interpreting color names. In particular, if a
    # <html:a rel="type">color</html:a> value has form <html:code>xxx</html:code> or <html:code>//xxx</html:code>,
    # then the color <html:code>xxx</html:code> will be evaluated according to the current color scheme.
    # If no color scheme is set, the standard X11 naming is used.
    # For example, if <html:code>colorscheme=bugn9</html:code>, then <html:code>color=7</html:code>
    # is interpreted as <html:code>/bugn9/7</html:code>.
    colorscheme = color_scheme_trait

    # Color used to fill the background of a node or cluster
    # assuming <html:a rel="attr">style</html:a>=filled.
    # If <html:a rel="attr">fillcolor</html:a> is not defined, <html:a rel="attr">color</html:a> is
    # used. (For clusters, if <html:a rel="attr">color</html:a> is not defined,
    # <html:a rel="attr">bgcolor</html:a> is used.) If this is not defined,
    # the default is used, except for
    # <html:a rel="attr">shape</html:a>=point or when the output
    # format is MIF,
    # which use black by default.
    #
    # Note that a cluster inherits the root graph's attributes if defined.
    # Thus, if the root graph has defined a <html:a rel="attr">fillcolor</html:a>, this will override a
    # <html:a rel="attr">color</html:a> or <html:a rel="attr">bgcolor</html:a> attribute set for the cluster.
    fillcolor = Color("grey", desc="fill color for background of a node")

    # If true, the node size is specified by the values of the
    # <html:a rel="attr">width</html:a>
    # and <html:a rel="attr">height</html:a> attributes only
    # and is not expanded to contain the text label.
    fixedsize = Bool(False, desc="node size to be specified by 'width' and "
        "'height'", label="Fixed size")

    # Color used for text.
    fontcolor = fontcolor_trait

    # Font used for text. This very much depends on the output format and, for
    # non-bitmap output such as PostScript or SVG, the availability of the font
    # when the graph is displayed or printed. As such, it is best to rely on
    # font faces that are generally available, such as Times-Roman, Helvetica or
    # Courier.
    #
    # If Graphviz was built using the
    # <html:a href="http://pdx.freedesktop.org/~fontconfig/fontconfig-user.html">fontconfig library</html:a>, the latter library
    # will be used to search for the font. However, if the <html:a rel="attr">fontname</html:a> string
    # contains a slash character "/", it is treated as a pathname for the font
    # file, though font lookup will append the usual font suffixes.
    #
    # If Graphviz does not use fontconfig, <html:a rel="attr">fontname</html:a> will be
    # considered the name of a Type 1 or True Type font file.
    # If you specify <html:code>fontname=schlbk</html:code>, the tool will look for a
    # file named  <html:code>schlbk.ttf</html:code> or <html:code>schlbk.pfa</html:code> or <html:code>schlbk.pfb</html:code>
    # in one of the directories specified by
    # the <html:a rel="attr">fontpath</html:a> attribute.
    # The lookup does support various aliases for the common fonts.
    fontname = fontname_trait

    # Font size, in <html:a rel="note">points</html:a>, used for text.
    fontsize = fontsize_trait

    # Spring constant used in virtual physical model. It roughly corresponds to
    # an ideal edge length (in inches), in that increasing K tends to increase
    # the distance between nodes. Note that the edge attribute len can be used
    # to override this value for adjacent nodes.
    K = Float(0.3, desc="spring constant used in virtual physical model")

    # Text label attached to objects.
    # If a node's <html:a rel="attr">shape</html:a> is record, then the label can
    # have a <html:a href="http://www.graphviz.org/doc/info/shapes.html#record">special format</html:a>
    # which describes the record layout.
    label = label_trait

    # Justification for cluster labels. If <html:span class="val">r</html:span>, the label
    # is right-justified within bounding rectangle; if <html:span class="val">l</html:span>, left-justified;
    # else the label is centered.
    # Note that a subgraph inherits attributes from its parent. Thus, if
    # the root graph sets <html:a rel="attr">labeljust</html:a> to <html:span class="val">l</html:span>, the subgraph inherits
    # this value.
    labeljust = Trait("c", {"Centre": "c", "Right": "r", "Left": "l"},
        desc="justification for cluster labels", label="Label justification")

    # Top/bottom placement of graph and cluster labels.
    # If the attribute is <html:span class="val">t</html:span>, place label at the top;
    # if the attribute is <html:span class="val">b</html:span>, place label at the bottom.
    # By default, root
    # graph labels go on the bottom and cluster labels go on the top.
    # Note that a subgraph inherits attributes from its parent. Thus, if
    # the root graph sets <html:a rel="attr">labelloc</html:a> to <html:span class="val">b</html:span>, the subgraph inherits
    # this value.
    labelloc = Trait("b", {"Bottom": "b", "Top":"t"},
        desc="placement of graph and cluster labels",
        label="Label location")

    # Label position, in points. The position indicates the center of the
    # label.
    lp = point_trait

    # By default, the justification of multi-line labels is done within the
    # largest context that makes sense. Thus, in the label of a polygonal node,
    # a left-justified line will align with the left side of the node (shifted
    # by the prescribed margin). In record nodes, left-justified line will line
    # up with the left side of the enclosing column of fields. If nojustify is
    # "true", multi-line labels will be justified in the context of itself. For
    # example, if the attribute is set, the first label line is long, and the
    # second is shorter and left-justified, the second will align with the
    # left-most character in the first line, regardless of how large the node
    # might be.
    nojustify = nojustify_trait


    # Color used to draw the bounding box around a cluster. If
    # <html:a rel="attr">pencolor</html:a> is not defined,
    # <html:a rel="attr">color</html:a> is used. If this is not defined,
    # <html:a rel="attr">bgcolor</html:a> is used. If this is not defined, the
    # default is used.
    # Note that a cluster inherits the root graph's attributes if defined.
	# Thus, if the root graph has defined a
    # <html:a rel="attr">pencolor</html:a>, this will override a
	# <html:a rel="attr">color</html:a> or <html:a rel="attr">bgcolor</html:a>
    # attribute set for the cluster.
    pencolor = Color("grey", desc="color for the cluster bounding box")

    # Set style for node or edge. For cluster subgraph, if "filled", the
    # cluster box's background is filled.
    style = ListStr(desc="style for node")

    # If the object has a URL, this attribute determines which window
    # of the browser is used for the URL.
    # See <html:a href="http://www.w3.org/TR/html401/present/frames.html#adef-target">W3C documentation</html:a>.
    target = target_trait

    # Tooltip annotation attached to the node or edge. If unset, Graphviz
    # will use the object's <html:a rel="attr">label</html:a> if defined.
    # Note that if the label is a record specification or an HTML-like
    # label, the resulting tooltip may be unhelpful. In this case, if
    # tooltips will be generated, the user should set a <html:tt>tooltip</html:tt>
    # attribute explicitly.
    tooltip = tooltip_trait

    # Hyperlinks incorporated into device-dependent output.
    # At present, used in ps2, cmap, i*map and svg formats.
    # For all these formats, URLs can be attached to nodes, edges and
    # clusters. URL attributes can also be attached to the root graph in ps2,
    # cmap and i*map formats. This serves as the base URL for relative URLs in the
    # former, and as the default image map file in the latter.
    #
    # For svg, cmapx and imap output, the active area for a node is its
    # visible image.
    # For example, an unfilled node with no drawn boundary will only be active on its label.
    # For other output, the active area is its bounding box.
    # The active area for a cluster is its bounding box.
    # For edges, the active areas are small circles where the edge contacts its head
    # and tail nodes. In addition, for svg, cmapx and imap, the active area
    # includes a thin polygon approximating the edge. The circles may
    # overlap the related node, and the edge URL dominates.
    # If the edge has a label, this will also be active.
    # Finally, if the edge has a head or tail label, this will also be active.
    #
    # Note that, for edges, the attributes <html:a rel="attr">headURL</html:a>,
    # <html:a rel="attr">tailURL</html:a>, <html:a rel="attr">labelURL</html:a> and
    # <html:a rel="attr">edgeURL</html:a> allow control of various parts of an
    # edge. Also note that, if active areas of two edges overlap, it is unspecified
    # which area dominates.
    URL = url_trait

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        Tabbed(
            VGroup(
                Item("ID"),
                Tabbed(nodes_item, edges_item, dock="tab"),
                label="Cluster"
            ),
            Group(["label", "fontname", "fontsize", "nojustify", "labeljust",
                   "labelloc", "lp"],
                label="Label"
            ),
            Group(["bgcolor", "color", "colorscheme", "fillcolor", "fontcolor",
                   "pencolor"],
                label="Color"),
            Group(["fixedsize", "K", "style", "tooltip", "target", "URL"],
                Group(["_draw_", "_ldraw_"], label="Xdot", show_border=True),
                label="Misc"
            )
        ),
        title="Cluster", id="godot.cluster", buttons=["OK", "Cancel", "Help"],
        resizable=True
    )

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __str__(self):
        """ Return a string representing the graph when requested by str()
        (or print).

        @rtype:  string
        @return: String representing the graph.

        """
        s = "subgraph"
        return "%s %s" % ( s, super( Cluster, self ).__str__() )

    #--------------------------------------------------------------------------
    #  "BaseGraph" interface:
    #--------------------------------------------------------------------------

    def _dot_attributes_default(self):
        """ Trait initialiser.
        """
        return CLUSTER_ATTRIBUTES

    #--------------------------------------------------------------------------
    #  Trait initialisers:
    #--------------------------------------------------------------------------

    def _labelloc_default(self):
        """ Trait initialiser.
        """
        return "Top"

    #--------------------------------------------------------------------------
    #  Event handlers :
    #--------------------------------------------------------------------------

    def _ID_changed(self, new):
        """ Handles the ID changing by ensuring that it has a 'cluster' prefix.
        """
        if new[:7].lower() != "cluster":
            self.ID = "cluster_%s" % new

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    Cluster().configure_traits()

# EOF +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
