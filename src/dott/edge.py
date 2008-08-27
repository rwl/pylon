#------------------------------------------------------------------------------
#
#  Copyright (c) 2008, Richard W. Lincoln
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Richard W. Lincoln
#  Date:   27/08/2008
#
#------------------------------------------------------------------------------

""" Defines a graph edge """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import HasTraits, Any

#------------------------------------------------------------------------------
#  "Edge" class:
#------------------------------------------------------------------------------

class Edge(HasTraits):
    """ Defines a graph edge """

    # Style of arrowhead on the head node of an edge.
    # See also the <html:a rel="attr">dir</html:a> attribute,
    # and the <html:a rel="note">undirected</html:a> note.
    arrowhead = Enum

	# Multiplicative scale factor for arrowheads.
    arrowsize = Float

    # Style of arrowhead on the tail node of an edge.
    # See also the <html:a rel="attr">dir</html:a> attribute,
    # and the <html:a rel="note">undirected</html:a> note.
    arrowtail = Enum

    # Basic drawing color for graphics, not text. For the latter, use the
    # <html:a rel="attr">fontcolor</html:a> attribute.
    #
    # For edges, the value
    # can either be a single <html:a rel="type">color</html:a> or a <html:a rel="type">colorList</html:a>.
    # In the latter case, the edge is drawn using parallel splines or lines,
    # one for each color in the list, in the order given.
    # The head arrow, if any, is drawn using the first color in the list,
    # and the tail arrow, if any, the second color. This supports the common
    # case of drawing opposing edges, but using parallel splines instead of
    # separately routed multiedges.
    color = Color

    # This attribute specifies a color scheme namespace. If defined, it specifies
    # the context for interpreting color names. In particular, if a
    # <html:a rel="type">color</html:a> value has form <html:code>xxx</html:code> or <html:code>//xxx</html:code>,
    # then the color <html:code>xxx</html:code> will be evaluated according to the current color scheme.
    # If no color scheme is set, the standard X11 naming is used.
    # For example, if <html:code>colorscheme=bugn9</html:code>, then <html:code>color=7</html:code>
    # is interpreted as <html:code>/bugn9/7</html:code>.
    colorscheme = Str

	# Comments are inserted into output. Device-dependent.
    comment = Any

	# If <html:span class="val">false</html:span>, the edge is not used in
    # ranking the nodes.
    constraint = Bool

    # If <html:span class="val">true</html:span>, attach edge label to edge by a 2-segment
    # polyline, underlining the label, then going to the closest point of spline.
    decorate = Bool

    # Set edge type for drawing arrowheads. This indicates which ends of the
    # edge should be decorated with an arrowhead. The actual style of the
    # arrowhead can be specified using the <html:a rel="attr">arrowhead</html:a>
    # and <html:a rel="attr">arrowtail</html:a> attributes.
    # See <html:a rel="note">undirected</html:a>.
    dir = DirType

	# Synonym for <html:a rel="attr">edgeURL</html:a>.
    edgehref = Str

    edgetarget = Any

    # Tooltip annotation attached to the non-label part of an edge.
    # This is used only if the edge has a <html:a rel="attr">URL</html:a>
    # or <html:a rel="attr">edgeURL</html:a> attribute.
    edgetooltip = EscString

    # If <html:a rel="attr">edgeURL</html:a> is defined, this is the link used for the non-label
    # parts of an edge. This value overrides any <html:a rel="attr">URL</html:a>
    # defined for the edge.
    # Also, this value is used near the head or tail node unless overridden
    # by a <html:a rel="attr">headURL</html:a> or <html:a rel="attr">tailURL</html:a> value,
    # respectively.
    # See <html:a rel="note">undirected</html:a>.
    edge_url = Str

	# Color used for text.
    fontcolor = Any

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
    fontname = Font

	# Font size, in <html:a rel="note">points</html:a>, used for text.
    fontsize = Float

    # If <html:span class="val">true</html:span>, the head of an edge is clipped to the boundary of the head node;
    # otherwise, the end of the edge goes to the center of the node, or the
    # center of a port, if applicable.
    headclip = Bool

	# Synonym for <html:a rel="attr">headURL</html:a>.
    headhref = Str

	# Text label to be placed near head of edge.
	# See <html:a rel="note">undirected</html:a>.
    headlabel = Str

    headport = Any

    headtarget = EscString

    # Tooltip annotation attached to the head of an edge. This is used only
    # if the edge has a <html:a rel="attr">headURL</html:a> attribute.
    headtooltip = EscString

    # If <html:a rel="attr">headURL</html:a> is defined, it is
    # output as part of the head label of the edge.
    # Also, this value is used near the head node, overriding any
    # <html:a rel="attr">URL</html:a> value.
    # See <html:a rel="note">undirected</html:a>.
    headurl = Str

	# Synonym for <html:a rel="attr">URL</html:a>.
    href = Any

    # Text label attached to objects.
    # If a node's <html:a rel="attr">shape</html:a> is record, then the label can
    # have a <html:a href="http://www.graphviz.org/doc/info/shapes.html#record">special format</html:a>
    # which describes the record layout.
    label = Str

    # This, along with <html:a rel="attr">labeldistance</html:a>, determine
    # where the
    # headlabel (taillabel) are placed with respect to the head (tail)
    # in polar coordinates. The origin in the coordinate system is
    # the point where the edge touches the node. The ray of 0 degrees
    # goes from the origin back along the edge, parallel to the edge
    # at the origin.
    #
    # The angle, in degrees, specifies the rotation from the 0 degree ray,
    # with positive angles moving counterclockwise and negative angles
    # moving clockwise.
    labelangle = Float

    # Multiplicative scaling factor adjusting the distance that
    # the headlabel (taillabel) is from the head (tail) node.
    # The default distance is 10 points. See <html:a rel="attr">labelangle</html:a>
    # for more details.
    labeldistance = Float

    labelfloat = Bool

    # Color used for headlabel and taillabel.
    # If not set, defaults to edge's fontcolor.
    labelfontcolor = Color

	# Font used for headlabel and taillabel.
	# If not set, defaults to edge's fontname.
    labelfontname = Font

	# Font size, in <html:a rel="note">points</html:a>, used for headlabel and taillabel.
	# If not set, defaults to edge's fontsize.
    labelfontsize = Float

	# Synonym for <html:a rel="attr">labelURL</html:a>.
    labelhref = Str

    labeltarget = EscString

    # Tooltip annotation attached to label of an edge.
    # This is used only if the edge has a <html:a rel="attr">URL</html:a>
    # or <html:a rel="attr">labelURL</html:a> attribute.
    labeltooltip = EscString

    # If <html:a rel="attr">labelURL</html:a> is defined, this is the link used for the label
    # of an edge. This value overrides any <html:a rel="attr">URL</html:a>
    # defined for the edge.
    labelurl = Str

	# Specifies layers in which the node or edge is present.
    layer = Any

	# Preferred edge length, in inches.
    len = Float

    lhead = Str

    lp = Any

    ltail = Str

	# Minimum edge length (rank difference between head and tail).
    minlen = Int

    nojustify = Bool

    # Position of node, or spline control points.
    # For nodes, the position indicates the center of the node.
    # On output, the coordinates are in <html:a href="#points">points</html:a>.
    #
    # In neato and fdp, pos can be used to set the initial position of a node.
    # By default, the coordinates are assumed to be in inches. However, the
    # <html:a href="http://www.graphviz.org/doc/info/command.html#d:s">-s</html:a> command line flag can be used to specify
    # different units.
    #
    # When the <html:a href="http://www.graphviz.org/doc/info/command.html#d:n">-n</html:a> command line flag is used with
    # neato, it is assumed the positions have been set by one of the layout
    # programs, and are therefore in points. Thus, <html:code>neato -n</html:code> can accept
    # input correctly without requiring a <html:code>-s</html:code> flag and, in fact,
    # ignores any such flag.
    pos = Any

    # Edges with the same head and the same <html:a rel="attr">samehead</html:a> value are aimed
    # at the same point on the head.
    # See <html:a rel="note">undirected</html:a>.
    samehead = Str

    # Edges with the same tail and the same <html:a rel="attr">sametail</html:a> value are aimed
    # at the same point on the tail.
    # See <html:a rel="note">undirected</html:a>.
    sametail = Str

	# Print guide boxes in PostScript at the beginning of
	# routesplines if 1, or at the end if 2. (Debugging)
    showboxes = Trait("beginning", {"beginning": 1, "end": 2})

    # Set style for node or edge. For cluster subgraph, if "filled", the
    # cluster box's background is filled.
    style = Enum("filled")

    # If <html:span class="val">true</html:span>, the tail of an edge is clipped to the boundary of the tail node;
    # otherwise, the end of the edge goes to the center of the node, or the
    # center of a port, if applicable.
    tailclip = Bool

	# Synonym for <html:a rel="attr">tailURL</html:a>.
    tailhref = Str

	# Text label to be placed near tail of edge.
	# See <html:a rel="note">undirected</html:a>.
    taillabel = Str

    tailport = Any

    tailtarget = Any

	# Tooltip annotation attached to the tail of an edge. This is used only
	# if the edge has a <html:a rel="attr">tailURL</html:a> attribute.
    tailtooltip = EscString

    # If <html:a rel="attr">tailURL</html:a> is defined, it is
    # output as part of the tail label of the edge.
    # Also, this value is used near the tail node, overriding any
    # <html:a rel="attr">URL</html:a> value.
    # See <html:a rel="note">undirected</html:a>.
    tailurl = Str

	# If the object has a URL, this attribute determines which window
	# of the browser is used for the URL.
	# See <html:a href="http://www.w3.org/TR/html401/present/frames.html#adef-target">W3C documentation</html:a>.
    target = EscString

    # Tooltip annotation attached to the node or edge. If unset, Graphviz
    # will use the object's <html:a rel="attr">label</html:a> if defined.
    # Note that if the label is a record specification or an HTML-like
    # label, the resulting tooltip may be unhelpful. In this case, if
    # tooltips will be generated, the user should set a <html:tt>tooltip</html:tt>
    # attribute explicitly.
    tooltip = EscString

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
    url = Str

    weight = Float

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    Edge().configure_traits()

# EOF +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
