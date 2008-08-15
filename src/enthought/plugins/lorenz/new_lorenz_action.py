""" An action for creating a new Lorenz resource """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.pyface.api import ImageResource, OK
from enthought.pyface.action.api import Action

from new_lorenz_wizard import NewLorenzWizard

#------------------------------------------------------------------------------
#  "NewLorenzAction" class:
#------------------------------------------------------------------------------

class NewLorenzAction(Action):
    """ An action for creating a new Lorenz resource """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Create a new Lorenz resource"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "Lorenz"

    # A short description of the action used for tooltip text etc:
    tooltip = "New Lorenz"

    # The action's image (displayed on tool bar tools etc):
    image = ImageResource("new")

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def perform(self, event):
        """ Perform the action """

        wizard = NewLorenzWizard(
            parent=self.window.control,
            window=self.window,
            title="New Lorenz"
        )

        # Open the wizard
        if wizard.open() == OK:
            # Fire the 'finished' event if completed successfully
            wizard.finished = True

        return

# EOF -------------------------------------------------------------------------
