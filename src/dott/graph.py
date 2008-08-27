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

""" Defines a representation of a graph in Graphviz's dot language """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import HasTraits, Any

#------------------------------------------------------------------------------
#  "Graph" class:
#------------------------------------------------------------------------------

class Graph(HasTraits):
    """ Defines a representation of a graph in Graphviz's dot language """

    # Bounding box of drawing in integer points.
    bb = Tuple(Float, Float, desc="bounding box of drawing in integer points")

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
    bgcolor = Color(desc="color used as the background for entire canvas")

	# If true, the drawing is centered in the output canvas.
    center = Bool

    # Specifies the character encoding used when interpreting string input
    # as a text label. The default value is <html:span class="val">UTF-8</html:span>.
    # The other legal value is <html:span class="val">iso-8859-1</html:span> or,
    # equivalently,
    # <html:span class="val">Latin1</html:span>. The <html:a rel="attr">charset</html:a> attribute is case-insensitive.
    # Note that if the character encoding used in the input does not
    # match the <html:a rel="attr">charset</html:a> value, the resulting output may be very strange.
    charset = Str

    # Mode used for handling clusters. If <html:a rel="attr">clusterrank</html:a> is <html:span class="val">local</html:span>, a
    # subgraph whose name begins with "cluster" is given special treatment.
    # The subgraph is laid out separately, and then integrated as a unit into
    # its parent graph, with a bounding rectangle drawn about it.
    # If the cluster has a <html:a rel="attr">label</html:a> parameter, this label
    # is displayed within the rectangle.
    # Note also that there can be clusters within clusters.
    # At present, the modes <html:span class="val">global</html:span> and <html:span class="val">none</html:span>
    # appear to be identical, both turning off the special cluster processing.
    clusterrank = ClusterMode

    # This attribute specifies a color scheme namespace. If defined, it specifies
    # the context for interpreting color names. In particular, if a
    # <html:a rel="type">color</html:a> value has form <html:code>xxx</html:code> or <html:code>//xxx</html:code>,
    # then the color <html:code>xxx</html:code> will be evaluated according to the current color scheme.
    # If no color scheme is set, the standard X11 naming is used.
    # For example, if <html:code>colorscheme=bugn9</html:code>, then <html:code>color=7</html:code>
    # is interpreted as <html:code>/bugn9/7</html:code>.
    colorscheme = String

	# Comments are inserted into output. Device-dependent.
    comment = Str

	# If <html:span class="val">true</html:span>, allow edges between clusters.
    # (See <html:a rel="attr">lhead</html:a> and <html:a rel="attr">ltail</html:a> below.)
    compound = Bool

	# If <html:span class="val">true</html:span>, use edge concentrators.
    concentrate = Bool

    # Factor damping force motions. On each iteration, a nodes movement
    # is limited to this factor of its potential motion. By being less than
    # 1.0, the system tends to "cool", thereby preventing cycling.
    damping = Float

    # This specifies the distance between nodes in separate connected
    # components. If set too small, connected components may overlap.
    # Only applicable if <html:a rel="attr">pack</html:a>=false.
    defaultdist = Float

    # Set the number of dimensions used for the layout. The maximum value
    # allowed is 10.
    dim = Range(1, 10)

    diredgeconstraints = Str

    # This specifies the expected number of pixels per inch on a display device.
    # For bitmap output, this guarantees that text rendering will be
    # done more accurately, both in size and in placement. For SVG output,
    # it is used to guarantee that the dimensions in the output correspond to
    # the correct number of points or inches.
    dpi = Float


    # Terminating condition. If the length squared of all energy gradients are
    # &lt; <html:a rel="attr">epsilon</html:a>, the algorithm stops.
    epsilon = Float


    # Fraction to increase polygons (multiply
    # coordinates by 1 + esep) for purposes of spline edge routing.
    # This should normally be strictly less than
    # <html:a rel="attr">sep</html:a>.
    esep = Float

	# Color used for text.
    fontcolor = Color

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

    # Allows user control of how basic fontnames are represented in SVG output.
    # If <html:a rel="attr">fontnames</html:a> is undefined or <html:span class="val">svg</html:span>,
    # the output will try to use known SVG fontnames. For example, the
    # default font <html:code>Times-Roman</html:code> will be mapped to the
    # basic SVG font <html:code>serif</html:code>. This can be overridden by setting
    # <html:a rel="attr">fontnames</html:a> to <html:span class="val">ps</html:span> or <html:span class="val">gd</html:span>.
    # In the former case, known PostScript font names such as
    # <html:code>Times-Roman</html:code> will be used in the output.
    # In the latter case, the fontconfig font conventions
    # are used. Thus, <html:code>Times-Roman</html:code> would be treated as
    # <html:code>Nimbus Roman No9 L</html:code>. These last two options are useful
    # with SVG viewers that support these richer fontname spaces.
    fontnames = Str

    # Directory list used by libgd to search for bitmap fonts if Graphviz
    # was not built with the fontconfig library.
    # If <html:a rel="attr">fontpath</html:a> is not set, the environment
    # variable <html:code>DOTFONTPATH</html:code> is checked.
    # If that is not set, <html:code>GDFONTPATH</html:code> is checked.
    # If not set, libgd uses its compiled-in font path.
    # Note that fontpath is an attribute of the root graph.
    fontpath = Str


	# Font size, in <html:a rel="note">points</html:a>, used for text.
    fontsize = Float

    k = Float

    # Text label attached to objects.
    # If a node's <html:a rel="attr">shape</html:a> is record, then the label can
    # have a <html:a href="http://www.graphviz.org/doc/info/shapes.html#record">special format</html:a>
    # which describes the record layout.
    label = Str

    # Justification for cluster labels. If <html:span class="val">r</html:span>, the label
    # is right-justified within bounding rectangle; if <html:span class="val">l</html:span>, left-justified;
    # else the label is centered.
    # Note that a subgraph inherits attributes from its parent. Thus, if
    # the root graph sets <html:a rel="attr">labeljust</html:a> to <html:span class="val">l</html:span>, the subgraph inherits
    # this value.
    labeljust = Str

    # Top/bottom placement of graph and cluster labels.
    # If the attribute is <html:span class="val">t</html:span>, place label at the top;
    # if the attribute is <html:span class="val">b</html:span>, place label at the bottom.
    # By default, root
    # graph labels go on the bottom and cluster labels go on the top.
    # Note that a subgraph inherits attributes from its parent. Thus, if
    # the root graph sets <html:a rel="attr">labelloc</html:a> to <html:span class="val">b</html:span>, the subgraph inherits
    # this value.
    labelloc = Str

    # If true, the graph is rendered in landscape mode. Synonymous with
    # <html:code><html:a rel="attr">rotate</html:a>=90</html:code> or <html:code>
    # <html:a rel="attr">orientation</html:a>=landscape</html:code>.
    landscape = Any

    # Specifies a linearly ordered list of layer names attached to the graph
    # The graph is then output in separate layers. Only those components
    # belonging to the current output layer appear. For more information,
    # see the page <html:a href="http://www.graphviz.org/Documentation/html/layers/">How to use drawing layers (overlays)</html:a>.
    layers = ListStr

    # Specifies the separator characters used to split the
    # <html:a rel="attr">layers </html:a>attribute into a list of layer names.
    layersep = Str

    # Specifies strictness of level constraints in neato
    # when <html:code><html:a rel="attr">mode</html:a>="ipsep" or "hier"</html:code>.
    # Larger positive values mean stricter constraints, which demand more
    # separation between levels. On the other hand, negative values will relax
    # the constraints by allowing some overlap between the levels.
    levelsgap = Float

    lp = Any

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
    margin = Float

    maxiter = Int

    # Multiplicative scale factor used to alter the MinQuit (default = 8)
    # and MaxIter (default = 24) parameters used during crossing
    # minimization. These correspond to the
    # number of tries without improvement before quitting and the
    # maximum number of iterations in each pass.
    mclimit = Float

	# Specifies the minimum separation between all nodes.
    mindist = Float

    # Technique for optimizing the layout. If <html:a rel="attr">mode</html:a> is <html:span class="val">major</html:span>,
    # neato uses stress majorization. If <html:a rel="attr">mode</html:a> is <html:span class="val">KK</html:span>,
    # neato uses a version of the gradient descent method. The only advantage
    # to the latter technique is that it is sometimes appreciably faster for
    # small (number of nodes &lt; 100) graphs. A significant disadvantage is that
    # it may cycle.
    #
    # There are two new, experimental modes in neato, <html:span class="val">hier</html:span>, which adds a top-down
    # directionality similar to the layout used in dot, and <html:span class="val">ipsep</html:span>, which
    # allows the graph to specify minimum vertical and horizontal distances
    # between nodes. (See the <html:a rel="attr">sep</html:a> attribute.)
    mode = Str

    # This value specifies how the distance matrix is computed for the input
    # graph. The distance matrix specifies the ideal distance between every
    # pair of nodes. neato attemps to find a layout which best achieves
    # these distances. By default, it uses the length of the shortest path,
    # where the length of each edge is given by its <html:a rel="attr">len</html:a>
    # attribute. If <html:a rel="attr">model</html:a> is <html:span class="val">circuit</html:span>, neato uses the
    # circuit resistance
    # model to compute the distances. This tends to emphasize clusters. If
    # <html:a rel="attr">model</html:a> is <html:span class="val">subset</html:span>, neato uses the subset model. This sets the
    # edge length to be the number of nodes that are neighbors of exactly one
    # of the end points, and then calculates the shortest paths. This helps
    # to separate nodes with high degree.
    model = Str

    # If Graphviz is built with MOSEK defined, mode=ipsep and mosek=true,
    # the Mosek software (www.mosek.com) is use to solve the ipsep constraints.
    mosek = Bool

	# Minimum space between two adjacent nodes in the same rank, in inches.
    nodesep = Float

    nojustify = Bool

    # If set, normalize coordinates of final
    # layout so that the first point is at the origin, and then rotate the
    # layout so that the first edge is horizontal.
    normalize = Bool

    # Used to set number of iterations in
    # network simplex applications, used in
    # computing node x coordinates.
    # If defined, # iterations =  <html:a rel="attr">nslimit</html:a> * # nodes;
    # otherwise,  # iterations = MAXINT.
    nslimit = Float

    # Used to set number of iterations in
    # network simplex applications, used for ranking nodes.
    # If defined, # iterations =  <html:a rel="attr">nslimit1</html:a> * # nodes;
    # otherwise,  # iterations = MAXINT.
    nslimit1 = Float

    # If "out" for a graph G, and n is a node in G, then edges n-&gt;* appear
    # left-to-right in the same order in which they are defined.
    # If "in", the edges *-&gt;n appear
    # left-to-right in the same order in which they are defined for all
    # nodes n.
    ordering = Str

	# Specify order in which nodes and edges are drawn.
    outputorder = OutputMode

    # Determines if and how node overlaps should be removed. Nodes are first
    # enlarged using the <html:a rel="attr">sep</html:a> attribute.
    # If <html:span class="val">true</html:span>, overlaps are retained.
    # If the value is <html:span class="val">scale</html:span>, overlaps are removed by uniformly scaling in x and y.
    # If the value converts to <html:span class="val">false</html:span>, node overlaps are removed by a
    # Voronoi-based technique.
    # If the value is <html:span class="val">scalexy</html:span>, x and y are separately
    # scaled to remove overlaps.
    # If the value is <html:span class="val">orthoxy</html:span> or <html:span class="val">orthoyx</html:span>, overlaps
    # are moved by optimizing two constraint problems, one for the x axis and
    # one for the y. The suffix indicates which axis is processed first.
    # If the value is <html:span class="val">ortho</html:span>, the technique is similar to <html:span class="val">orthoxy</html:span> except a
    # heuristic is used to reduce the bias between the two passes.
    # If the value is <html:span class="val">ortho_yx</html:span>, the technique is the same as <html:span class="val">ortho</html:span>, except
    # the roles of x and y are reversed.
    # The values <html:span class="val">portho</html:span>, <html:span class="val">porthoxy</html:span>, <html:span class="val">porthoxy</html:span>, and <html:span class="val">portho_yx</html:span> are similar
    # to the previous four, except only pseudo-orthogonal ordering is
    # enforced.
    #
    # If the value is <html:span class="val">compress</html:span>, the layout will be scaled down as much as
    # possible without introducing any overlaps, obviously assuming there are
    # none to begin with.
    #
    # If the value is <html:span class="val">ipsep</html:span>, and the layout is done by neato with
    # <html:a rel="attr">mode</html:a>="ipsep", the overlap removal constraints are
    # incorporated into the layout algorithm itself.
    # N.B. At present, this only supports one level of clustering.
    #
    # If the value is <html:span class="val">vpsc</html:span>, overlap removal is similarly to <html:span class="val">ortho</html:span>, except
    # quadratic optimization is used to minimize node displacement.
    # N.B. At present, this mode only works when <html:a rel="attr">mode</html:a>="ipsep".
    #
    # Except for fdp, the layouts assume <html:code>overlap="true"</html:code> as the default.
    # Fdp first uses a number of passes using built-in, force-directed technique
    # to remove overlaps. Thus, fdp accepts <html:a rel="attr">overlap</html:a> with an integer
    # prefix followed by a colon, specifying the number of tries. If there is
    # no prefix, no initial tries will be performed. If there is nothing following
    # a colon, none of the above methods will be attempted. By default, fdp
    # uses <html:code>overlap="9:portho"</html:code>. Note that <html:code>overlap="true"</html:code>,
    # <html:code>overlap="0:true"</html:code> and <html:code>overlap="0:"</html:code> all turn off all overlap
    # removal.
    #
    # Except for the Voronoi method, all of these transforms preserve the
    # orthogonal ordering of the original layout. That is, if the x coordinates
    # of two nodes are originally the same, they will remain the same, and if
    # the x coordinate of one node is originally less than the x coordinate of
    # another, this relation will still hold in the transformed layout. The
    # similar properties hold for the y coordinates.
    # This is not quite true for the "porth*" cases. For these, orthogonal
    # ordering is only preserved among nodes related by an edge.
    #
    # <html:b>NOTE</html:b>The methods <html:span class="val">orthoxy</html:span> and <html:span class="val">orthoyx</html:span> are still evolving. The semantics of these may change, or these methods may disappear altogether.
    overlap = Str

    pack = Str

    # This indicates the granularity and method used for packing
    # (cf. <html:a rel="type">packMode</html:a>). Note that defining
    # <html:a rel="attr">packmode</html:a> will automatically turn on packing as though one had
    # set <html:code>pack=true</html:code>.
    packmode = PackMode

    # The pad attribute specifies how much, in inches, to extend the
    # drawing area around the minimal area needed to draw the graph.
    # If the pad is a single double, both the x and y pad values are set
    # equal to the given value. This area is part of the
    # drawing and will be filled with the background color, if appropriate.
    #
    # Normally, a small pad is used for aesthetic reasons, especially when
    # a background color is used, to avoid having nodes and edges abutting
    # the boundary of the drawn region.
    pad = Float


    # Width and height of output pages, in inches. If this is set and is
    # smaller than the size of the layout, a rectangular array of pages of
    # the specified page size is overlaid on the layout, with origins
    # aligned in the lower-left corner, thereby partitioning the layout
    # into pages. The pages are then produced one at a time, in
    # <html:a rel="attr">pagedir</html:a> order.
    #
    # At present, this only works for PostScript output. For other types of
    # output, one should use another tool to split the output into multiple
    # output files. Or use the <html:a rel="attr">viewport</html:a> to generate
    # multiple files.
    page = Tuple(Float, Float)

    # If the <html:a rel="attr">page</html:a> attribute is set and applicable,
    # this attribute specifies the order in which the pages are emitted.
    # This is limited to one of the 8 row or column major orders.
    pagedir = Pagedir

    # If <html:a rel="attr">quantum</html:a> &gt; 0.0, node label dimensions
    # will be rounded to integral multiples of the quantum.
    quantum = Float

    # Sets direction of graph layout. For example, if <html:a rel="attr">rankdir</html:a>="LR",
    # and barring cycles, an edge <html:code>T -&gt; H;</html:code> will go
    # from left to right. By default, graphs are laid out from top to bottom.
    rankdir = Rankdir

    # In dot, this gives the desired rank separation, in inches. This is
    # the minimum vertical distance between the bottom of the nodes in one
    # rank and the tops of nodes in the next. If the value
    # contains "equally", the centers of all ranks are spaced equally apart.
    # Note that both
    # settings are possible, e.g., ranksep = "1.2 equally".
    # In twopi, specifies radial separation of concentric circles.
    ranksep = Float

    ratio = Str

    # If true and there are multiple clusters, run cross
    # minimization a second time.
    remincross = Bool

	# This is a synonym for the <html:a rel="attr">dpi</html:a> attribute.
    resolution = Float

    # This specifies nodes to be used as the center of the
    # layout and the root of the generated spanning tree. As a graph attribute,
    # this gives the name of the node. As a node attribute (circo only), it
    # specifies that the node should be used as a central node. In twopi,
    # this will actually be the central node. In circo, the block containing
    # the node will be central in the drawing of its connected component.
    # If not defined,
    # twopi will pick a most central node, and circo will pick a random node.
    root = Str

	# If 90, set drawing orientation to landscape.
    rotate = Int

    # During network simplex, maximum number of edges with negative cut values
    # to search when looking for one with minimum cut value.
    searchsize = Int

    # Fraction to increase polygons (multiply
    # coordinates by 1 + sep) for purposes of determining overlap. Guarantees
    # a minimal non-zero distance between nodes.
    # If unset but <html:a rel="attr">esep</html:a> is defined, <html:a rel="attr">sep</html:a> will be
    # set to <html:code>esep/0.8</html:code>. If <html:a rel="attr">esep</html:a> is unset, the default value
    # is used.
    #
    # When <html:a rel="attr">overlap</html:a>="ipsep" or "vpsc",
    # <html:a rel="attr">sep</html:a> gives a minimum distance, in inches, to be left between nodes.
    # In this case, if <html:a rel="attr">sep</html:a> is a pointf, the x and y separations can be
    # specified separately.
    sep = Float

	# Print guide boxes in PostScript at the beginning of
	# routesplines if 1, or at the end if 2. (Debugging)
    showboxes = Trait("beginning", {"beginning": 1, "end": 2})

    # Maximum width and height of drawing, in inches.
    # If defined and the drawing is too large, the drawing is uniformly
    # scaled down so that it fits within the given size.
    #
    # If <html:a rel="attr">size</html:a> ends in an exclamation point (<html:tt>!</html:tt>),
    # then it is taken to be
    # the desired size. In this case, if both dimensions of the drawing are
    # less than <html:a rel="attr">size</html:a>, the drawing is scaled up uniformly until at
    # least one dimension equals its dimension in <html:a rel="attr">size</html:a>.
    #
    # Note that there is some interaction between the <html:a rel="attr">size</html:a> and
    # <html:a rel="attr">ratio</html:a> attributes.
    size = Tuple(Float, Float)


    # Controls how, and if, edges are represented. If true, edges are drawn as
    # splines routed around nodes; if false, edges are drawn as line segments.
    # If set to "", no edges are drawn at all.
    #
    # (1 March 2007) The values <html:span class="val">line</html:span> and <html:span class="val">spline</html:span> can be
    # used as synonyms for <html:span class="val">false</html:span> and <html:span class="val">true</html:span>, respectively.
    # In addition, the value <html:span class="val">polyline</html:span> specifies that edges should be
    # drawn as polylines.
    #
    # By default, the attribute is unset. How this is interpreted depends on
    # the layout. For dot, the default is to draw edges as splines. For all
    # other layouts, the default is to draw edges as line segments. Note that
    # for these latter layouts, if <html:code>splines="true"</html:code>, this
    # requires non-overlapping nodes (cf. <html:a rel="attr">overlap</html:a>).
    # If fdp is used for layout and <html:tt>splines="compound"</html:tt>, then the edges are
    # drawn to avoid clusters as well as nodes.
    splines = Enum(True, False, "")

    # Parameter used to determine the initial layout of nodes. If unset, the
    # nodes are randomly placed in a unit square with
    # the same seed is always used for the random number generator, so the
    # initial placement is repeatable.
    start = Any

	# A URL or pathname specifying an XML style sheet, used in SVG output.
    stylesheet = Str

    # If the object has a URL, this attribute determines which window
    # of the browser is used for the URL.
    # See <html:a href="http://www.w3.org/TR/html401/present/frames.html#adef-target">W3C documentation</html:a>.
    target = EscString

    # If set explicitly to true or false, the value determines whether or not
    # internal bitmap rendering relies on a truecolor color model or uses
    # a color palette.
    # If the attribute is unset, truecolor is not used
    # unless there is a <html:a rel="attr">shapefile</html:a> property
    # for some node in the graph.
    # The output model will use the input model when possible.
    #
    # Use of color palettes results in less memory usage during creation of the
    # bitmaps and smaller output files.
    #
    # Usually, the only time it is necessary to specify the truetype model
    # is if the graph uses more than 256 colors.
    # However, if one uses <html:a rel="attr">bgcolor</html:a>=transparent with
    # a color palette, font
    # antialiasing can show up as a fuzzy white area around characters.
    # Using <html:a rel="attr">truecolor</html:a>=true avoids this problem.
    truecolor = Bool

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

    viewport = Any

    voro_margin = Any

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    Graph().configure_traits()

# EOF +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
