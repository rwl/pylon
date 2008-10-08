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

from enthought.pyface.api import ImageResource, OK
from enthought.pyface.action.api import Action

from enthought.plugins.workspace.wizard.wizard_selection_wizard \
    import WizardSelectionWizard

import pylon.plugin.resource.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = dirname(pylon.plugin.resource.api.__file__)

IMPORT_WIZARDS = "pylon.plugin.resource.import_wizards"

#------------------------------------------------------------------------------
#  "ImportAction" class:
#------------------------------------------------------------------------------

class ImportAction(Action):
    """ Defines an action that opens the import wizard selection wizard """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Import resources to the workspace"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "&Import..."

    # A short description of the action used for tooltip text etc:
    tooltip = "Import resources"

    # The action's image (displayed on tool bar tools etc):
    image = ImageResource("import", search_path=[IMAGE_LOCATION])

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def perform(self, event):
        """ Performs the action """

        # Get all contributed import wizards
        contrib = self.window.application.get_extensions(IMPORT_WIZARDS)
        # Instantiate the contributed classes
        wizards = [wizard() for wizard in contrib]

        # Create the wizard...
        wizard = WizardSelectionWizard(
            parent=self.window.control, window=self.window,
            wizards=wizards, title="Import"
        )

        # ...open the wizard.
        if wizard.open() == OK:
            wizard.next_wizard.finished = True

        return

#        # Get all contributed new element wizards
#        app = self.window.workbench.application
#        contrib = app.get_extensions(IMPORT_WIZARDS)
#
#        # Ensure they are not instantiated
#        wizards = []
#        for factory_or_wizard in contrib:
#            if not isinstance(factory_or_wizard, WizardContribution):
#                wizard = factory_or_wizard()
#            else:
#                logger.warn(
#                    "DEPRECATED: contribute wizard classes or "
#                    "factories - not wizard instances."
#                )
#
#                wizard = factory_or_wizard
#            wizards.append(wizard)
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


#    def on_wizard_changed(self, new):
#
#        if new is not None:
#            app = self.window.application
#            wizard_klass = app.import_symbol(new.wizard_class)
#
#            workspace = self.window.application.get_service(WORKSPACE_SERVICE)
#
#            self.wizard.next_wizard = wizard_klass(
#                parent=None, workspace=workspace
#            )

# EOF -------------------------------------------------------------------------
