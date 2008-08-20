#------------------------------------------------------------------------------
# Copyright (C) 2007 Richard W. Lincoln
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This software is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANDABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA
#------------------------------------------------------------------------------

""" Defines the attributes used by various Graphviz tools """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os import path

from enthought.traits.api import HasTraits, Enum, String, Float, List, ListStr
#from enthought.traits.api import Color as Colour
#from enthought.enable.traits.api import RGBAColor as Colour
from enthought.enable.colors import ColorTrait as Colour
from enthought.traits.ui.api import View, Item, Group, SetEditor
from enthought.traits.ui.menu import NoButtons

from enthought.pyface.image_resource import ImageResource

#------------------------------------------------------------------------------
#  Trait definitions:
#------------------------------------------------------------------------------

shape_trait = Enum(
   "rectangle",
   "ellipse",
   "circle",
   "invtriangle",
   "invtrapezium",
   "point",
   "egg",
   "triangle",
   "plaintext",
   "diamond"
   "trapezium",
   "parallelogram",
   "house",
   "pentagon",
   "hexagon",
   "septagon",
   "octagon",
   "doublecircle",
   "doubleoctagon",
   "tripleoctagon",
   "invhouse",
   "none",
   "note",
   "tab",
   "box3d",
   "component",
   desc="node shape",
   label="Node shape"
)

#------------------------------------------------------------------------------
#  "DotAttributes" class:
#------------------------------------------------------------------------------

class DotAttributes(HasTraits):
    """ Defines the attributes used by various Graphviz tools """

    # Recognised style names for nodes and edges
    _node_and_edge_styles = ListStr(
        ["dashed", "dotted", "solid", "invis" "bold"]
    )

    # Recognised style names for nodes only
    _node_styles = ListStr

    #--------------------------------------------------------------------------
    #  Graph properties:
    #--------------------------------------------------------------------------

    # The graph background colour
#    bg_colour = Colour("white", desc="graph background colour")

    # Graph font colour
    font_colour = Colour("black", desc="general font colour")

#    # Colour representing active power
#    active_colour = Colour("black", desc="colour representing active power")
#
#    # Colour representing reactive power
#    reactive_colour = Colour("blue", desc="colour representing reactive power")

    # Bus node properties -----------------------------------------------------

#    node_attrs = [
#        "URL", "color", "colorscheme", "comment",
#        "distortion", "fillcolor", "fixedsize", "fontcolor", "fontname",
#        "fontsize", "group", "height", "image", "imagescale", "label",
#        "layer", "margin", "nojustify", "orientation", "peripheries",
#        "pin", "pos", "rects", "regular", "root", "samplepoints",
#        "shape", "shapefile", "showboxes", "sides", "skew", "style",
#        "target", "tooltip", "vertices", "width", "z"
#    ]

    # Bus node styles
    v_style = ListStr(["rounded", "filled"], label="Bus style")

    # Bus node shape
    v_shape = shape_trait

    # Bus node fill colour
    v_fill_colour = Colour(
        "green", desc="bus node fill colour", label="Bus fill colour"
    )

    # Bus node stroke colour
    v_stroke_colour = Colour(
        "blue", desc="bus node stroke colour", label="Bus stroke colour"
    )

    # Branch properties -------------------------------------------------------

#    e_colour = Property(String, depends_on=["active_colour", "reactive_colour"])

    # Generator properties ----------------------------------------------------

#    g_style = List(String, ["rounded", "filled"])
#
#    g_shape = shape_trait
#
#    g_fill_colour = Colour("white", desc="generator node background colour")
#
#    g_stroke_colour = Colour("black", desc="generator stroke colour")
#
#    g_width = Float(desc="generator node width")
#
#    g_height = Float(desc="generator node height")

    # Load properties ---------------------------------------------------------

#    l_style = List(String, ["filled"])
#
#    l_shape = shape_trait
#
#    l_fill_colour = Colour("white", desc="load node background colour")
#
#    l_stroke_colour = Colour("black", desc="load node stroke colour")
#
#    l_width = Float(desc="load node width")
#
#    l_height = Float(desc="load node height")

    # Default view:
    traits_view = View(
        Group(
#            Item(name="bg_colour"),
            Item(name="font_colour"),
#            Item(name="active_colour"),
#            Item(name="reactive_colour"),
#            label="Global"
#        ),
#        Group(
            Item(name="v_shape"),
            Item(name="v_fill_colour"),
            Item(name="v_stroke_colour"),
#            Item(
#                name="v_style",
#                editor=SetEditor(
#                    name="_node_styles",
#                    left_column_title="Unselected",
#                    right_column_title="Selected"
#                )
#            ),
#            label="Bus"
        ),
#        Group(
#            Item(name="g_style"),
#            Item(name="g_shape"),
#            Item(name="g_fill_colour"),
#            Item(name="g_stroke_colour"),
#            Item(name="g_width"),
#            Item(name="g_height"),
#            label="Generator"
#        ),
#        Group(
#            # Load node traits
#            Item(name="l_style"),
#            Item(name="l_shape"),
#            Item(name="l_fill_colour"),
#            Item(name="l_stroke_colour"),
#            Item(name="l_width"),
#            Item(name="l_height"),
#            label="Load"
#        ),
#        title="Graph Preferences",
        buttons=["OK"],
        close_result=True,
        resizable=True
    )

    def __node_styles_default(self):
        """ Trait initialiser """

        return self._node_and_edge_styles + ["rounded", "filled", "diagonals"]


    def _v_shape_default(self):
        """ Trait initialiser """

        return "rectangle"


    def _g_shape_default(self):
        """ Trait initialiser """

        return "circle"


    def _l_shape_default(self):
        """ Trait initialiser """

        return "invtriangle"


#    def _get_e_colour(self):
##        return self.active_colour+":"+self.reactive_colour
#        return "black:black"

# EOF -------------------------------------------------------------------------
