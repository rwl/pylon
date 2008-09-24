#------------------------------------------------------------------------------
#  Copyright (C) 2007 Richard W. Lincoln
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; version 2 dated June, 1991.
#
#  This software is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANDABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#------------------------------------------------------------------------------

#  Generated from Attributes.ecore on Wed 27/08/2008 at 09:14

"""
mixed

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    HasTraits, Instance, List, Any


from ecore.e_string_to_string_map_entry import EStringToStringMapEntry

from ecore.e_string_to_string_map_entry import EStringToStringMapEntry

#------------------------------------------------------------------------------
#  "DocumentRoot" class:
#------------------------------------------------------------------------------

class DocumentRoot(HasTraits):
    """
    mixed

    """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # attributexmlns:prefix
#    xmlns_prefix_map = List(Instance(EStringToStringMapEntry))
#
#
#    # attributexsi:schemaLocation
#    xsi_schema_location = List(Instance(EStringToStringMapEntry))
#
#
#    # elementWildcard:mixed
#    mixed = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Style of
#arrowhead on the head node of an edge.
#					See also the <html:a rel="attr">dir</html:a> attribute,
#					and the <html:a rel="note">undirected</html:a> note.
#				</html:p>
#			attributearrowhead##targetNamespace
#    arrowhead = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Multiplicative
#scale factor for arrowheads.
#				</html:p>
#			attributearrowsize##targetNamespace
#    arrowsize = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Style of
#arrowhead on the tail node of an edge.
#					See also the <html:a rel="attr">dir</html:a> attribute,
#					and the <html:a rel="note">undirected</html:a> note.
#				</html:p>
#			attributearrowtail##targetNamespace
#    arrowtail = Any
#
#    # attributebb##targetNamespace
#    bb = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					When attached
#to the root graph, this color is used as the background for
#					entire canvas. When a cluster attribute, it is used as the initial
#					background for the cluster. If a cluster has a filled
#					<html:a rel="attr">style</html:a>, the
#					cluster's <html:a rel="attr">fillcolor</html:a> will overlay the
#					background color.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If no background color is specified for the root graph, no graphics
#					operation are performed on the background. This works fine for
#					PostScript but for bitmap output, all bits are initialized to something.
#					This means that when the bitmap output is included in some other
#					document, all of the bits within the bitmap's bounding box will be
#					set, overwriting whatever color or graphics where already on the page.
#					If this effect is not desired, and you only want to set bits explicitly
#					assigned in drawing the graph, set <html:a rel="attr">bgcolor</html:a>="transparent".
#				</html:p>
#			attributebgcolor##targetNamespace
#    bgcolor = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If true, the
#drawing is centered in the output canvas.
#				</html:p>
#			attributecenter##targetNamespace
#    center = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Specifies the
#character encoding used when interpreting string input
#					as a text label. The default value is <html:span class="val">UTF-8</html:span>.
#					The other legal value is <html:span class="val">iso-8859-1</html:span> or,
#					equivalently,
#					<html:span class="val">Latin1</html:span>. The <html:a rel="attr">charset</html:a> attribute is case-insensitive.
#					Note that if the character encoding used in the input does not
#					match the <html:a rel="attr">charset</html:a> value, the resulting output may be very strange.
#				</html:p>
#			attributecharset##targetNamespace
#    charset = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Mode used for
#handling clusters. If <html:a rel="attr">clusterrank</html:a> is <html:span class="val">local</html:span>, a
#					subgraph whose name begins with "cluster" is given special treatment.
#					The subgraph is laid out separately, and then integrated as a unit into
#					its parent graph, with a bounding rectangle drawn about it.
#					If the cluster has a <html:a rel="attr">label</html:a> parameter, this label
#					is displayed within the rectangle.
#					Note also that there can be clusters within clusters.
#					At present, the modes <html:span class="val">global</html:span> and <html:span class="val">none</html:span>
#					appear to be identical, both turning off the special cluster processing.
#				</html:p>
#			dotattributeclusterrank##targetNamespace
#    clusterrank = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Basic drawing
#color for graphics, not text. For the latter, use the
#					<html:a rel="attr">fontcolor</html:a> attribute.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					For edges, the value
#					can either be a single <html:a rel="type">color</html:a> or a <html:a rel="type">colorList</html:a>.
#					In the latter case, the edge is drawn using parallel splines or lines,
#					one for each color in the list, in the order given.
#					The head arrow, if any, is drawn using the first color in the list,
#					and the tail arrow, if any, the second color. This supports the common
#					case of drawing opposing edges, but using parallel splines instead of
#					separately routed multiedges.
#				</html:p>
#			attributecolor##targetNamespace
#    color = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					This attribute
#specifies a color scheme namespace. If defined, it specifies
#					the context for interpreting color names. In particular, if a
#					<html:a rel="type">color</html:a> value has form <html:code>xxx</html:code> or <html:code>//xxx</html:code>,
#					then the color <html:code>xxx</html:code> will be evaluated according to the current color scheme.
#					If no color scheme is set, the standard X11 naming is used.
#					For example, if <html:code>colorscheme=bugn9</html:code>, then <html:code>color=7</html:code>
#					is interpreted as <html:code>/bugn9/7</html:code>.
#				</html:p>
#			attributecolorscheme##targetNamespace
#    colorscheme = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Comments are
#inserted into output. Device-dependent.
#				</html:p>
#			attributecomment##targetNamespace
#    comment = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If <html:span
#class="val">true</html:span>, allow edges between clusters. (See <html:a rel="attr">lhead</html:a> and <html:a rel="attr">ltail</html:a> below.)
#				</html:p>
#			dotattributecompound##targetNamespace
#    compound = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If <html:span
#class="val">true</html:span>, use edge concentrators.
#				</html:p>
#			dotattributeconcentrate##targetNamespace
#    concentrate = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If <html:span
#class="val">false</html:span>, the edge is not used in ranking the nodes.
#				</html:p>
#			dotattributeconstraint##targetNamespace
#    constraint = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Factor damping
#force motions. On each iteration, a nodes movement
#					is limited to this factor of its potential motion. By being less than
#					1.0, the system tends to "cool", thereby preventing cycling.
#				</html:p>
#			neatoattributeDamping##targetNamespace
#    damping = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If <html:span
#class="val">true</html:span>, attach edge label to edge by a 2-segment
#					polyline, underlining the label, then going to the closest point of spline.
#				</html:p>
#			attributedecorate##targetNamespace
#    decorate = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					This specifies
#the distance between nodes in separate connected
#					components. If set too small, connected components may overlap.
#					Only applicable if <html:a rel="attr">pack</html:a>=false.
#				</html:p>
#			neatoattributedefaultdist##targetNamespace
#    defaultdist = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Set the number
#of dimensions used for the layout. The maximum value
#					allowed is 10.
#				</html:p>
#			fdp neatoattributedim##targetNamespace
#    dim = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Set edge type
#for drawing arrowheads. This indicates which ends of the
#					edge should be decorated with an arrowhead. The actual style of the
#					arrowhead can be specified using the <html:a rel="attr">arrowhead</html:a>
#					and <html:a rel="attr">arrowtail</html:a> attributes.
#					See <html:a rel="note">undirected</html:a>.
#				</html:p>
#			attributedir##targetNamespace
#    dir = Any
#
#    # neatoattributediredgeconstraints##targetNamespace
#    diredgeconstraints = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Distortion
#factor for <html:a rel="attr">shape</html:a>=polygon.
#					Positive values cause top part to
#					be larger than bottom; negative values do the opposite.
#				</html:p>
#			attributedistortion##targetNamespace
#    distortion = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					This specifies
#the expected number of pixels per inch on a display device.
#					For bitmap output, this guarantees that text rendering will be
#					done more accurately, both in size and in placement. For SVG output,
#					it is used to guarantee that the dimensions in the output correspond to
#					the correct number of points or inches.
#				</html:p>
#			attributedpi##targetNamespace
#    dpi = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Synonym for
#<html:a rel="attr">edgeURL</html:a>.
#				</html:p>
#			svg mapattributeedgehref##targetNamespace
#    edgehref = Any
#
#    # svg mapattributeedgetarget##targetNamespace
#    edgetarget = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Tooltip
#annotation attached to the non-label part of an edge.
#					This is used only if the edge has a <html:a rel="attr">URL</html:a>
#					or <html:a rel="attr">edgeURL</html:a> attribute.
#				</html:p>
#			svg cmapattributeedgetooltip##targetNamespace
#    edgetooltip = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If <html:a
#rel="attr">edgeURL</html:a> is defined, this is the link used for the non-label
#					parts of an edge. This value overrides any <html:a rel="attr">URL</html:a>
#					defined for the edge.
#					Also, this value is used near the head or tail node unless overridden
#					by a <html:a rel="attr">headURL</html:a> or <html:a rel="attr">tailURL</html:a> value,
#					respectively.
#					See <html:a rel="note">undirected</html:a>.
#				</html:p>
#			svg mapattributeedgeURL##targetNamespace
#    edgeur_l = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Terminating
#condition. If the length squared of all energy gradients are
#					&lt; <html:a rel="attr">epsilon</html:a>, the algorithm stops.
#				</html:p>
#			neatoattributeepsilon##targetNamespace
#    epsilon = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Fraction to
#increase polygons (multiply
#					coordinates by 1 + esep) for purposes of spline edge routing.
#					This should normally be strictly less than
#					<html:a rel="attr">sep</html:a>.
#				</html:p>
#			neato circo fdpattributeesep##targetNamespace
#    esep = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Color used to
#fill the background of a node or cluster
#					assuming <html:a rel="attr">style</html:a>=filled.
#					If <html:a rel="attr">fillcolor</html:a> is not defined, <html:a rel="attr">color</html:a> is
#					used. (For clusters, if <html:a rel="attr">color</html:a> is not defined,
#					<html:a rel="attr">bgcolor</html:a> is used.) If this is not defined,
#					the default is used, except for
#					<html:a rel="attr">shape</html:a>=point or when the output
#					format is MIF,
#					which use black by default.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Note that a cluster inherits the root graph's attributes if defined.
#					Thus, if the root graph has defined a <html:a rel="attr">fillcolor</html:a>, this will override a
#					<html:a rel="attr">color</html:a> or <html:a rel="attr">bgcolor</html:a> attribute set for the cluster.
#				</html:p>
#			attributefillcolor##targetNamespace
#    fillcolor = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If true, the
#node size is specified by the values of the
#					<html:a rel="attr">width</html:a>
#					and <html:a rel="attr">height</html:a> attributes only
#					and is not expanded to contain the text label.
#				</html:p>
#			attributefixedsize##targetNamespace
#    fixedsize = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Color used for
#text.
#				</html:p>
#			attributefontcolor##targetNamespace
#    fontcolor = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Font used for
#text. This very much depends on the output format and, for
#					non-bitmap output such as PostScript or SVG, the availability of the font
#					when the graph is displayed or printed. As such, it is best to rely on
#					font faces that are generally available, such as Times-Roman, Helvetica or
#					Courier.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If Graphviz was built using the
#					<html:a href="http://pdx.freedesktop.org/~fontconfig/fontconfig-user.html">fontconfig library</html:a>, the latter library
#					will be used to search for the font. However, if the <html:a rel="attr">fontname</html:a> string
#					contains a slash character "/", it is treated as a pathname for the font
#					file, though font lookup will append the usual font suffixes.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If Graphviz does not use fontconfig, <html:a rel="attr">fontname</html:a> will be
#					considered the name of a Type 1 or True Type font file.
#					If you specify <html:code>fontname=schlbk</html:code>, the tool will look for a
#					file named  <html:code>schlbk.ttf</html:code> or <html:code>schlbk.pfa</html:code> or <html:code>schlbk.pfb</html:code>
#					in one of the directories specified by
#					the <html:a rel="attr">fontpath</html:a> attribute.
#					The lookup does support various aliases for the common fonts.
#				</html:p>
#			attributefontname##targetNamespace
#    fontname = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Allows user
#control of how basic fontnames are represented in SVG output.
#					If <html:a rel="attr">fontnames</html:a> is undefined or <html:span class="val">svg</html:span>,
#					the output will try to use known SVG fontnames. For example, the
#					default font <html:code>Times-Roman</html:code> will be mapped to the
#					basic SVG font <html:code>serif</html:code>. This can be overridden by setting
#					<html:a rel="attr">fontnames</html:a> to <html:span class="val">ps</html:span> or <html:span class="val">gd</html:span>.
#					In the former case, known PostScript font names such as
#					<html:code>Times-Roman</html:code> will be used in the output.
#					In the latter case, the fontconfig font conventions
#					are used. Thus, <html:code>Times-Roman</html:code> would be treated as
#					<html:code>Nimbus Roman No9 L</html:code>. These last two options are useful
#					with SVG viewers that support these richer fontname spaces.
#				</html:p>
#			svgattributefontnames##targetNamespace
#    fontnames = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Directory list
#used by libgd to search for bitmap fonts if Graphviz
#					was not built with the fontconfig library.
#					If <html:a rel="attr">fontpath</html:a> is not set, the environment
#					variable <html:code>DOTFONTPATH</html:code> is checked.
#					If that is not set, <html:code>GDFONTPATH</html:code> is checked.
#					If not set, libgd uses its compiled-in font path.
#					Note that fontpath is an attribute of the root graph.
#				</html:p>
#			attributefontpath##targetNamespace
#    fontpath = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Font size, in
#<html:a rel="note">points</html:a>, used for text.
#				</html:p>
#			attributefontsize##targetNamespace
#    fontsize = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If the end
#points of an edge belong to the same group, i.e., have the
#					same group attribute, parameters are set to avoid crossings and keep
#					the edges straight.
#				</html:p>
#			dotattributegroup##targetNamespace
#    group = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If <html:span
#class="val">true</html:span>, the head of an edge is clipped to the boundary of the head node;
#					otherwise, the end of the edge goes to the center of the node, or the
#					center of a port, if applicable.
#				</html:p>
#			attributeheadclip##targetNamespace
#    headclip = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Synonym for
#<html:a rel="attr">headURL</html:a>.
#				</html:p>
#			svg mapattributeheadhref##targetNamespace
#    headhref = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Text label to
#be placed near head of edge.
#					See <html:a rel="note">undirected</html:a>.
#				</html:p>
#			attributeheadlabel##targetNamespace
#    headlabel = Any
#
#    # attributeheadport##targetNamespace
#    headport = Any
#
#    # svg mapattributeheadtarget##targetNamespace
#    headtarget = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Tooltip
#annotation attached to the head of an edge. This is used only
#					if the edge has a <html:a rel="attr">headURL</html:a> attribute.
#				</html:p>
#			svg cmapattributeheadtooltip##targetNamespace
#    headtooltip = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If <html:a
#rel="attr">headURL</html:a> is defined, it is
#					output as part of the head label of the edge.
#					Also, this value is used near the head node, overriding any
#					<html:a rel="attr">URL</html:a> value.
#					See <html:a rel="note">undirected</html:a>.
#				</html:p>
#			svg mapattributeheadURL##targetNamespace
#    headur_l = Any
#
#    # attributeheight##targetNamespace
#    height = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Synonym for
#<html:a rel="attr">URL</html:a>.
#				</html:p>
#			svg ps ps2 mapattributehref##targetNamespace
#    href = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Gives the name
#of a file containing an image to be displayed inside
#					a node. The image file must be in one of the recognized formats,
#					typically JPEG, PNG, GIF or Postscript, and be able to be converted
#					into the desired output format.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Unlike with the <html:a rel="attr">shapefile</html:a> attribute,
#					the image is treated as node
#					content rather than the entire node. In particular, an image can
#					be contained in a node of any shape, not just a rectangle.
#				</html:p>
#			attributeimage##targetNamespace
#    image = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Attribute
#controlling how an image fills its
#					containing node. In general, the image is given its natural size,
#					(cf. <html:a rel="attr">dpi</html:a>),
#					and the node size is made large enough to contain its image, its
#					label, its margin, and its peripheries.
#					Its width and height will also be at least as large as its
#					minimum <html:a rel="attr">width</html:a> and <html:a rel="attr">height</html:a>.
#					If, however, <html:code>fixedsize=true</html:code>,
#					the width and height attributes specify the exact size of the node.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					During rendering, in the default case (<html:code>imagescale=false</html:code>),
#					the image retains its natural size.
#					If <html:span class="val">true</html:span>,
#					the image is uniformly scaled (i.e., its aspect ration is
#					preserved) to fit inside the node.
#					At least one dimension of the image will be as large as possible
#					given the size of the node.
#					When <html:span class="val">width</html:span>,
#					the width of the image is scaled to fill the node width.
#					The corresponding property holds when <html:tt>imagescale=height</html:tt>.
#					When <html:span class="val">both</html:span>,
#					both the height and the width are scaled separately to fill the node.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					In all cases, if a dimension of the image is larger than the
#					corresponding dimension of the node, that dimension of the
#					image is scaled down to fit the node. As with the case of
#					expansion, if <html:code>imagescale=true</html:code>, width and height are
#					scaled uniformly.
#				</html:p>
#			attributeimagescale##targetNamespace
#    imagescale = Any
#
#    # fdpattributeK##targetNamespace
#    k = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Text label
#attached to objects.
#					If a node's <html:a rel="attr">shape</html:a> is record, then the label can
#					have a <html:a href="http://www.graphviz.org/doc/info/shapes.html#record">special format</html:a>
#					which describes the record layout.
#				</html:p>
#			attributelabel##targetNamespace
#    label = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					This, along
#with <html:a rel="attr">labeldistance</html:a>, determine
#					where the
#					headlabel (taillabel) are placed with respect to the head (tail)
#					in polar coordinates. The origin in the coordinate system is
#					the point where the edge touches the node. The ray of 0 degrees
#					goes from the origin back along the edge, parallel to the edge
#					at the origin.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					The angle, in degrees, specifies the rotation from the 0 degree ray,
#					with positive angles moving counterclockwise and negative angles
#					moving clockwise.
#				</html:p>
#			attributelabelangle##targetNamespace
#    labelangle = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Multiplicative
#scaling factor adjusting the distance that
#					the headlabel (taillabel) is from the head (tail) node.
#					The default distance is 10 points. See <html:a rel="attr">labelangle</html:a>
#					for more details.
#				</html:p>
#			attributelabeldistance##targetNamespace
#    labeldistance = Any
#
#    # attributelabelfloat##targetNamespace
#    labelfloat = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Color used for
#headlabel and taillabel.
#					If not set, defaults to edge's fontcolor.
#				</html:p>
#			attributelabelfontcolor##targetNamespace
#    labelfontcolor = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Font used for
#headlabel and taillabel.
#					If not set, defaults to edge's fontname.
#				</html:p>
#			attributelabelfontname##targetNamespace
#    labelfontname = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Font size, in
#<html:a rel="note">points</html:a>, used for headlabel and taillabel.
#					If not set, defaults to edge's fontsize.
#				</html:p>
#			attributelabelfontsize##targetNamespace
#    labelfontsize = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Synonym for
#<html:a rel="attr">labelURL</html:a>.
#				</html:p>
#			attributelabelhref##targetNamespace
#    labelhref = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Justification
#for cluster labels. If <html:span class="val">r</html:span>, the label
#					is right-justified within bounding rectangle; if <html:span class="val">l</html:span>, left-justified;
#					else the label is centered.
#					Note that a subgraph inherits attributes from its parent. Thus, if
#					the root graph sets <html:a rel="attr">labeljust</html:a> to <html:span class="val">l</html:span>, the subgraph inherits
#					this value.
#				</html:p>
#			attributelabeljust##targetNamespace
#    labeljust = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Top/bottom
#placement of graph and cluster labels.
#					If the attribute is <html:span class="val">t</html:span>, place label at the top;
#					if the attribute is <html:span class="val">b</html:span>, place label at the bottom.
#					By default, root
#					graph labels go on the bottom and cluster labels go on the top.
#					Note that a subgraph inherits attributes from its parent. Thus, if
#					the root graph sets <html:a rel="attr">labelloc</html:a> to <html:span class="val">b</html:span>, the subgraph inherits
#					this value.
#				</html:p>
#			attributelabelloc##targetNamespace
#    labelloc = Any
#
#    # attributelabeltarget##targetNamespace
#    labeltarget = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Tooltip
#annotation attached to label of an edge.
#					This is used only if the edge has a <html:a rel="attr">URL</html:a>
#					or <html:a rel="attr">labelURL</html:a> attribute.
#				</html:p>
#			attributelabeltooltip##targetNamespace
#    labeltooltip = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If <html:a
#rel="attr">labelURL</html:a> is defined, this is the link used for the label
#					of an edge. This value overrides any <html:a rel="attr">URL</html:a>
#					defined for the edge.
#				</html:p>
#			attributelabelURL##targetNamespace
#    labelur_l = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If true, the
#graph is rendered in landscape mode. Synonymous with
#					<html:code>
#      <html:a rel="attr">rotate</html:a>=90</html:code> or
#					<html:code>
#      <html:a rel="attr">orientation</html:a>=landscape</html:code>.
#				</html:p>
#			attributelandscape##targetNamespace
#    landscape = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Specifies
#layers in which the node or edge is present.
#				</html:p>
#			attributelayer##targetNamespace
#    layer = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Specifies a
#linearly ordered list of layer names attached to the graph
#					The graph is then output in separate layers. Only those components
#					belonging to the current output layer appear. For more information,
#					see the page <html:a href="http://www.graphviz.org/Documentation/html/layers/">How to use drawing layers (overlays)</html:a>.
#				</html:p>
#			attributelayers##targetNamespace
#    layers = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Specifies the
#separator characters used to split the
#					<html:a rel="attr">layers </html:a>attribute into a list of layer names.
#				</html:p>
#			attributelayersep##targetNamespace
#    layersep = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Preferred edge
#length, in inches.
#				</html:p>
#			attributelen##targetNamespace
#    len = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Specifies
#strictness of level constraints in neato
#					when <html:code>
#      <html:a rel="attr">mode</html:a>="ipsep" or "hier"</html:code>.
#					Larger positive values mean stricter constraints, which demand more
#					separation between levels. On the other hand, negative values will relax
#					the constraints by allowing some overlap between the levels.
#				</html:p>
#			attributelevelsgap##targetNamespace
#    levelsgap = Any
#
#    # attributelhead##targetNamespace
#    lhead = Any
#
#    # attributelp##targetNamespace
#    lp = Any
#
#    # attributeltail##targetNamespace
#    ltail = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					For graphs,
#this sets x and y margins of canvas, in inches. If the margin
#					is a single double, both margins are set equal to the given value.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Note that the margin is not part of the drawing but just empty space
#					left around the drawing. It basically corresponds to a translation of
#					drawing, as would be necessary to center a drawing on a page. Nothing
#					is actually drawn in the margin. To actually extend the background of
#					a drawing, see the <html:a rel="attr">pad</html:a> attribute.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					For nodes, this attribute specifies space left around the node's label.
#					By default, the value is <html:code>0.11,0.055</html:code>.
#				</html:p>
#			attributemargin##targetNamespace
#    margin = Any
#
#    # attributemaxiter##targetNamespace
#    maxiter = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Multiplicative
#scale factor used to alter the MinQuit (default = 8)
#					and MaxIter (default = 24) parameters used during crossing
#					minimization. These correspond to the
#					number of tries without improvement before quitting and the
#					maximum number of iterations in each pass.
#				</html:p>
#			attributemclimit##targetNamespace
#    mclimit = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Specifies the
#minimum separation between all nodes.
#				</html:p>
#			attributemindist##targetNamespace
#    mindist = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#				Minimum edge
#length (rank difference between head and tail).
#				</html:p>
#			attributeminlen##targetNamespace
#    minlen = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Technique for
#optimizing the layout. If <html:a rel="attr">mode</html:a> is <html:span class="val">major</html:span>,
#					neato uses stress majorization. If <html:a rel="attr">mode</html:a> is <html:span class="val">KK</html:span>,
#					neato uses a version of the gradient descent method. The only advantage
#					to the latter technique is that it is sometimes appreciably faster for
#					small (number of nodes &lt; 100) graphs. A significant disadvantage is that
#					it may cycle.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					There are two new, experimental modes in neato, <html:span class="val">hier</html:span>, which adds a top-down
#					directionality similar to the layout used in dot, and <html:span class="val">ipsep</html:span>, which
#					allows the graph to specify minimum vertical and horizontal distances
#					between nodes. (See the <html:a rel="attr">sep</html:a> attribute.)
#				</html:p>
#			attributemode##targetNamespace
#    mode = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					This value
#specifies how the distance matrix is computed for the input
#					graph. The distance matrix specifies the ideal distance between every
#					pair of nodes. neato attemps to find a layout which best achieves
#					these distances. By default, it uses the length of the shortest path,
#					where the length of each edge is given by its <html:a rel="attr">len</html:a>
#					attribute. If <html:a rel="attr">model</html:a> is <html:span class="val">circuit</html:span>, neato uses the
#					circuit resistance
#					model to compute the distances. This tends to emphasize clusters. If
#					<html:a rel="attr">model</html:a> is <html:span class="val">subset</html:span>, neato uses the subset model. This sets the
#					edge length to be the number of nodes that are neighbors of exactly one
#					of the end points, and then calculates the shortest paths. This helps
#					to separate nodes with high degree.
#				</html:p>
#			attributemodel##targetNamespace
#    model = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If Graphviz is
#built with MOSEK defined, mode=ipsep and mosek=true,
#					the Mosek software (www.mosek.com) is use to solve the ipsep constraints.
#				</html:p>
#			attributemosek##targetNamespace
#    mosek = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Minimum space
#between two adjacent nodes in the same rank, in inches.
#				</html:p>
#			attributenodesep##targetNamespace
#    nodesep = Any
#
#    # attributenojustify##targetNamespace
#    nojustify = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If set,
#normalize coordinates of final
#					layout so that the first point is at the origin, and then rotate the
#					layout so that the first edge is horizontal.
#				</html:p>
#			attributenormalize##targetNamespace
#    normalize = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Used to set
#number of iterations in
#					network simplex applications, used in
#					computing node x coordinates.
#					If defined, # iterations =  <html:a rel="attr">nslimit</html:a> * # nodes;
#					otherwise,  # iterations = MAXINT.
#				</html:p>
#			attributenslimit##targetNamespace
#    nslimit = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Used to set
#number of iterations in
#					network simplex applications, used for ranking nodes.
#					If defined, # iterations =  <html:a rel="attr">nslimit1</html:a> * # nodes;
#					otherwise,  # iterations = MAXINT.
#				</html:p>
#			attributenslimit1##targetNamespace
#    nslimit1 = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If "out" for a
#graph G, and n is a node in G, then edges n-&gt;* appear
#					left-to-right in the same order in which they are defined.
#					If "in", the edges *-&gt;n appear
#					left-to-right in the same order in which they are defined for all
#					nodes n.
#				</html:p>
#			attributeordering##targetNamespace
#    ordering = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Specify order
#in which nodes and edges are drawn.
#				</html:p>
#			attributeoutputorder##targetNamespace
#    outputorder = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Determines if
#and how node overlaps should be removed. Nodes are first
#					enlarged using the <html:a rel="attr">sep</html:a> attribute.
#					If <html:span class="val">true</html:span>, overlaps are retained.
#					If the value is <html:span class="val">scale</html:span>, overlaps are removed by uniformly scaling in x and y.
#					If the value converts to <html:span class="val">false</html:span>, node overlaps are removed by a
#					Voronoi-based technique.
#					If the value is <html:span class="val">scalexy</html:span>, x and y are separately
#					scaled to remove overlaps.
#					If the value is <html:span class="val">orthoxy</html:span> or <html:span class="val">orthoyx</html:span>, overlaps
#					are moved by optimizing two constraint problems, one for the x axis and
#					one for the y. The suffix indicates which axis is processed first.
#					If the value is <html:span class="val">ortho</html:span>, the technique is similar to <html:span class="val">orthoxy</html:span> except a
#					heuristic is used to reduce the bias between the two passes.
#					If the value is <html:span class="val">ortho_yx</html:span>, the technique is the same as <html:span class="val">ortho</html:span>, except
#					the roles of x and y are reversed.
#					The values <html:span class="val">portho</html:span>, <html:span class="val">porthoxy</html:span>, <html:span class="val">porthoxy</html:span>, and <html:span class="val">portho_yx</html:span> are similar
#					to the previous four, except only pseudo-orthogonal ordering is
#					enforced.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If the value is <html:span class="val">compress</html:span>, the layout will be scaled down as much as
#					possible without introducing any overlaps, obviously assuming there are
#					none to begin with.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If the value is <html:span class="val">ipsep</html:span>, and the layout is done by neato with
#					<html:a rel="attr">mode</html:a>="ipsep", the overlap removal constraints are
#					incorporated into the layout algorithm itself.
#					N.B. At present, this only supports one level of clustering.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If the value is <html:span class="val">vpsc</html:span>, overlap removal is similarly to <html:span class="val">ortho</html:span>, except
#					quadratic optimization is used to minimize node displacement.
#					N.B. At present, this mode only works when <html:a rel="attr">mode</html:a>="ipsep".
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Except for fdp, the layouts assume <html:code>overlap="true"</html:code> as the default.
#					Fdp first uses a number of passes using built-in, force-directed technique
#					to remove overlaps. Thus, fdp accepts <html:a rel="attr">overlap</html:a> with an integer
#					prefix followed by a colon, specifying the number of tries. If there is
#					no prefix, no initial tries will be performed. If there is nothing following
#					a colon, none of the above methods will be attempted. By default, fdp
#					uses <html:code>overlap="9:portho"</html:code>. Note that <html:code>overlap="true"</html:code>,
#					<html:code>overlap="0:true"</html:code> and <html:code>overlap="0:"</html:code> all turn off all overlap
#					removal.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Except for the Voronoi method, all of these transforms preserve the
#					orthogonal ordering of the original layout. That is, if the x coordinates
#					of two nodes are originally the same, they will remain the same, and if
#					the x coordinate of one node is originally less than the x coordinate of
#					another, this relation will still hold in the transformed layout. The
#					similar properties hold for the y coordinates.
#					This is not quite true for the "porth*" cases. For these, orthogonal
#					ordering is only preserved among nodes related by an edge.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					<html:b>NOTE</html:b>The methods <html:span class="val">orthoxy</html:span> and <html:span class="val">orthoyx</html:span> are still evolving. The semantics of these may change, or these methods may disappear altogether.
#				</html:p>
#			attributeoverlap##targetNamespace
#    overlap = Any
#
#    # attributepack##targetNamespace
#    pack = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					This indicates
#the granularity and method used for packing
#					(cf. <html:a rel="type">packMode</html:a>). Note that defining
#					<html:a rel="attr">packmode</html:a> will automatically turn on packing as though one had
#					set <html:code>pack=true</html:code>.
#				</html:p>
#			attributepackmode##targetNamespace
#    packmode = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					The pad
#attribute specifies how much, in inches, to extend the
#					drawing area around the minimal area needed to draw the graph.
#					If the pad is a single double, both the x and y pad values are set
#					equal to the given value. This area is part of the
#					drawing and will be filled with the background color, if appropriate.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Normally, a small pad is used for aesthetic reasons, especially when
#					a background color is used, to avoid having nodes and edges abutting
#					the boundary of the drawn region.
#				</html:p>
#			attributepad##targetNamespace
#    pad = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Width and
#height of output pages, in inches. If this is set and is
#					smaller than the size of the layout, a rectangular array of pages of
#					the specified page size is overlaid on the layout, with origins
#					aligned in the lower-left corner, thereby partitioning the layout
#					into pages. The pages are then produced one at a time, in
#					<html:a rel="attr">pagedir</html:a> order.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					At present, this only works for PostScript output. For other types of
#					output, one should use another tool to split the output into multiple
#					output files. Or use the <html:a rel="attr">viewport</html:a> to generate
#					multiple files.
#				</html:p>
#			attributepage##targetNamespace
#    page = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If the <html:a
#rel="attr">page</html:a> attribute is set and applicable,
#					this attribute specifies the order in which the pages are emitted.
#					This is limited to one of the 8 row or column major orders.
#				</html:p>
#			attributepagedir##targetNamespace
#    pagedir = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Color used to
#draw the bounding box around a cluster.
#					If <html:a rel="attr">pencolor</html:a> is not defined, <html:a rel="attr">color</html:a> is
#					used. If this is not defined, <html:a rel="attr">bgcolor</html:a> is used.
#					If this is not defined, the default is used.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Note that a cluster inherits the root graph's attributes if defined.
#					Thus, if the root graph has defined a <html:a rel="attr">pencolor</html:a>, this will override a
#					<html:a rel="attr">color</html:a> or <html:a rel="attr">bgcolor</html:a> attribute set for the cluster.
#				</html:p>
#			attributepencolor##targetNamespace
#    pencolor = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Set number of
#peripheries used in polygonal shapes and cluster
#					boundaries. Note that
#					<html:a href="http://www.graphviz.org/doc/info/shapes.html#epsf">user-defined shapes</html:a> are treated as a
#					form of box shape, so the default
#					peripheries value is 1 and the user-defined shape will be drawn in
#					a bounding rectangle. Setting <html:code>peripheries=0</html:code> will turn this off.
#					Also, 1 is the maximum peripheries value for clusters.
#				</html:p>
#			attributeperipheries##targetNamespace
#    peripheries = Any
#
#    # attributepin##targetNamespace
#    pin = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Position of
#node, or spline control points.
#					For nodes, the position indicates the center of the node.
#					On output, the coordinates are in <html:a href="#points">points</html:a>.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					In neato and fdp, pos can be used to set the initial position of a node.
#					By default, the coordinates are assumed to be in inches. However, the
#					<html:a href="http://www.graphviz.org/doc/info/command.html#d:s">-s</html:a> command line flag can be used to specify
#					different units.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					When the <html:a href="http://www.graphviz.org/doc/info/command.html#d:n">-n</html:a> command line flag is used with
#					neato, it is assumed the positions have been set by one of the layout
#					programs, and are therefore in points. Thus, <html:code>neato -n</html:code> can accept
#					input correctly without requiring a <html:code>-s</html:code> flag and, in fact,
#					ignores any such flag.
#				</html:p>
#			attributepos##targetNamespace
#    pos = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If <html:a
#rel="attr">quantum</html:a> &gt; 0.0, node label dimensions
#					will be rounded to integral multiples of the quantum.
#				</html:p>
#			attributequantum##targetNamespace
#    quantum = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Rank
#constraints on the nodes in a subgraph.
#					If <html:span class="val">same</html:span>, all nodes are placed on the same rank.
#					If <html:span class="val">min</html:span>, all nodes are placed on the minimum rank.
#					If <html:span class="val">source</html:span>, all nodes are placed on the minimum rank, and
#					the only nodes on the minimum rank belong to some subgraph whose
#					rank attribute is "source" or "min".
#					Analogous criteria hold for <html:a rel="attr">rank</html:a>=<html:span class="val">max</html:span> and <html:a rel="attr">rank</html:a>=<html:span class="val">sink</html:span>.
#					(Note: the
#					minimum rank is topmost or leftmost, and the maximum rank is bottommost
#					or rightmost.)
#				</html:p>
#			attributerank##targetNamespace
#    rank = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Sets direction
#of graph layout. For example, if <html:a rel="attr">rankdir</html:a>="LR",
#					and barring cycles, an edge <html:code>T -&gt; H;</html:code> will go
#					from left to right. By default, graphs are laid out from top to bottom.
#				</html:p>
#			attributerankdir##targetNamespace
#    rankdir = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					In dot, this
#gives the desired rank separation, in inches. This is
#					the minimum vertical distance between the bottom of the nodes in one
#					rank and the tops of nodes in the next. If the value
#					contains "equally", the centers of all ranks are spaced equally apart.
#					Note that both
#					settings are possible, e.g., ranksep = "1.2 equally".
#					In twopi, specifies radial separation of concentric circles.
#				</html:p>
#			attributeranksep##targetNamespace
#    ranksep = Any
#
#    # attributeratio##targetNamespace
#    ratio = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Rectangles for
#fields of records, in <html:a rel="note">points</html:a>.
#				</html:p>
#			attributerects##targetNamespace
#    rects = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If true, force
#polygon to be regular.
#				</html:p>
#			attributeregular##targetNamespace
#    regular = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If true and
#there are multiple clusters, run cross
#					minimization a second time.
#				</html:p>
#			attributeremincross##targetNamespace
#    remincross = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					This is a
#synonym for the <html:a rel="attr">dpi</html:a> attribute.
#				</html:p>
#			attributeresolution##targetNamespace
#    resolution = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					This specifies
#nodes to be used as the center of the
#					layout and the root of the generated spanning tree. As a graph attribute,
#					this gives the name of the node. As a node attribute (circo only), it
#					specifies that the node should be used as a central node. In twopi,
#					this will actually be the central node. In circo, the block containing
#					the node will be central in the drawing of its connected component.
#					If not defined,
#					twopi will pick a most central node, and circo will pick a random node.
#				</html:p>
#			attributeroot##targetNamespace
#    root = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If 90, set
#drawing orientation to landscape.
#				</html:p>
#			attributerotate##targetNamespace
#    rotate = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Edges with the
#same head and the same <html:a rel="attr">samehead</html:a> value are aimed
#					at the same point on the head.
#					See <html:a rel="note">undirected</html:a>.
#				</html:p>
#			attributesamehead##targetNamespace
#    samehead = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Edges with the
#same tail and the same <html:a rel="attr">sametail</html:a> value are aimed
#					at the same point on the tail.
#					See <html:a rel="note">undirected</html:a>.
#				</html:p>
#			attributesametail##targetNamespace
#    sametail = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If the input
#graph defines the <html:a rel="attr">
#      <html:a rel="attr">vertices</html:a>
#    </html:a>
#					attribute, and output is dot or xdot, this gives
#					the number of points used for a node whose shape is a circle or ellipse.
#					It plays the same role in neato, when adjusting the layout to avoid
#					overlapping nodes, and in image maps.
#				</html:p>
#			attributesamplepoints##targetNamespace
#    samplepoints = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					During network
#simplex, maximum number of edges with negative cut values
#					to search when looking for one with minimum cut value.
#				</html:p>
#			attributesearchsize##targetNamespace
#    searchsize = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Fraction to
#increase polygons (multiply
#					coordinates by 1 + sep) for purposes of determining overlap. Guarantees
#					a minimal non-zero distance between nodes.
#					If unset but <html:a rel="attr">esep</html:a> is defined, <html:a rel="attr">sep</html:a> will be
#					set to <html:code>esep/0.8</html:code>. If <html:a rel="attr">esep</html:a> is unset, the default value
#					is used.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					When <html:a rel="attr">overlap</html:a>="ipsep" or "vpsc",
#					<html:a rel="attr">sep</html:a> gives a minimum distance, in inches, to be left between nodes.
#					In this case, if <html:a rel="attr">sep</html:a> is a pointf, the x and y separations can be
#					specified separately.
#				</html:p>
#			attributesep##targetNamespace
#    sep = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Set the shape
#of a node.
#				</html:p>
#			attributeshape##targetNamespace
#    shape = Any
#
#    # attributeshapefile##targetNamespace
#    shapefile = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Print guide
#boxes in PostScript at the beginning of
#					routesplines if 1, or at the end if 2. (Debugging)
#				</html:p>
#			attributeshowboxes##targetNamespace
#    showboxes = Any
#
#    # attributesides##targetNamespace
#    sides = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Maximum width
#and height of drawing, in inches.
#					If defined and the drawing is too large, the drawing is uniformly
#					scaled down so that it fits within the given size.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If <html:a rel="attr">size</html:a> ends in an exclamation point (<html:tt>!</html:tt>),
#					then it is taken to be
#					the desired size. In this case, if both dimensions of the drawing are
#					less than <html:a rel="attr">size</html:a>, the drawing is scaled up uniformly until at
#					least one dimension equals its dimension in <html:a rel="attr">size</html:a>.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Note that there is some interaction between the <html:a rel="attr">size</html:a> and
#					<html:a rel="attr">ratio</html:a> attributes.
#				</html:p>
#			attributesize##targetNamespace
#    size = Any
#
#    # attributeskew##targetNamespace
#    skew = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Controls how,
#and if, edges are represented. If true, edges are drawn as
#					splines routed around nodes; if false, edges are drawn as line segments.
#					If set to "", no edges are drawn at all.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					(1 March 2007) The values <html:span class="val">line</html:span> and <html:span class="val">spline</html:span> can be
#					used as synonyms for <html:span class="val">false</html:span> and <html:span class="val">true</html:span>, respectively.
#					In addition, the value <html:span class="val">polyline</html:span> specifies that edges should be
#					drawn as polylines.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					By default, the attribute is unset. How this is interpreted depends on
#					the layout. For dot, the default is to draw edges as splines. For all
#					other layouts, the default is to draw edges as line segments. Note that
#					for these latter layouts, if <html:code>splines="true"</html:code>, this
#					requires non-overlapping nodes (cf. <html:a rel="attr">overlap</html:a>).
#					If fdp is used for layout and <html:tt>splines="compound"</html:tt>, then the edges are
#					drawn to avoid clusters as well as nodes.
#				</html:p>
#			attributesplines##targetNamespace
#    splines = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Parameter used
#to determine the initial layout of nodes. If unset, the
#					nodes are randomly placed in a unit square with
#					the same seed is always used for the random number generator, so the
#					initial placement is repeatable.
#				</html:p>
#			attributestart##targetNamespace
#    start = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Set style for
#node or edge. For cluster subgraph, if "filled", the
#					cluster box's background is filled.
#				</html:p>
#			attributestyle##targetNamespace
#    style = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					A URL or
#pathname specifying an XML style sheet, used in SVG output.
#				</html:p>
#			attributestylesheet##targetNamespace
#    stylesheet = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If <html:span
#class="val">true</html:span>, the tail of an edge is clipped to the boundary of the tail node;
#					otherwise, the end of the edge goes to the center of the node, or the
#					center of a port, if applicable.
#				</html:p>
#			attributetailclip##targetNamespace
#    tailclip = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Synonym for
#<html:a rel="attr">tailURL</html:a>.
#				</html:p>
#			attributetailhref##targetNamespace
#    tailhref = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Text label to
#be placed near tail of edge.
#					See <html:a rel="note">undirected</html:a>.
#				</html:p>
#			attributetaillabel##targetNamespace
#    taillabel = Any
#
#    # attributetailport##targetNamespace
#    tailport = Any
#
#    # attributetailtarget##targetNamespace
#    tailtarget = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Tooltip
#annotation attached to the tail of an edge. This is used only
#					if the edge has a <html:a rel="attr">tailURL</html:a> attribute.
#				</html:p>
#			attributetailtooltip##targetNamespace
#    tailtooltip = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If <html:a
#rel="attr">tailURL</html:a> is defined, it is
#					output as part of the tail label of the edge.
#					Also, this value is used near the tail node, overriding any
#					<html:a rel="attr">URL</html:a> value.
#					See <html:a rel="note">undirected</html:a>.
#				</html:p>
#			attributetailURL##targetNamespace
#    tailur_l = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If the object
#has a URL, this attribute determines which window
#					of the browser is used for the URL.
#					See <html:a href="http://www.w3.org/TR/html401/present/frames.html#adef-target">W3C documentation</html:a>.
#				</html:p>
#			attributetarget##targetNamespace
#    target = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Tooltip
#annotation attached to the node or edge. If unset, Graphviz
#					will use the object's <html:a rel="attr">label</html:a> if defined.
#					Note that if the label is a record specification or an HTML-like
#					label, the resulting tooltip may be unhelpful. In this case, if
#					tooltips will be generated, the user should set a <html:tt>tooltip</html:tt>
#					attribute explicitly.
#				</html:p>
#			attributetooltip##targetNamespace
#    tooltip = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If set
#explicitly to true or false, the value determines whether or not
#					internal bitmap rendering relies on a truecolor color model or uses
#					a color palette.
#					If the attribute is unset, truecolor is not used
#					unless there is a <html:a rel="attr">shapefile</html:a> property
#					for some node in the graph.
#					The output model will use the input model when possible.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Use of color palettes results in less memory usage during creation of the
#					bitmaps and smaller output files.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Usually, the only time it is necessary to specify the truetype model
#					is if the graph uses more than 256 colors.
#					However, if one uses <html:a rel="attr">bgcolor</html:a>=transparent with
#					a color palette, font
#					antialiasing can show up as a fuzzy white area around characters.
#					Using <html:a rel="attr">truecolor</html:a>=true avoids this problem.
#				</html:p>
#			attributetruecolor##targetNamespace
#    truecolor = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Hyperlinks
#incorporated into device-dependent output.
#					At present, used in ps2, cmap, i*map and svg formats.
#					For all these formats, URLs can be attached to nodes, edges and
#					clusters. URL attributes can also be attached to the root graph in ps2,
#					cmap and i*map formats. This serves as the base URL for relative URLs in the
#					former, and as the default image map file in the latter.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					For svg, cmapx and imap output, the active area for a node is its
#					visible image.
#					For example, an unfilled node with no drawn boundary will only be active on its label.
#					For other output, the active area is its bounding box.
#					The active area for a cluster is its bounding box.
#					For edges, the active areas are small circles where the edge contacts its head
#					and tail nodes. In addition, for svg, cmapx and imap, the active area
#					includes a thin polygon approximating the edge. The circles may
#					overlap the related node, and the edge URL dominates.
#					If the edge has a label, this will also be active.
#					Finally, if the edge has a head or tail label, this will also be active.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Note that, for edges, the attributes <html:a rel="attr">headURL</html:a>,
#					<html:a rel="attr">tailURL</html:a>, <html:a rel="attr">labelURL</html:a> and
#					<html:a rel="attr">edgeURL</html:a> allow control of various parts of an
#					edge. Also note that, if active areas of two edges overlap, it is unspecified
#					which area dominates.
#				</html:p>
#  			svg ps ps2 mapattributeURL##targetNamespace
#    ur_l = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					If the input
#graph defines this attribute, the node is polygonal,
#					and output is dot or xdot, this attribute provides the
#					coordinates of the vertices of the node's polygon, in inches.
#					If the node is an ellipse or circle, the
#					<html:a rel="attr">samplepoints</html:a> attribute affects
#					the output.
#				</html:p>
#			attributevertices##targetNamespace
#    vertices = Any
#
#    # attributeviewport##targetNamespace
#    viewport = Any
#
#    # attributevoro_margin##targetNamespace
#    voro_margin = Any
#
#    # attributeweight##targetNamespace
#    weight = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Width of node,
#in inches. This is taken as the initial, minimum width
#					of the node. If <html:a rel="attr">fixedsize</html:a> is true, this
#					will be the final width of the node. Otherwise, if the node label
#					requires more width to fit, the node's width will be increased to
#					contain the label. Note also that, if the output format is dot, the
#					value given to <html:a rel="attr">width</html:a> will be the final value.
#				</html:p>
#			attributewidth##targetNamespace
#    width = Any
#
#    #
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Provides z
#coordinate value for 3D layouts and displays. If the
#					graph has <html:a rel="attr">dim</html:a> set to 3 (or more),
#					neato will use a node's <html:a rel="attr">z</html:a> value
#					for the z coordinate of its initial position if
#					its <html:a rel="attr">pos</html:a> attribute is also defined.
#				</html:p>
#				<html:p xmlns:html="http://www.w3.org/1999/xhtml">
#					Even if no <html:a rel="attr">z</html:a> values are specified in the input, it is necessary to
#					declare a <html:a rel="attr">z</html:a> attribute for nodes, e.g, using <html:tt>node[z=""]</html:tt>
#					in order to get z values on output.
#					Thus, setting <html:tt>dim=3</html:tt> but not declaring <html:a rel="attr">z</html:a> will
#					cause <html:tt>neato -Tvrml</html:tt> to
#					layout the graph in 3D but project the layout onto the xy-plane
#					for the rendering. If the <html:a rel="attr">z</html:a> attribute is declared, the final rendering
#					will be in 3D.
#				</html:p>
#			attributez##targetNamespace
#    z = Any


    #--------------------------------------------------------------------------
    #  Private interface:
    #--------------------------------------------------------------------------

    #--------------------------------------------------------------------------
    #  Public interface:
    #--------------------------------------------------------------------------



#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    DocumentRoot().configure_traits()

# EOF +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
