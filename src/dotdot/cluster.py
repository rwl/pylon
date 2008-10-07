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
clusterempty

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    HasTraits, Any


#------------------------------------------------------------------------------
#  "Cluster" class:
#------------------------------------------------------------------------------

class Cluster(HasTraits):
    """
    clusterempty

    """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

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
#					Font size, in
#<html:a rel="note">points</html:a>, used for text.
#				</html:p>
#			attributefontsize##targetNamespace
#    fontsize = Any
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
#    # attributelp##targetNamespace
#    lp = Any
#
#    # attributenojustify##targetNamespace
#    nojustify = Any
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
#					Set style for
#node or edge. For cluster subgraph, if "filled", the
#					cluster box's background is filled.
#				</html:p>
#			attributestyle##targetNamespace
#    style = Any
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
    Cluster().configure_traits()

# EOF +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
