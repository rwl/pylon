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

from enthought.traits.api import \
    HasTraits, Color, Str, Enum, Float, Font, Any, Bool, Int, File, Trait, \
    List, Tuple, ListStr, Instance

from enthought.traits.ui.api import TableEditor, View, Group, Item, Tabbed

from enthought.traits.ui.api import TableEditor, InstanceEditor
from enthought.traits.ui.table_column import ObjectColumn
from enthought.traits.ui.extras.checkbox_column import CheckboxColumn

from enthought.traits.ui.table_filter import \
    EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate, RuleTableFilter

from enthought.enable.api import Container

from dot2tex.dotparsing import quote_if_necessary

from node import Node

from common import \
    Alias, color_trait, color_scheme_trait, comment_trait, fontcolor_trait, \
    fontname_trait, fontsize_trait, label_trait, layer_trait, margin_trait, \
    nojustify_trait, peripheries_trait, pos_trait, rectangle_trait, \
    root_trait, showboxes_trait, target_trait, tooltip_trait, url_trait, \
    pointf_trait, point_trait, color_trait

#------------------------------------------------------------------------------
#  Trait definitions:
#------------------------------------------------------------------------------

arrow_styles = ["normal", "inv", "dot", "invdot", "odot", "invodot", "none",
    "tee", "empty", "invempty", "diamond", "odiamond", "ediamond", "crow",
    "box", "obox", "open", "halfopen", "vee"]

arrow_trait = Enum(arrow_styles, desc="Arrow style")

# portPos
#    modifier indicating where on a node an edge should be aimed. It has the
#    form portname[:compass_point] or compass_point. If the first form is used,
#    the corresponding node must either have record shape with one of its
#    fields having the given portname, or have an HTML-like label, one of whose
#    components has a PORT attribute set to portname.
#
#    If a compass point is used, it must have the form "n","ne","e","se","s",
#    "sw","w","nw","c","_". This modifies the edge placement to aim for the
#    corresponding compass point on the port or, in the second form where no
#    portname is supplied, on the node itself. The compass point "c" specifies
#    the center of the node or port. The compass point "_" specifies that an
#    appropriate side of the port adjacent to the exterior of the node should
#    be used, if such exists. Otherwise, the center is used. If no compass
#    point is used with a portname, the default value is "_".
#
#    This attribute can be attached to an edge using the headport and tailport
#    attributes, or as part of the edge description as in
#        node1:port1 -> node2:port5:nw;
#
#    Note that it is legal to have a portname the same as one of the compass
#    points. In this case, this reference will be resolved to the port. Thus,
#    if node A has a port w, then headport=w will refer to the port and not
#    the compass point. At present, in this case, there is no way to specify
#    that the compass point should be used.
port_pos_trait = Str(desc="port position")

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

