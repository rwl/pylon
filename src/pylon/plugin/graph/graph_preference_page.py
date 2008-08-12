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

"""
The preferences for the Pylon graph image

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from tempfile import gettempdir

from os.path import join, dirname, exists

from enthought.traits.api import \
    String, Enum, Directory, Property, cached_property

from enthought.traits.ui.api import View, Group, HGroup, VGroup, Item, Label

from enthought.preferences.ui.api import PreferencesPage

from enthought.traits.ui.api import View

#------------------------------------------------------------------------------
#  "GraphPreferencesPage" class:
#------------------------------------------------------------------------------

class GraphPreferencesPage(PreferencesPage):
    """
    The preferences page for the Pylon graph

    """

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
    name = "Graph"

    # The path to the preference node that contains the preferences.
    preferences_path = "pylon.graph"

    #--------------------------------------------------------------------------
    #  "GraphPreferencesPage" interface:
    #--------------------------------------------------------------------------

    # Graphviz layout engine
    program = Enum("dot", "circo", "neato", "twopi", "fdp")

    traits_view = View(
        Label("Graph"),
        "_",
        Group(Item(name="program"))
    )

# EOF -------------------------------------------------------------------------
