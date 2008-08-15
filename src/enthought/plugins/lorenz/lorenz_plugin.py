""" The Lorenz plugin. """


# Enthought library imports.
from enthought.envisage.api import Plugin, ServiceOffer
from enthought.traits.api import List


class LorenzPlugin(Plugin):
    """ The Lorenz plugin.

    This plugin is part of the 'Lorenz' example application.

    """

    # Extension points Ids.
    SERVICE_OFFERS = 'enthought.envisage.service_offers'
    ACTION_SETS = "enthought.envisage.ui.workbench.action_sets"
    NEW_WIZARDS = "enthought.plugins.workspace.new_wizards"
    EDITORS = "enthought.plugins.workspace.editors"

    #### 'IPlugin' interface ##################################################

    # The plugin's unique identifier.
    id = 'enthought.plugins.lorenz'

    # The plugin's name (suitable for displaying to the user).
    name = 'Lorenz'

    #### Contributions to extension points made by this plugin ################

    action_sets = List(contributes_to=ACTION_SETS)

    # Contributed new resource wizards:
    new_wizards = List(contributes_to=NEW_WIZARDS)

    # Contributed workspace editors:
    editors = List(contributes_to=EDITORS)

    # Service offers.
#    service_offers = List(contributes_to=SERVICE_OFFERS)
#
#    def _service_offers_default(self):
#        """ Trait initializer. """
#
#        lorenz_service_offer = ServiceOffer(
#            protocol = 'enthought.plugins.lorenz.lorenz.Lorenz',
#            factory  = 'enthought.plugins.lorenz.lorenz.Lorenz'
#        )
#
#        return [lorenz_service_offer]

    def _action_sets_default(self):
        """ Trait initialiser """

        from lorenz_action_set import LorenzActionSet

        return [LorenzActionSet]


    def _new_wizards_default(self):
        """ Trait initialiser """

        from new_lorenz_wizard_definition import NewLorenzWizardDefinition

        return [NewLorenzWizardDefinition]


    def _editors_default(self):
        """ Trait initialiser """

        from lorenz_editor_definition import LorenzEditorDefinition

        return [LorenzEditorDefinition]

#### EOF ######################################################################
