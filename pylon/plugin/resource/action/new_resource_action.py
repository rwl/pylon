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

""" Extended Workbench plug-in actions """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import dirname

from enthought.traits.api import Instance, on_trait_change
from enthought.pyface.api import ImageResource, OK
from enthought.pyface.action.api import Action
from enthought.pyface.wizard.api import ChainedWizard

from enthought.plugins.workspace.wizard.wizard_selection_wizard \
    import WizardSelectionWizard

import pylon.plugin.resource.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = dirname(pylon.plugin.resource.api.__file__)

NEW_WIZARDS = "pylon.plugin.resource.new_wizards"

#------------------------------------------------------------------------------
#  "NewResourceAction" class:
#------------------------------------------------------------------------------

class NewResourceAction(Action):
    """ Defines an action that opens the new resource creation wizard """

#    wizard = Instance(ChainedWizard)

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Create a new resource"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "&Other..."

    # A short description of the action used for tooltip text etc:
    tooltip = "New"

    # The action's image (displayed on tool bar tools etc):
    image = ImageResource("new", search_path=[IMAGE_LOCATION])

    # Keyboard accelerator
    accelerator = "Ctrl+N"

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def perform(self, event):
        """ Performs the action """

        # Get all contributed new resource wizards
        contrib = self.window.application.get_extensions(NEW_WIZARDS)
        # Instantiate the contributed classes
        wizards = [wizard() for wizard in contrib]

        # Create the wizard...
        wizard = WizardSelectionWizard(
            parent=self.window.control, window=self.window,
            wizards=wizards, title="New"
        )

        # ...open the wizard.
        if wizard.open() == OK:
            wizard.next_wizard.finished = True

        return

#    @on_trait_change("wizard.controller.complete")
#    def _wizard_complete(self, new):
#
#        print "WIZARD SELECTION WIZARD COMPLETE:", new

# EOF -------------------------------------------------------------------------
