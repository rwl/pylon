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

""" Defines a graph node. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import uuid

from enthought.traits.api import \
    HasTraits, Color, Str, Enum, Float, Font, Any, Bool, Int, File, Trait, \
    List, Tuple, ListStr, Range, Instance, on_trait_change

from enthought.traits.ui.api import View, Item, Group, Tabbed

from enthought.traits.ui.api import TableEditor, InstanceEditor
from enthought.traits.ui.table_column import ObjectColumn
from enthought.traits.ui.extras.checkbox_column import CheckboxColumn

from enthought.traits.ui.table_filter import \
    EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate, RuleTableFilter

from enthought.enable.api import Container
from enthought.naming.unique_name import make_unique_name

from dot2tex.dotparsing import quote_if_necessary

from common import \
    color_scheme_trait, comment_trait, fontcolor_trait, fontname_trait, \
    fontsize_trait, label_trait, layer_trait, margin_trait, nojustify_trait, \
    peripheries_trait, pos_trait, rectangle_trait, root_trait, \
    showboxes_trait, target_trait, tooltip_trait, url_trait, pointf_trait, \
    color_trait, Alias

from xdot_attr_parser import XdotAttrParser

#------------------------------------------------------------------------------
#  Trait definitions:
#------------------------------------------------------------------------------

node_shapes = ["rect", "rectangle", "box", "ellipse", "circle", "invtriangle",
    "invtrapezium", "point", "egg", "triangle", "plaintext", "diamond",
    "trapezium", "parallelogram", "house", "pentagon", "hexagon", "septagon",
    "octagon", "doublecircle", "doubleoctagon", "tripleoctagon", "invhouse",
    "none", "note", "tab", "box3d", "component"]

shape_trait = Enum(node_shapes, desc="node shape", label="Node shape")

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

#node_attrs = ['URL', 'color', 'colorscheme', 'comment', 'distortion',
#    'fillcolor', 'fixedsize', 'fontcolor', 'fontname', 'fontsize', 'group',
#    'height', 'image', 'imagescale', 'label', 'label_drawing', 'layer',
#    'margin', 'nojustify', 'orientation', 'peripheries', 'pin', 'pos', 'rects',
#    'regular', 'root', 'samplepoints', 'shape', 'shapefile', 'showboxes',
#    'sides', 'skew', 'style', 'target', 'tooltip', 'vertices', 'width', 'z']

#------------------------------------------------------------------------------
#  "Node" class:
#------------------------------------------------------------------------------

class Node(HasTraits):
    """ A graph node. """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    ID = Str
    name = Alias("ID", desc="synonym for ID")

    #--------------------------------------------------------------------------
    #  Xdot trait definitions:
    #--------------------------------------------------------------------------

    # For a given graph object, one will typically a draw directive before the
    # label directive. For example, for a node, one would first use the
    # commands in _draw_ followed by the commands in _ldraw_.
    _draw_ = Str(desc="xdot drawing directive")
    _ldraw_ = Str(desc="xdot label drawing directive")

    #--------------------------------------------------------------------------
    #  Enable trait definitions:
    #--------------------------------------------------------------------------

    # Container for the drawing and label components.
    component = Instance(Container, desc="container of graph components.")

    # Container of drawing components, typically the node shape.
    drawing = Instance(Container)

    # Container of label components.
    label_drawing = Instance(Container)

    #--------------------------------------------------------------------------
    #  Graphviz dot language trait definitions:
    #--------------------------------------------------------------------------

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

	# Comments are inserted into output. Device-dependent.
    comment = comment_trait

    # Distortion factor for <html:a rel="attr">shape</html:a>=polygon.
    # Positive values cause top part to be larger than bottom; negative values do the opposite.
    distortion = Float(0.0, desc="distortion factor for polygons")

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

    # If the end points of an edge belong to the same group, i.e., have the
    # same group attribute, parameters are set to avoid crossings and keep
    # the edges straight.
    group = Str("", desc="If the end points of an edge belong to the same "
        "group, i.e., have the same group attribute, parameters are set to "
        "avoid crossings and keep the edges straight.")

    # Height of node, in inches. This is taken as the initial, minimum height
    # of the node. If fixedsize is true, this will be the final height of the
    # node. Otherwise, if the node label requires more height to fit, the
    # node's height will be increased to contain the label. Note also that, if
    # the output format is dot, the value given to height will be the final
    # value.
    height = Float(0.5, desc="node height, in inches")

    # Gives the name of a file containing an image to be displayed inside
    # a node. The image file must be in one of the recognized formats,
    # typically JPEG, PNG, GIF or Postscript, and be able to be converted
    # into the desired output format.
    #
    # Unlike with the <html:a rel="attr">shapefile</html:a> attribute,
    # the image is treated as node
    # content rather than the entire node. In particular, an image can
    # be contained in a node of any shape, not just a rectangle.
    image = Str("", desc="file name containing an image to be displayed "
        "inside a node")

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
    imagescale = Str("false", desc="how an image fills its containing node",
        label="Image scale")

    # Text label attached to objects.
    # If a node's <html:a rel="attr">shape</html:a> is record, then the label can
    # have a <html:a href="http://www.graphviz.org/doc/info/shapes.html#record">special format</html:a>
    # which describes the record layout.
    label = label_trait

    # Specifies layers in which the node or edge is present.
    layer = layer_trait

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
    margin = margin_trait

    nojustify = nojustify_trait

    # Angle, in degrees, used to rotate polygon node shapes. For any number of
    # polygon sides, 0 degrees rotation results in a flat base.
    orientation = Range(0.0, 360.0, desc="polygon rotation angle")

    # Set number of peripheries used in polygonal shapes and cluster
    # boundaries. Note that
    # <html:a href="http://www.graphviz.org/doc/info/shapes.html#epsf">user-defined shapes</html:a> are treated as a
    # form of box shape, so the default
    # peripheries value is 1 and the user-defined shape will be drawn in
    # a bounding rectangle. Setting <html:code>peripheries=0</html:code> will turn this off.
    # Also, 1 is the maximum peripheries value for clusters.
    peripheries = peripheries_trait

    # If true and the node has a pos attribute on input, neato prevents the
    # node from moving from the input position. This property can also be
    # specified in the pos attribute itself (cf. the point type).
    #
    # Note: Due to an artifact of the implementation, final coordinates are
    # translated to the origin. Thus, if you look at the output coordinates
    # given in the (x)dot or plain format, pinned nodes will not have the same
    # output coordinates as were given on input. If this is important, a simple
    # workaround is to maintain the coordinates of a pinned node. The vector
    # difference between the old and new coordinates will give the translation,
    # which can then be subtracted from all of the appropriate coordinates.
    pin = Bool(False, desc="neato to prevent the node from moving from the "
        "input position")

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
    pos = pos_trait

	# Rectangles for fields of records, in <html:a rel="note">points</html:a>.
    rects = rectangle_trait

    # If true, force polygon to be regular.
    regular = Bool(False, desc="polygon to be regular")


    # This specifies nodes to be used as the center of the
    # layout and the root of the generated spanning tree. As a graph attribute,
    # this gives the name of the node. As a node attribute (circo only), it
    # specifies that the node should be used as a central node. In twopi,
    # this will actually be the central node. In circo, the block containing
    # the node will be central in the drawing of its connected component.
    # If not defined,
    # twopi will pick a most central node, and circo will pick a random node.
    root = root_trait

    # If the input graph defines the <html:a rel="attr">
    # <html:a rel="attr">vertices</html:a></html:a>
    # attribute, and output is dot or xdot, this gives
    # the number of points used for a node whose shape is a circle or ellipse.
    # It plays the same role in neato, when adjusting the layout to avoid
    # overlapping nodes, and in image maps.
    samplepoints = Int(8, desc="number of points used for a node whose shape "
        "is a circle or ellipse", label="Sample points")

	# Set polygon to be regular.
    shape = shape_trait#(desc="polygon to be regular")

    # (Deprecated) If defined, shapefile specifies a file containing
    # user-supplied node content. The shape of the node is set to box. The
    # image in the shapefile must be rectangular. The image formats supported
    # as well as the precise semantics of how the file is used depends on the
    # output format.
    shapefile = File(desc="file containing user-supplied node content",
        label="Shape file")

    # Print guide boxes in PostScript at the beginning of
    # routesplines if 1, or at the end if 2. (Debugging)
    showboxes = showboxes_trait

    # Number of sides if shape=polygon.
    sides = Int(4, desc="number of sides if shape=polygon")

    # Skew factor for shape=polygon. Positive values skew top of polygon to
    # right; negative to left.
    skew = Float(0.0, desc="skew factor for shape=polygon")

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

    # If the input graph defines this attribute, the node is polygonal,
    # and output is dot or xdot, this attribute provides the
    # coordinates of the vertices of the node's polygon, in inches.
    # If the node is an ellipse or circle, the
    # <html:a rel="attr">samplepoints</html:a> attribute affects
    # the output.
    vertices = List(pointf_trait, desc="coordinates of the vertices of the "
        "node's polygon")
#    vertices = pointf_trait

    # Width of node, in inches. This is taken as the initial, minimum width
    # of the node. If <html:a rel="attr">fixedsize</html:a> is true, this
    # will be the final width of the node. Otherwise, if the node label
    # requires more width to fit, the node's width will be increased to
    # contain the label. Note also that, if the output format is dot, the
    # value given to <html:a rel="attr">width</html:a> will be the final value.
    width = Float(0.75, desc="width of node, in inches")

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
    z = Float(0.0, desc="z coordinate value for 3D layouts and displays",
        label="z-coordinate")

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        Tabbed(
            Group(["ID", "_", "shape", "shapefile", "color", "fillcolor",
                "colorscheme", "style", "showboxes", "tooltip", "distortion",
                "sides", "target", "comment"],
                Group(["_draw_", "_ldraw_"], label="Xdot", show_border=True),
                label="Node"
            ),
            Group(["label", "fontname", "fontsize", "fontcolor", "nojustify",
                "image", "imagescale", "layer", "margin", "nojustify",
                "orientation", "peripheries", "pin", "rects", "regular"],
                label="Label"
            ),
            Group(["fixedsize", "width", "height", "z", "pos", "vertices"],
                label="Dimension"),
            Group(["URL", "samplepoints", "skew", "root", "group"],
                label="Miscellaneous")
        ),
        title="Node", id="godot.node", buttons=["OK", "Cancel", "Help"],
        resizable=True
    )

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, ID, **traits):
        """ Initialises a Node instance.
        """
        self.ID = ID
        super(Node, self).__init__(**traits)


    def __hash__(self):
        """ objects which compare equal have the same hash value.
        """
        return hash(self.ID)

    #--------------------------------------------------------------------------
    #  Trait initialisers:
    #--------------------------------------------------------------------------

    def _component_default(self):
        """ Trait initialiser.
        """
        return Container(fit_window=False, auto_size=True)

    #--------------------------------------------------------------------------
    #  Event handlers:
    #--------------------------------------------------------------------------

    @on_trait_change("_draw_")
    def parse_xdot_drawing_directive(self, new):
        """ Parses the drawing directive, updating the node components. """

        components = XdotAttrParser().parse_xdot_data(new)

#        max_x = max([c.bounds[0] for c in components] + [1])
#        max_y = max([c.bounds[1] for c in components] + [1])
#
#        container = Container(bounds=[max_x, max_y])
#        self.bounds = bounds=[max_x, max_y]

        container = Container(fit_window=False, auto_size=True)
        container.add(*components)
        self.drawing = container


    @on_trait_change("_ldraw_")
    def parse_xdot_label_directive(self, new):
        """ Parses the label drawing directive, updating the label
        components. """

        print "_ldraw_", new

        components = XdotAttrParser().parse_xdot_data(new)
        print "COMPONENTS:", components

        container = Container(fit_window=False, auto_size=True)#bounds=[200, 200])
        container.add(*components)
        self.label_drawing = container


    def _drawing_changed(self, old, new):
        """ Handles the container of drawing components changing. """

        if old is not None:
            self.component.remove(old)
        if new is not None:
            self.component.add(new)


    def _label_drawing_changed(self, old, new):
        """ Handles the container of label components changing. """

        if old is not None:
            self.component.remove(old)
        if new is not None:
            self.component.add(new)

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys, logging
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    from godot.component.component_viewer import ComponentViewer

    node = Node("node1", _draw_="c 5 -black e 32 18 32 18")
#    node.configure_traits()
    viewer = ComponentViewer(component=node.component)
    viewer.configure_traits()

# EOF +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
