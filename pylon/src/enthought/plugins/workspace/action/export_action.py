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
#  Date:   17/07/2008
#
#------------------------------------------------------------------------------

""" Extended Workbench plug-in actions """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import dirname

from enthought.pyface.api import ImageResource, OK

from enthought.pyface.action.api import Action

from enthought.plugins.workspace.wizard.wizard_selection_wizard \
    import WizardSelectionWizard

import enthought.plugins.workspace.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = dirname(enthought.plugins.workspace.api.__file__)

EXPORT_WIZARDS = "enthought.plugins.workspace.export_wizards"

#------------------------------------------------------------------------------
#  "ExportAction" class:
#------------------------------------------------------------------------------

class ExportAction(Action):
    """ Defines an action that opens the export wizard selection wizard """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Export resources from the workspace"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "&Export..."

    # A short description of the action used for tooltip text etc:
    tooltip = "Export resources"

    # The action's image (displayed on tool bar tools etc):
    image = ImageResource("export", search_path=[IMAGE_LOCATION])

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def perform(self, event):
        """ Performs the action """

        # Get all contributed import wizards
        contrib = self.window.application.get_extensions(EXPORT_WIZARDS)
        # Instantiate the contributed classes
        wizards = [wizard() for wizard in contrib]

        # Create the wizard...
        wizard = WizardSelectionWizard(
            parent=self.window.control, window=self.window,
            wizards=wizards, title="Export"
        )

        # ...open the wizard.
        if wizard.open() == OK:
            wizard.next_wizard.finished = True

        return

#        # Get all contributed new element wizards
#        app = self.window.workbench.application
#        contrib = app.get_extensions(EXPORT_WIZARDS)
#
#        # Ensure they are not instantiated
#        wizards = [factory() for factory in contrib]
##        for factory_or_wizard in contrib:
##            if not isinstance(factory_or_wizard, WizardContribution):
##                wizard = factory_or_wizard()
##            else:
##                logger.warn(
##                    "DEPRECATED: contribute wizard classes or "
##                    "factories - not wizard instances."
##                )
##
##                wizard = factory_or_wizard
##            wizards.append(wizard)
#
#        # Create the selection page...
#        wswp = WizardSelectionPage(
#            wizards=wizards, id="wizard_selection"
#        )
#        wswp.on_trait_change(self.on_wizard_changed, "wizard")
#
#        # ...add it to the a wizard...
#        self.wizard = wizard = ChainedWizard(
#            parent=self.window.control, title="New",
#            pages=[wswp]
#        )
#
#        # ...open the wizard.
#        wizard.open()
#
#        return
#
#
#    def on_wizard_changed(self, new):
#
#        if new is not None:
#            app = self.window.application
#            wizard_klass = app.import_symbol(new.wizard_class)
#            self.wizard.next_wizard = wizard_klass(parent=None)

# EOF -------------------------------------------------------------------------
