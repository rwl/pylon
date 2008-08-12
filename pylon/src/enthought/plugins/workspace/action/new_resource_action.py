#------------------------------------------------------------------------------
#
#  Copyright (c) 2008, Richard W. Lincoln
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Richard W. Lincoln
#  Date:   16/07/2008
#
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

import enthought.plugins.workspace.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

NEW_WIZARDS = "enthought.plugins.workspace.new_wizards"

IMAGE_LOCATION = dirname(enthought.plugins.workspace.api.__file__)

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
