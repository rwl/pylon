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

""" Pylon interactive graph plug-in """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.envisage.api import Plugin

from enthought.traits.api import Instance, List

#------------------------------------------------------------------------------
#  "GraphPlugin" class:
#------------------------------------------------------------------------------

class GraphPlugin(Plugin):
    """ Interactive graph plug-in """

    # Extension point IDs
    PREFERENCES_PAGES = "enthought.envisage.ui.workbench.preferences_pages"
    EDITORS = "enthought.plugins.workspace.editors"

    # Unique plugin identifier
    id = "pylon.plugin.graph"

    # Human readable plugin name
    name = "Pylon Graph"

    #--------------------------------------------------------------------------
    #  Extensions (Contributions):
    #--------------------------------------------------------------------------

    # Contributes preferences pages
    preferences_pages = List(contributes_to=PREFERENCES_PAGES)

    # Editors contributed to the workspace
    editors = List(contributes_to=EDITORS)

    #--------------------------------------------------------------------------
    #  "GraphPlugin" interface:
    #--------------------------------------------------------------------------

    def _preferences_pages_default(self):
        """ Trait initialiser """

        from pylon.plugin.graph.graph_preference_page import \
            GraphPreferencesPage

        return [GraphPreferencesPage]


    def _editors_default(self):
        """ Trait initialiser """

        from pylon.plugin.graph.graph_editor_extension import \
            GraphEditorExtension

        return [GraphEditorExtension]

# EOF -------------------------------------------------------------------------
