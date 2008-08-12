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

""" Graph image plugin """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.envisage.api import Plugin

from enthought.traits.api import Instance, List

#------------------------------------------------------------------------------
#  "GraphImagePlugin" class:
#------------------------------------------------------------------------------

class GraphImagePlugin(Plugin):
    """ Graph image plugin """

    # Extension point IDs
    PREFERENCES_PAGES = "enthought.envisage.ui.workbench.preferences_pages"
    EDITORS = "enthought.plugins.workspace.editors"

    # Unique plugin identifier
    id = "pylon.plugin.graph_image"

    # Human readable plugin name
    name = "Pylon Graph Image"

    #--------------------------------------------------------------------------
    #  Extensions (Contributions):
    #--------------------------------------------------------------------------

    # Contributes preferences pages
    preferences_pages = List(contributes_to=PREFERENCES_PAGES)

    # Editors contributed to the workspace
    editors = List(contributes_to=EDITORS)

    #--------------------------------------------------------------------------
    #  "GraphImagePlugin" interface:
    #--------------------------------------------------------------------------

    def _preferences_pages_default(self):
        """ Trait initialiser """

        from pylon.plugin.graph_image.graph_image_preference_page \
            import GraphImagePreferencesPage

        return [GraphImagePreferencesPage]


    def _editors_default(self):
        """ Trait initialiser """

        from pylon.plugin.graph_image.graph_image_editor_extension import \
            GraphImageEditorExtension

        return [GraphImageEditorExtension]

# EOF -------------------------------------------------------------------------
