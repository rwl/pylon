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

""" Defines Pylon plug-in actions """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import dirname

from enthought.traits.api import Bool
from enthought.pyface.action.api import Action
from enthought.envisage.ui.workbench.workbench_window import WorkbenchWindow
from enthought.pyface.api import ImageResource, OK

from pylon.plugin.pylon_network_wizard import NetworkWizard

import pylon.ui.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_PATH = dirname(pylon.ui.api.__file__)

#------------------------------------------------------------------------------
#  "NewNetworkAction" class:
#------------------------------------------------------------------------------

class NewNetworkAction(Action):
    """ An action for instantiating a new Pylon network and adding it
    to the project.

    """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Add a new network to the project"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "&Network"

    # A short description of the action used for tooltip text etc:
    tooltip = "New Network"

    # The action's image (displayed on tool bar tools etc):
    image = ImageResource("new.png", search_path=[IMAGE_PATH])

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def perform(self, event):
        """ Performs the action """

        wizard = NetworkWizard(
            parent=self.window.control, window=self.window, title="New Network"
        )

        # Open the wizard
        if wizard.open() == OK:
            wizard.finished = True

# EOF -------------------------------------------------------------------------
