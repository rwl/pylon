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

""" The preferences for the Pylon graph image """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from tempfile import gettempdir
from os.path import join, dirname, exists

from enthought.traits.api import \
    String, Enum, Directory, Property, Trait, ListStr
from enthought.traits.ui.api import \
    View, Group, HGroup, VGroup, Item, Heading, SetEditor, Tabbed
from enthought.enable.colors import ColorTrait as Colour
from enthought.preferences.ui.api import PreferencesPage

from pylon.ui.graph.dot_attributes import shape_trait

#------------------------------------------------------------------------------
#  "GraphImagePreferencesPage" class:
#------------------------------------------------------------------------------

class GraphImagePreferencesPage(PreferencesPage):
    """ The preferences page for the Pylon graph image """

    #--------------------------------------------------------------------------
    #  "PreferencesPage" interface:
    #--------------------------------------------------------------------------

    # The page's category (e.g. 'General/Appearance'). The empty string means
    # that this is a top-level page.
    category = "Pylon"

    # The page's help identifier (optional). If a help Id *is* provided then
    # there will be a 'Help' button shown on the preference page.
    help_id = ""

    # The page name (this is what is shown in the preferences dialog tree)
    name = "Graph Image"

    # The path to the preference node that contains the preferences.
    preferences_path = "pylon.graph_image"

    #--------------------------------------------------------------------------
    #  "GraphImagePreferencesPage" interface:
    #--------------------------------------------------------------------------

    # Image format for Graphviz output
    image_format = Trait("PNG", {"PNG": "png", "JPEG": "jpg", "GIF": "gif"})

    # The Graphviz layout program
    program = Enum("dot", "circo", "neato", "twopi", "fdp")

    #--------------------------------------------------------------------------
    #  Bus node preferences:
    #--------------------------------------------------------------------------

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

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        Tabbed(
            Group(
                Item(name="program"),
                Item(name="image_format"),
                label="Image"
            ),
            Group(
                Item(name="v_shape"),
                Item(name="v_fill_colour"),
                Item(name="v_stroke_colour"),
                Item(
                    name="v_style",
                    editor=SetEditor(
                        name="_node_styles",
                        left_column_title="Unselected",
                        right_column_title="Selected"
                    )
                ),
                label="Bus"
            ),
            springy=True
        )
    )

    #--------------------------------------------------------------------------
    #  Private traits:
    #--------------------------------------------------------------------------

    # Recognised style names for nodes and edges
    _node_and_edge_styles = ListStr(
        ["dashed", "dotted", "solid", "invis" "bold"]
    )

    # Recognised style names for nodes only
    _node_styles = ListStr

    #--------------------------------------------------------------------------
    #  "GraphImagePreferencesPage" interface:
    #--------------------------------------------------------------------------

    def __node_styles_default(self):
        """ Trait initialiser """

        node_styles = ["rounded", "filled", "diagonals"]
        return self._node_and_edge_styles + node_styles

# EOF -------------------------------------------------------------------------
