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

""" A graph node """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import HasTraits, Color, String

#------------------------------------------------------------------------------
#  "Node" class:
#------------------------------------------------------------------------------

class Node(HasTraits):
    """ A graph node """

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
    color = Color(desc="drawing color for graphics, not text")

    # This attribute specifies a color scheme namespace. If defined, it
    # specifies the context for interpreting color names. In particular, if a
    # <html:a rel="type">color</html:a> value has form <html:code>xxx</html:code> or <html:code>//xxx</html:code>,
    # then the color <html:code>xxx</html:code> will be evaluated according to the current color scheme.
    # If no color scheme is set, the standard X11 naming is used.
    # For example, if <html:code>colorscheme=bugn9</html:code>, then <html:code>color=7</html:code>
    # is interpreted as <html:code>/bugn9/7</html:code>.
    colorscheme = Enum(desc="a color scheme namespace")

	# Comments are inserted into output. Device-dependent.
    comment = Str(desc="comments inserted into output")

    # Distortion factor for <html:a rel="attr">shape</html:a>=polygon.
    # Positive values cause top part to be larger than bottom; negative values do the opposite.
    distortion = Float(desc="distortion factor for polygons")

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
    fillcolor = Color(desc="fill color for background of a node or cluster")

    # If true, the node size is specified by the values of the
    # <html:a rel="attr">width</html:a>
    # and <html:a rel="attr">height</html:a> attributes only
    # and is not expanded to contain the text label.
    fixedsize = Float(desc="node size to be specified by 'width' and 'height'")

	# Color used for text.
    fontcolor = Color(desc="color used for text")

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
    fontname = Font(desc="font used for text")

    # Font size, in <html:a rel="note">points</html:a>, used for text.
    fontsize = Float(desc="font size in points")

    # If the end points of an edge belong to the same group, i.e., have the
    # same group attribute, parameters are set to avoid crossings and keep
    # the edges straight.
    group = Str

    height = Float

    # Gives the name of a file containing an image to be displayed inside
    # a node. The image file must be in one of the recognized formats,
    # typically JPEG, PNG, GIF or Postscript, and be able to be converted
    # into the desired output format.
    #
    # Unlike with the <html:a rel="attr">shapefile</html:a> attribute,
    # the image is treated as node
    # content rather than the entire node. In particular, an image can
    # be contained in a node of any shape, not just a rectangle.
    image = Str

    # Attribute controlling how an image fills its
    # containing node. In general, the image is given its natural size,
    # (cf. <html:a rel="attr">dpi</html:a>),
    # and the node size is made large enough to contain its image, its
    # label, its margin, and its peripheries.
    # Its width and height will also be at least as large as its
    # minimum <html:a rel="attr">width</html:a> and <html:a rel="attr">height</html:a>.
    # If, however, <html:code>fixedsize=true</html:code>,
    # the width and height attributes specify the exact size of the node.
    #
    # During rendering, in the default case (<html:code>imagescale=false</html:code>),
    # the image retains its natural size.
    # If <html:span class="val">true</html:span>,
    # the image is uniformly scaled (i.e., its aspect ration is
    # preserved) to fit inside the node.
    # At least one dimension of the image will be as large as possible
    # given the size of the node.
    # When <html:span class="val">width</html:span>,
    # the width of the image is scaled to fill the node width.
    # The corresponding property holds when <html:tt>imagescale=height</html:tt>.
    # When <html:span class="val">both</html:span>,
    # both the height and the width are scaled separately to fill the node.
    #
    # In all cases, if a dimension of the image is larger than the
    # corresponding dimension of the node, that dimension of the
    # image is scaled down to fit the node. As with the case of
    # expansion, if <html:code>imagescale=true</html:code>, width and height are
    # scaled uniformly.
    imagescale = Float

    # Text label attached to objects.
    # If a node's <html:a rel="attr">shape</html:a> is record, then the label can
    # have a <html:a href="http://www.graphviz.org/doc/info/shapes.html#record">special format</html:a>
    # which describes the record layout.
    label = Str(desc="text label attached to objects")

    # Specifies layers in which the node or edge is present.
    layer = Any

    # For graphs, this sets x and y margins of canvas, in inches. If the margin
    # is a single double, both margins are set equal to the given value.
    #
    # Note that the margin is not part of the drawing but just empty space
    # left around the drawing. It basically corresponds to a translation of
    # drawing, as would be necessary to center a drawing on a page. Nothing
    # is actually drawn in the margin. To actually extend the background of
    # a drawing, see the <html:a rel="attr">pad</html:a> attribute.
    #
    # For nodes, this attribute specifies space left around the node's label.
    # By default, the value is <html:code>0.11,0.055</html:code>.
    margin = Float(desc="x and y margins of canvas, in inches")

    nojustify = Bool

    # Set number of peripheries used in polygonal shapes and cluster
    # boundaries. Note that
    # <html:a href="http://www.graphviz.org/doc/info/shapes.html#epsf">user-defined shapes</html:a> are treated as a
    # form of box shape, so the default
    # peripheries value is 1 and the user-defined shape will be drawn in
    # a bounding rectangle. Setting <html:code>peripheries=0</html:code> will turn this off.
    # Also, 1 is the maximum peripheries value for clusters.
    peripheries = Int

    pin = Bool

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
    pos = Float(desc="position of node, or spline control points")

	# Rectangles for fields of records, in <html:a rel="note">points</html:a>.
    rects = Float

    # If true, force polygon to be regular.
    regular = Bool(desc="polygon to be regular")


    # This specifies nodes to be used as the center of the
    # layout and the root of the generated spanning tree. As a graph attribute,
    # this gives the name of the node. As a node attribute (circo only), it
    # specifies that the node should be used as a central node. In twopi,
    # this will actually be the central node. In circo, the block containing
    # the node will be central in the drawing of its connected component.
    # If not defined,
    # twopi will pick a most central node, and circo will pick a random node.
    root = Str

    # If the input graph defines the <html:a rel="attr">
    # <html:a rel="attr">vertices</html:a></html:a>
    # attribute, and output is dot or xdot, this gives
    # the number of points used for a node whose shape is a circle or ellipse.
    # It plays the same role in neato, when adjusting the layout to avoid
    # overlapping nodes, and in image maps.
    samplepoints = Int

	# Set polygon to be regular.
    shape = shape_trait(desc="polygon to be regular")

    shapefile = File

    # Print guide boxes in PostScript at the beginning of
    # routesplines if 1, or at the end if 2. (Debugging)
    showboxes = Trait("beginning", {"beginning": 1, "end": 2})

    sides = Int

    skew = Float

    # Set style for node or edge. For cluster subgraph, if "filled", the
    # cluster box's background is filled.
    style = Any(desc="style for node or edge")

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
    tooltip = EscString(desc="tooltip annotation attached to the node or edge")

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
    url = String(desc="hyperlinks incorporated into device-dependent output")

    # If the input graph defines this attribute, the node is polygonal,
    # and output is dot or xdot, this attribute provides the
    # coordinates of the vertices of the node's polygon, in inches.
    # If the node is an ellipse or circle, the
    # <html:a rel="attr">samplepoints</html:a> attribute affects
    # the output.
    vertices = List(Tuple(Float, Float))

    # Width of node, in inches. This is taken as the initial, minimum width
    # of the node. If <html:a rel="attr">fixedsize</html:a> is true, this
    # will be the final width of the node. Otherwise, if the node label
    # requires more width to fit, the node's width will be increased to
    # contain the label. Note also that, if the output format is dot, the
    # value given to <html:a rel="attr">width</html:a> will be the final value.
    width = Float(desc="width of node, in inches")

    # Provides z coordinate value for 3D layouts and displays. If the
    # graph has <html:a rel="attr">dim</html:a> set to 3 (or more),
    # neato will use a node's <html:a rel="attr">z</html:a> value
    # for the z coordinate of its initial position if
    # its <html:a rel="attr">pos</html:a> attribute is also defined.
    #
    # Even if no <html:a rel="attr">z</html:a> values are specified in the input, it is necessary to
    # declare a <html:a rel="attr">z</html:a> attribute for nodes, e.g, using <html:tt>node[z=""]</html:tt>
    # in order to get z values on output.
    # Thus, setting <html:tt>dim=3</html:tt> but not declaring <html:a rel="attr">z</html:a> will
    # cause <html:tt>neato -Tvrml</html:tt> to
    # layout the graph in 3D but project the layout onto the xy-plane
    # for the rendering. If the <html:a rel="attr">z</html:a> attribute is declared, the final rendering
    # will be in 3D.
    z = Float(desc="z coordinate value for 3D layouts and displays")

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    Node().configure_traits()

# EOF +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
