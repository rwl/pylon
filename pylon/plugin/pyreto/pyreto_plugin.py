#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard W. Lincoln
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

""" Pyreto plug-in.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.envisage.api import Plugin, ExtensionPoint
from enthought.traits.api import Instance, List, Callable

#------------------------------------------------------------------------------
#  "PyretoPlugin" class:
#------------------------------------------------------------------------------

class PyretoPlugin(Plugin):
    """ Pyreto plugin.
    """

    # Extension point IDs.
    ACTION_SETS = "enthought.envisage.ui.workbench.action_sets"
    COMMANDS = "enthought.plugins.python_shell.commands"

    NEW_WIZARDS = "puddle.resource.new_wizards"
    EDITORS = "puddle.resource.editors"

    # Unique plug-in identifier.
    id = "pylon.plugin.pyreto_plugin"

    # Human readable plug-in name.
    name = "Pyreto"

    #--------------------------------------------------------------------------
    #  Extensions (Contributions):
    #--------------------------------------------------------------------------

    # Contributed action sets:
    action_sets = List(contributes_to=ACTION_SETS)

    # Contributed commands that are executed in the interactive
    # Python shell on startup
    commands = List(contributes_to=COMMANDS)

    # Contributed new resource wizards:
    new_wizards = List(contributes_to=NEW_WIZARDS)

    # Contributed Pylon editors:
    editors = List(contributes_to=EDITORS)

    #--------------------------------------------------------------------------
    #  "PyretoPlugin" interface:
    #--------------------------------------------------------------------------

    def _action_sets_default(self):
        """ Trait initialiser.
        """
        from pyreto_action import PyretoActionSet

        return [PyretoActionSet]


    def _commands_default(self):
        """ Trait initialiser.
        """
        return []#"from pylon.pyreto.api import *"]


    def _new_wizards_default(self):
        """ Trait initialiser.
        """
        from experiment_wizard import ExperimentWizardExtension

        return [ExperimentWizardExtension]


    def _editors_default(self):
        """ Trait initialiser.
        """
        from pyreto_editor import PyretoPlotEditorExtension

        return [PyretoPlotEditorExtension]

# EOF -------------------------------------------------------------------------
