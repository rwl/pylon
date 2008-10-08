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

""" Wizard selection wizard page """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import dirname

from enthought.traits.api import \
    Instance, List, Property, Str, cached_property

from enthought.traits.ui.api import View, Group, Item, InstanceEditor, Heading
from enthought.pyface.api import ImageResource
from enthought.pyface.wizard.api import WizardPage, ChainedWizard, SimpleWizard
from enthought.envisage.ui.workbench.workbench_window import WorkbenchWindow

from pylon.plugin.resource.wizard_extension import WizardExtension

from wizard_tree_viewer import WizardTreeViewer

import pylon.plugin.resource.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = dirname(pylon.plugin.resource.api.__file__)

#------------------------------------------------------------------------------
#  "WizardSelectionWizardPage" class:
#------------------------------------------------------------------------------

class WizardSelectionPage(WizardPage):
    """ Wizard page for element creation wizard selection """

    # The selection of wizards from which to choose
    wizards = List(Instance(WizardExtension))

    # The selected wizard
    wizard = Instance(WizardExtension)

    # A viewer based on a tree control
#    tree_viewer = Instance(WizardTreeViewer)
#    name = "General"
#    image = ImageResource("open_folder", search_path=[IMAGE_LOCATION])

    # A label providing further information
    _label = Property(Str, depends_on=["wizard"])

    # The default view
    traits_view = View(
        Group(Heading("Select a wizard")),
        Group(
            Item(name="_label", style="readonly", show_label=False),
            "_",
        ),
        Item(
            name="wizard",
            editor=InstanceEditor(name="wizards", editable=False)
        )
    )

    #--------------------------------------------------------------------------
    #  "WizardSelectionWizardPage" interface:
    #--------------------------------------------------------------------------

#    def _wizard_default(self):
#        """ Trait initialiser """
#
#        if self.wizards:
#            self.complete = True
#            return self.wizards[0]
#        else:
#            return None


    def _wizard_changed(self, new):
        """ Complete the wizard when a wizard is set """

        if isinstance(new, WizardExtension):
            self.complete = True
        else:
            self.complete = False


    @cached_property
    def _get__label(self):
        """ Property getter """

        if self.wizard is not None:
            return self.wizard.description
        else:
            return "No wizard selected."


    def on_selection_change(self, selection):
        """ Relates the container selected in the tree viewer to the wizard
        page's folder trait.

        """

        if selection:
            sel = selection[0]
            if isinstance(sel, WizardExtension):
                self.wizard = sel
            else:
                self.wizard = None

    #--------------------------------------------------------------------------
    #  "WizardPage" interface:
    #--------------------------------------------------------------------------

    def create_page(self, parent):
        """ Create the wizard page. """

#        self.tree_viewer = tree_viewer = WizardTreeViewer(
#            parent=parent, input=self
#        )
#
#        tree_viewer.on_trait_change(self.on_selection_change, "selection")
#
#        return tree_viewer.control

        ui = self.edit_traits(parent=parent, kind="subpanel")

        return ui.control

#------------------------------------------------------------------------------
#  "WizardSelectionWizard" class:
#------------------------------------------------------------------------------

class WizardSelectionWizard(ChainedWizard):
    """ A wizard for wizard selection """

    #--------------------------------------------------------------------------
    #  "WizardSelectionWizard" interface:
    #--------------------------------------------------------------------------

#    wizards = List(SimpleWizard)

    window = Instance(WorkbenchWindow)

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, window, wizards, **traits):
        """ Returns a new WizardSelectionWizard instance """

        self.window = window
        self.wizards = wizards

        # Create the selection page...
        wsp = WizardSelectionPage(
            wizards=wizards, id="wizard_selection"
        )
        wsp.on_trait_change(self.on_wizard_changed, "wizard")

        # ...add it to the wizard.
        self.pages = [wsp]

        super(WizardSelectionWizard, self).__init__(**traits)


    def on_wizard_changed(self, new):
        """ Handles the selected wizard changing """

        if new is not None:
            app = self.window.application
            wizard_klass = app.import_symbol(new.wizard_class)
            self.next_wizard = wizard_klass(
                parent=self.control, window=self.window
            )

# EOF -------------------------------------------------------------------------