edge_attrs = ['URL', 'arrowhead', 'arrowsize', 'arrowtail', 'color',
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
#  "Edge" class:
#------------------------------------------------------------------------------

class Edge(Container):
    """ Defines a graph edge. """

    from_node = Instance(Node, allow_none=False)

    to_node = Instance(Node, allow_none=False)

    # Nodes from which the 'to' and 'from' nodes may be selected.
    _nodes = List(Instance(Node))

    # Connection string used in string output.
    conn = Enum("--", "->")

    # For a given graph object, one will typically a draw directive before the
    # label directive. For example, for a node, one would first use the
    # commands in _draw_ followed by the commands in _ldraw_.
    _draw_ = Str(desc="xdot drawing directive", label="draw")
    _ldraw_ = Str(desc="xdot label drawing directive", label="ldraw")

    _hdraw_ = Str(desc="edge head arrowhead drawing directive.", label="hdraw")
    _tdraw_ = Str(desc="edge tail arrowhead drawing directive.", label="tdraw")
    _hldraw_ = Str(desc="edge head label drawing directive.", label="hldraw")
    _tldraw_ = Str(desc="edge tail label drawing directive.", label="tldraw")

    # Style of arrowhead on the head node of an edge.
    # See also the <html:a rel="attr">dir</html:a> attribute,
    # and the <html:a rel="note">undirected</html:a> note.
    arrowhead = arrow_trait

	# Multiplicative scale factor for arrowheads.
    arrowsize = Float(1.0, desc="multiplicative scale factor for arrowheads",
        label="Arrow size")

    # Style of arrowhead on the tail node of an edge.
    # See also the <html:a rel="attr">dir</html:a> attribute,
    # and the <html:a rel="note">undirected</html:a> note.
    arrowtail = arrow_trait

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
    color = color_trait

    # This attribute specifies a color scheme namespace. If defined, it specifies
    # the context for interpreting color names. In particular, if a
    # <html:a rel="type">color</html:a> value has form <html:code>xxx</html:code> or <html:code>//xxx</html:code>,
    # then the color <html:code>xxx</html:code> will be evaluated according to the current color scheme.
    # If no color scheme is set, the standard X11 naming is used.
    # For example, if <html:code>colorscheme=bugn9</html:code>, then <html:code>color=7</html:code>
    # is interpreted as <html:code>/bugn9/7</html:code>.
    colorscheme = color_scheme_trait

	# Comments are inserted into output. Device-dependent.
    comment = comment_trait

	# If <html:span class="val">false</html:span>, the edge is not used in
    # ranking the nodes.
    constraint = Bool(True, desc="if edge is used in ranking the nodes")

    # If <html:span class="val">true</html:span>, attach edge label to edge by a 2-segment
    # polyline, underlining the label, then going to the closest point of spline.
    decorate = Bool(False, desc="to attach edge label to edge by a 2-segment "
        "polyline, underlining the label, then going to the closest point of "
        "spline")

    # Set edge type for drawing arrowheads. This indicates which ends of the
    # edge should be decorated with an arrowhead. The actual style of the
    # arrowhead can be specified using the <html:a rel="attr">arrowhead</html:a>
    # and <html:a rel="attr">arrowtail</html:a> attributes.
    # See <html:a rel="note">undirected</html:a>.
    dir = Enum("forward", "back", "both", "none",
        desc="edge type for drawing arrowheads", label="Direction")

	# Synonym for <html:a rel="attr">edgeURL</html:a>.
    edgehref = Alias("edgeURL", desc="synonym for edgeURL")

    # If the edge has a URL or edgeURL  attribute, this attribute determines
    # which window of the browser is used for the URL attached to the non-label
    # part of the edge. Setting it to "_graphviz" will open a new window if it
    # doesn't already exist, or reuse it if it does. If undefined, the value of
    # the target is used.
    edgetarget = Str("", desc="which window of the browser is used for the "
        "URL attached to the non-label part of the edge", label="Edge target")

    # Tooltip annotation attached to the non-label part of an edge.
    # This is used only if the edge has a <html:a rel="attr">URL</html:a>
    # or <html:a rel="attr">edgeURL</html:a> attribute.
    edgetooltip = Str("", desc="annotation attached to the non-label part of "
        "an edge", label="Edge tooltip") #EscString

    # If <html:a rel="attr">edgeURL</html:a> is defined, this is the link used for the non-label
    # parts of an edge. This value overrides any <html:a rel="attr">URL</html:a>
    # defined for the edge.
    # Also, this value is used near the head or tail node unless overridden
    # by a <html:a rel="attr">headURL</html:a> or <html:a rel="attr">tailURL</html:a> value,
    # respectively.
    # See <html:a rel="note">undirected</html:a>.
    edgeURL = Str("", desc="link used for the non-label parts of an edge",
        label="Edge URL")#LabelStr

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

    # If <html:span class="val">true</html:span>, the head of an edge is clipped to the boundary of the head node;
    # otherwise, the end of the edge goes to the center of the node, or the
    # center of a port, if applicable.
    headclip = Bool(True, desc="head of an edge to be clipped to the boundary "
        "of the head node", label="Head clip")

	# Synonym for <html:a rel="attr">headURL</html:a>.
    headhref = Alias("headURL", desc="synonym for headURL")

	# Text label to be placed near head of edge.
	# See <html:a rel="note">undirected</html:a>.
    headlabel = Str("", desc="text label to be placed near head of edge",
        label="Head label")

    headport = port_pos_trait

    # If the edge has a headURL, this attribute determines which window of the
    # browser is used for the URL. Setting it to "_graphviz" will open a new
    # window if it doesn't already exist, or reuse it if it does. If undefined,
    # the value of the target is used.
    headtarget = Str(
        desc="which window of the browser is used for the URL",
        label="Head target"
    )

    # Tooltip annotation attached to the head of an edge. This is used only
    # if the edge has a <html:a rel="attr">headURL</html:a> attribute.
    headtooltip = Str("", desc="tooltip annotation attached to the head of an "
        "edge", label="Head tooltip")

    # If <html:a rel="attr">headURL</html:a> is defined, it is
    # output as part of the head label of the edge.
    # Also, this value is used near the head node, overriding any
    # <html:a rel="attr">URL</html:a> value.
    # See <html:a rel="note">undirected</html:a>.
    headURL = Str("", desc="output as part of the head label of the edge",
        label="Head URL")

	# Synonym for <html:a rel="attr">URL</html:a>.
    href = Alias("URL", desc="synonym for URL")

    # Text label attached to objects.
    # If a node's <html:a rel="attr">shape</html:a> is record, then the label can
    # have a <html:a href="http://www.graphviz.org/doc/info/shapes.html#record">special format</html:a>
    # which describes the record layout.
    label = label_trait

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
    labelangle = Float(-25.0, desc=", along with labeldistance, where the "
        "headlabel (taillabel) are placed with respect to the head (tail)",
        label="Label angle")

    # Multiplicative scaling factor adjusting the distance that
    # the headlabel (taillabel) is from the head (tail) node.
    # The default distance is 10 points. See <html:a rel="attr">labelangle</html:a>
    # for more details.
    labeldistance = Float(1.0, desc="multiplicative scaling factor adjusting "
        "the distance that the headlabel (taillabel) is from the head (tail) "
        "node", label="Label distance")

    # If true, allows edge labels to be less constrained in position. In
    # particular, it may appear on top of other edges.
    labelfloat = Bool(False, desc="edge labels to be less constrained in "
        "position", label="Label float")

    # Color used for headlabel and taillabel.
    # If not set, defaults to edge's fontcolor.
    labelfontcolor = Color("black", desc="color used for headlabel and "
        "taillabel", label="Label font color")

	# Font used for headlabel and taillabel.
	# If not set, defaults to edge's fontname.
    labelfontname = Font("Times-Roman", desc="Font used for headlabel and "
        "taillabel", label="Label font name")

	# Font size, in <html:a rel="note">points</html:a>, used for headlabel and taillabel.
	# If not set, defaults to edge's fontsize.
    labelfontsize = Float(14.0, desc="Font size, in points, used for "
        "headlabel and taillabel", label="label_font_size")

	# Synonym for <html:a rel="attr">labelURL</html:a>.
    labelhref = Alias("labelURL", desc="synonym for labelURL")

    # If the edge has a URL or labelURL  attribute, this attribute determines
    # which window of the browser is used for the URL attached to the label.
    # Setting it to "_graphviz" will open a new window if it doesn't already
    # exist, or reuse it if it does. If undefined, the value of the target is
    # used.
    labeltarget = Str("", desc="which window of the browser is used for the "
        "URL attached to the label", label="Label target")

    # Tooltip annotation attached to label of an edge.
    # This is used only if the edge has a <html:a rel="attr">URL</html:a>
    # or <html:a rel="attr">labelURL</html:a> attribute.
    labeltooltip = Str("", desc="tooltip annotation attached to label of an "
        "edge", label="Label tooltip")

    # If <html:a rel="attr">labelURL</html:a> is defined, this is the link used for the label
    # of an edge. This value overrides any <html:a rel="attr">URL</html:a>
    # defined for the edge.
    labelURL = Str(desc="link used for the label of an edge")

	# Specifies layers in which the node or edge is present.
    layer = layer_trait

	# Preferred edge length, in inches.
    len = Float(1.0, desc="preferred edge length, in inches") #0.3(fdp)

    # Logical head of an edge. When compound is true, if lhead is defined and
    # is the name of a cluster containing the real head, the edge is clipped to
    # the boundary of the cluster.
    lhead = Str(desc="Logical head of an edge")

    # Label position, in points. The position indicates the center of the label.
    lp = point_trait

    # Logical tail of an edge. When compound is true, if ltail is defined and
    # is the name of a cluster containing the real tail, the edge is clipped to
    # the boundary of the cluster.
    ltail = Str(desc="logical tail of an edge")

	# Minimum edge length (rank difference between head and tail).
    minlen = Int(1, desc="minimum edge length")

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

    # Edges with the same head and the same <html:a rel="attr">samehead</html:a> value are aimed
    # at the same point on the head.
    # See <html:a rel="note">undirected</html:a>.
    samehead = Str("", desc="dges with the same head and the same samehead "
        "value are aimed at the same point on the head")

    # Edges with the same tail and the same <html:a rel="attr">sametail</html:a> value are aimed
    # at the same point on the tail.
    # See <html:a rel="note">undirected</html:a>.
    sametail = Str("", desc="edges with the same tail and the same sametail "
        "value are aimed at the same point on the tail")

	# Print guide boxes in PostScript at the beginning of
	# routesplines if 1, or at the end if 2. (Debugging)
    showboxes = showboxes_trait

    # Set style for node or edge. For cluster subgraph, if "filled", the
    # cluster box's background is filled.
    style = ListStr(desc="style for node or edge")

    # If <html:span class="val">true</html:span>, the tail of an edge is clipped to the boundary of the tail node;
    # otherwise, the end of the edge goes to the center of the node, or the
    # center of a port, if applicable.
    tailclip = Bool(True, desc="tail of an edge to be clipped to the boundary "
        "of the tail node")

	# Synonym for <html:a rel="attr">tailURL</html:a>.
    tailhref = Alias("tailURL", desc="synonym for tailURL")

	# Text label to be placed near tail of edge.
	# See <html:a rel="note">undirected</html:a>.
    taillabel = Str(desc="text label to be placed near tail of edge")

    # Indicates where on the tail node to attach the tail of the edge.
    tailport = port_pos_trait

    # If the edge has a tailURL, this attribute determines which window of the
    # browser is used for the URL. Setting it to "_graphviz" will open a new
    # window if it doesn't already exist, or reuse it if it does. If undefined,
    # the value of the target is used.
    tailtarget = Str(desc="which window of the browser is used for the URL")

	# Tooltip annotation attached to the tail of an edge. This is used only
	# if the edge has a <html:a rel="attr">tailURL</html:a> attribute.
    tailtooltip = Str("", desc="tooltip annotation attached to the tail of an "
        "edge", label="Tail tooltip")

    # If <html:a rel="attr">tailURL</html:a> is defined, it is
    # output as part of the tail label of the edge.
    # Also, this value is used near the tail node, overriding any
    # <html:a rel="attr">URL</html:a> value.
    # See <html:a rel="note">undirected</html:a>.
    tailURL = Str("", desc="output as part of the tail label of the edge",
        label="Tail URL")

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

    # Weight of edge. In dot, the heavier the weight, the shorter, straighter
    # and more vertical the edge is.
    weight = Float(1.0, desc="weight of edge")

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        Tabbed(
            Group(["style", "layer", "color", "colorscheme", "dir",
                "arrowsize", "constraint", "decorate", "showboxes", "tooltip",
                "edgetooltip", "edgetarget", "target", "comment"],
                label="Edge"),
            Group(["label", "fontname", "fontsize", "fontcolor", "nojustify",
                "labeltarget", "labelfloat", "labelfontsize",
                "labeltooltip", "labelangle", "lp", "labelURL",
                "labelfontname", "labeldistance", "labelfontcolor",
                "labelhref"],
                label="Label"),
            Group(["minlen", "weight", "len", "pos"], label="Dimension"),
            Group(["arrowhead", "samehead", "headURL", "headtooltip",
                "headclip", "headport", "headlabel", "headtarget", "lhead",
                "headhref"],
                label="Head"),
            Group(["arrowtail", "tailtarget", "tailhref", "ltail", "sametail",
                "tailport", "taillabel", "tailtooltip", "tailURL", "tailclip"],
                label="Tail"),
            Group(["URL", "href", "edgeURL", "edgehref"], label="URL"),
            Group(["_draw_", "_ldraw_", "_hdraw_", "_tdraw_", "_hldraw_",
                "_tldraw_"], label="Xdot")
        ),
        title="Edge", id="godot.edge", buttons=["OK", "Cancel", "Help"],
        resizable=True
    )

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, from_node, to_node, **traits):
        """ Return a new Edge instance. """

        self.from_node = from_node
        self.to_node = to_node

        super(Container, self).__init__(**traits)


    def __str__(self):
        """ Return a string representing the edge when requested by str()
        (or print).

        @rtype:  string
        @return: String representing the edge.

        """

        attrs = []
        for trait_name in edge_attrs:
            value = getattr(self, trait_name)
            if value != self.trait(trait_name).default:
                attrs.append('%s="%s"' % (trait_name, str(value)))

        if attrs:
            attrstr = "[%s]" % ", ".join(attrs)
            return "%s%s %s %s%s %s;\n" % \
                (self.from_node.ID, self.tailport, self.conn, \
                 self.to_node.ID, self.headport, attrstr)
        else:
            return "%s%s %s %s%s;\n" % \
                (self.from_node.ID, self.tailport, self.conn, \
                 self.to_node.ID, self.headport)


    def get_edge_attributes(self):
        """ Return the attributes of an edge.

        @rtype:  list
        @return: List of attributes specified tuples in the form (attr, value).

        """

        return [
#            (edge_attr, self.get_attr(edge_attr)) \
#            for edge_attr in EDGE_ATTRIBUTES
        ]

