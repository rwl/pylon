""" New Lorenz resource wizard definition """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.pyface.api import ImageResource

from enthought.plugins.workspace.wizard_extension import WizardExtension

#------------------------------------------------------------------------------
#  "NewLorenzWizardDefinition" class:
#------------------------------------------------------------------------------

class NewLorenzWizardDefinition(WizardExtension):
    """ Contributes a new Lorenz resource wizard """

    # The wizard contribution's globally unique identifier.
    id = "enthought.plugins.lorenz.new_lorenz_wizard"

    # Human readable identifier
    name = "Lorenz"

    # The wizards's image (displayed on selection etc)
    image = ImageResource("document")

    # The class of contributed wizard
    wizard_class = "enthought.plugins.lorenz.new_lorenz_wizard:" \
    "NewLorenzWizard"

    # A longer description of the wizard's function
    description = "Create a new Lorenz resource"
