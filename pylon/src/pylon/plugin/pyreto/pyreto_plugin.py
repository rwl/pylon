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

""" Pyreto plug-in """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.envisage.api import Plugin, ExtensionPoint

from enthought.traits.api import Instance, List, Callable

#------------------------------------------------------------------------------
#  "PyretoPlugin" class:
#------------------------------------------------------------------------------

class PyretoPlugin(Plugin):
    """ Pyreto plugin """

    # Extension point IDs
    PERSPECTIVES = "enthought.envisage.ui.workbench.perspectives"
    PREFERENCES_PAGES = "enthought.envisage.ui.workbench.preferences_pages"
    PREFERENCES = "enthought.envisage.preferences"
    ACTION_SETS = "enthought.envisage.ui.workbench.action_sets"
#    COMMANDS = "enthought.plugins.python_shell.commands"
    COMMANDS = "enthought.plugins.ipython_shell.commands"

    NEW_WIZARDS = "enthought.plugins.workspace.new_wizards"
    EDITORS = "enthought.plugins.workspace.editors"

    SELECTORS = "pylon.plugin.pyreto.selectors"

    # Unique plugin identifier
    id = "pylon.plugin.pyreto_plugin"

    # Human readable plugin name
    name = "Pyreto"

    #--------------------------------------------------------------------------
    #  Extension Points:
    #--------------------------------------------------------------------------

    selectors = ExtensionPoint(List(Callable), id=SELECTORS)

    #--------------------------------------------------------------------------
    #  Extensions (Contributions):
    #--------------------------------------------------------------------------

    # Contributed perspectives:
    perspectives = List(contributes_to=PERSPECTIVES)

    # Contributed action sets:
    action_sets = List(contributes_to=ACTION_SETS)

    # Contributed commands that are executed in the interactive
    # Python shell on startup
#    contributed_commands = List(contributes_to=COMMANDS)

    # Contributed new resource wizards:
    new_wizards = List(contributes_to=NEW_WIZARDS)

    # Contributed Pylon editors:
    editors = List(contributes_to=EDITORS)

    # Selectors bundled with the pyreto plug-in:
    bundled_selectors = List(contributes_to=SELECTORS)

    #--------------------------------------------------------------------------
    #  "PyretoPlugin" interface:
    #--------------------------------------------------------------------------

    def _perspectives_default(self):
        """ Trait initialiser """

        from pyreto_perspective import PyretoPerspective

        return [PyretoPerspective]


    def _action_sets_default(self):
        """ Trait initialiser """

        from pyreto_action_set import \
            PyretoWorkbenchActionSet, PyretoWorkspaceActionSet

        return [PyretoWorkbenchActionSet, PyretoWorkspaceActionSet]


    def _contributed_commands_default(self):
        """ Trait initialiser """

        return ["from pylon.pyreto.api import *"]


    def _new_wizards_default(self):
        """ Trait initialiser """

        from wizard_extension import SwarmWizardExtension

        return [SwarmWizardExtension]


    def _editors_default(self):
        """ Trait initialiser """

        from editor_extension import SwarmTableEditor#, SwarmTreeEditor

        return [SwarmTableEditor]


    def _bundled_selectors_default(self):
        """ Trait initialiser """

        from pyqle.selector.profile_selector import ProfileSelector

        return [ProfileSelector]

# EOF -------------------------------------------------------------------------
