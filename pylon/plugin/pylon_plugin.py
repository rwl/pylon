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

""" Pylon plug-in """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.etsconfig.api import ETSConfig
from enthought.envisage.api import Plugin, ExtensionPoint
from enthought.traits.api import Instance, List

#------------------------------------------------------------------------------
#  "PylonPlugin" class:
#------------------------------------------------------------------------------

class PylonPlugin(Plugin):
    """ Pylon plugin """

    # Extension point IDs
    PERSPECTIVES = "enthought.envisage.ui.workbench.perspectives"
    PREFERENCES_PAGES = "enthought.envisage.ui.workbench.preferences_pages"
    PREFERENCES = "enthought.envisage.preferences"
    ACTION_SETS = "enthought.envisage.ui.workbench.action_sets"
#    COMMANDS = "enthought.plugins.python_shell.commands"
    COMMANDS = "enthought.plugins.ipython_shell.commands"

    NEW_WIZARDS = "enthought.plugins.workspace.new_wizards"
    EDITORS = "enthought.plugins.workspace.editors"

    # Unique plugin identifier
    id = "pylon.plugin.pylon_plugin"

    # Human readable plugin name
    name = "Pylon"

    #--------------------------------------------------------------------------
    #  Extensions (Contributions):
    #--------------------------------------------------------------------------

    # Contributed perspectives:
    perspectives = List(contributes_to=PERSPECTIVES)

    # Contributed preference pages:
    preferences_pages = List(contributes_to=PREFERENCES_PAGES)

    # Contributed default preferences:
    preferences = List(contributes_to=PREFERENCES)

    # Contributed action sets:
    action_sets = List(contributes_to=ACTION_SETS)

    # Contributed commands:
#    commands_extensions = List(contributes_to=COMMANDS)

    # Contributed new resource wizards:
    new_wizards = List(contributes_to=NEW_WIZARDS)

    # Contributed Pylon editors:
    editors = List(contributes_to=EDITORS)

    #--------------------------------------------------------------------------
    #  "PylonPlugin" interface:
    #--------------------------------------------------------------------------

    def _perspectives_default(self):
        """ Trait initialiser """

        from pylon_perspective import PylonEditPerspective

        return [PylonEditPerspective]


    def _preferences_pages_default(self):
        """ Trait initialiser """

        from pylon_preference_page import PylonRootPreferencePage

        return [PylonRootPreferencePage]


    def _preferences_default(self):
        """ Trait initialiser """

        return ["pkgfile://pylon/plugin/preferences.ini"]


    def _action_sets_default(self):
        """ Trait initialiser """

        from pylon_action_set import \
            PylonWorkbenchActionSet, PylonWorkspaceActionSet

        return [PylonWorkbenchActionSet, PylonWorkspaceActionSet]


    def _commands_extensions_default(self):
        """ Trait initialiser """

        commands = [
            "from pylon.api import *",
            "from pylon.filter.api import *",
            "from pylon.routine.api import *"
        ]

        return commands


    def _new_wizards_default(self):
        """ Trait initialiser """

        from pylon_wizard import NetworkWizardExtension

        return [NetworkWizardExtension]


    def _editors_default(self):
        """ Trait initialiser """

        from pylon_editor_extension import \
            PylonTreeEditorExtension, PylonTableEditorExtension, \
            PylonPlotEditorExtension

        editors = [
            PylonTreeEditorExtension, PylonTableEditorExtension,
            PylonPlotEditorExtension
        ]

        return editors

# EOF -------------------------------------------------------------------------
