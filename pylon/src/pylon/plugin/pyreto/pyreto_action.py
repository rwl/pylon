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

""" File menu actions for a Pyreto Swarm """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname

from enthought.traits.api import Instance, Callable
from enthought.traits.ui.menu import Action
from enthought.envisage.ui.workbench.workbench_window import WorkbenchWindow
from enthought.pyface.api import ImageResource, FileDialog, OK

from pylon.plugin.pyreto.swarm_wizard import SwarmWizard

import pylon.ui.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_PATH = dirname(pylon.ui.api.__file__)

SELECTORS = "pylon.plugin.pyreto.selectors"

#------------------------------------------------------------------------------
#  "NewSwarmAction" class:
#------------------------------------------------------------------------------

class NewSwarmAction(Action):
    """ An action for instantiating a new Pyreto swarm and adding it
    to the project.

    """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Add a new swarm to the project"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "&Swarm"

    # A short description of the action used for tooltip text etc:
    tooltip = "New Swarm"

    # The action's image (displayed on tool bar tools etc):
    image = ImageResource("new", search_path=[IMAGE_PATH])

    #--------------------------------------------------------------------------
    #  "NewSwarmAction" interface:
    #--------------------------------------------------------------------------

    def perform(self, event):
        """ Perform the action. """

        wizard = SwarmWizard(
            parent=self.window.control, window=self.window, title="New Swarm"
        )

        # Open the wizard
        if wizard.open() == OK:
            wizard.finished = True

# EOF -------------------------------------------------------------------------
