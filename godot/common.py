
from enthought.traits.api import \
    HasTraits, Color, Str, Enum, Float, Font, Any, Bool, Int, File, Trait, \
    List, Tuple, ListStr, Property, Either

pointf_trait = Float#Tuple(Float, Float, desc="the point (x,y)")

point_trait = Float #Either(
#    pointf_trait, Tuple(Float, Float, Float, desc="the point (x,y,z)")
#)

color_schemes = ["X11", "Accent", "Blues", "BRBG", "BUGN", "BUPU", "Dark",
    "GUBU", "Greens", "Greys", "Oranges", "OORD", "Paired", "Pastel", "PIYG",
    "PRGN", "PUBU", "PUBUGN", "PUOR", "PURD", "Purples", "RDBU", "RDGY",
    "RDPU", "RDYLBU", "RDYLGN", "Reds", "Set", "Spectral", "YLGN",
    "YLGNBU", "YLORBR", "YLORRD"]

color_scheme_trait = Enum(
    color_schemes, desc="a color scheme namespace",
    label="Color scheme"
)

color_trait = Color("black", desc="drawing color for graphics, not text")

def Alias(name, desc=""):
    """ Syntactically concise alias trait but creates a pair of lambda
    functions for every alias you declare.

    class MyClass(HasTraits):
        line_width = Float(3.0)
        thickness = Alias("line_width")

    """

    return Property(
        lambda obj: getattr(obj, name),
        lambda obj, val: setattr(obj, name, val),
        desc=desc
    )

comment_trait = Str(desc="comments inserted into output")

fontcolor_trait = Color(
    "black", desc="color used for text", label="Font color"
)

fontname_trait = Font(
    "Times-Roman", desc="font used for text", label="Font name"
)

fontsize_trait = Float(
    14.0, desc="size, in points, used for text", label="Font size"
)

label_trait = Str(desc="text label attached to objects")

# FIXME: Implement layerRange
#
# layerId or layerIdslayerId,
#     where layerId = "all", a decimal integer or a layer name. (An integer i
#     corresponds to layer i.) The string s consists of 1 or more separator
#     characters specified by the layersep attribute.
layer_trait = Str(desc="layers in which the node or edge is present")

margin_trait = Either(
    Float, pointf_trait, desc="x and y margins of canvas or node label"
)

nojustify_trait = Bool(
    False, label="No justify",
    desc="multi-line labels will be justified in the context of itself"
)

peripheries_trait = Int(
    desc="number of peripheries used in polygonal shapes and cluster "
    "boundaries"
)

# FIXME: Implement splineType
#
# splineType
#    spline ( ';' spline )*
#    where spline    =    (endp)? (startp)? point (triple)+
#    and triple    =    point point point
#    and endp    =    "e,%d,%d"
#    and startp    =    "s,%d,%d"
# If a spline has points p1 p2 p3 ... pn, (n = 1 (mod 3)), the points
# correspond to the control points of a B-spline from p1 to pn. If startp is
# given, it touches one node of the edge, and the arrowhead goes from p1 to
# startp. If startp is not given, p1 touches a node. Similarly for pn and endp.
pos_trait = Float(desc="position of node, or spline control points")

rectangle_trait = Tuple(
    Float, Float, Float, Float,
    desc="The rect llx,lly,urx,ury gives the coordinates, in points, of the "
    "lower-left corner (llx,lly) and the upper-right corner (urx,ury)."
)

root_trait = Str(
    desc="nodes to be used as the center of the layout and the root of "
    "the generated spanning tree"
)

showboxes_trait = Trait(
    "beginning", {"beginning": 1, "end": 2}, label="Show boxes",
    desc="guide boxes in PostScript output"
)

# Additional styles are available in device-dependent form. Style lists are
# passed to device drivers, which can use this to generate appropriate output.
edge_styles = ["dashed", "dotted", "solid", "invis", "bold"]
cluster_styles = ["filled", "rounded"]
node_styles = edge_styles + cluster_styles + ["diagonals"]

target_trait = Str(
    desc="if the object has a URL, this attribute determines which window "
    "of the browser is used"
)

tooltip_trait = Str(desc="tooltip annotation attached to the node or edge")

url_trait = Str(desc="hyperlinks incorporated into device-dependent output")


# EOF -------------------------------------------------------------------------