#------------------------------------------------------------------------------
#  Edge table editor:
#------------------------------------------------------------------------------

edge_table_editor = TableEditor(
    columns=[
        ObjectColumn(name="from_node", label="From",
            editor=InstanceEditor(name="_nodes", editable=False),
            format_func=lambda obj: obj.ID),
        ObjectColumn(name="to_node", label="To",
            editor=InstanceEditor(name="_nodes", editable=False),
            format_func=lambda obj: obj.ID),
        ObjectColumn(name="label"),
        ObjectColumn(name="style"),
        ObjectColumn(name="arrowsize"),
        ObjectColumn(name="weight"),
        ObjectColumn(name="len"),
        ObjectColumn(name="headlabel"),
        ObjectColumn(name="arrowhead"),
        ObjectColumn(name="taillabel"),
        ObjectColumn(name="arrowtail")
    ],
    other_columns = [  # not initially displayed
        ObjectColumn(name="color"),
        ObjectColumn(name="lp"),
        ObjectColumn(name="pos"),
        ObjectColumn(name="dir"),
        ObjectColumn(name="minlen"),
        ObjectColumn(name="colorscheme"),
        ObjectColumn(name="constraint"),
        ObjectColumn(name="decorate"),
        ObjectColumn(name="showboxes"),
        ObjectColumn(name="ltail"),
        ObjectColumn(name="lhead"),
    ],
    show_toolbar=True, deletable=True,
    filters=[EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate],
    search=RuleTableFilter(),
#    row_factory=edge_factory,
#    row_factory_kw={"__table_editor__": ""}
)

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    edge = Edge(Node("node1"), Node("node2"))
    edge.configure_traits()
    print edge

# EOF +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
