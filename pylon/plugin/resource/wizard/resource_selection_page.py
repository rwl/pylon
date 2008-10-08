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

""" Defines a wizard page for resource selection """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import expanduser, join, exists

from enthought.traits.api import Instance, Bool
from enthought.pyface.wizard.api import WizardPage

from pylon.plugin.resource.resource import Workspace, File

from pylon.plugin.resource.resource_tree_viewer import ResourceTreeViewer

#------------------------------------------------------------------------------
#  "ResourceSelectionPage" class:
#------------------------------------------------------------------------------

class ResourceSelectionPage(WizardPage):
    """ Wizard page for resource selection """

    #--------------------------------------------------------------------------
    #  "WizardPage" interface:
    #--------------------------------------------------------------------------

    complete = Bool(False)

    #--------------------------------------------------------------------------
    #  "ResourceSelectionPage" interface:
    #--------------------------------------------------------------------------

    # The workspace from which the file may be selected
    workspace = Instance(Workspace, allow_none=False)

    # The selected parent folder
    resource = Instance(File)

    #--------------------------------------------------------------------------
    #  "WizardPage" interface:
    #--------------------------------------------------------------------------

    def create_page(self, parent):
        """ Create the wizard page. """

        tree_viewer = ResourceTreeViewer(
            parent=parent, input=self.workspace,
            selection_mode="single", show_root=False
        )

        tree_viewer.on_trait_change(self.on_selection_change, "selection")

        return tree_viewer.control

    #--------------------------------------------------------------------------
    #  "ResourceSelectionPage" interface:
    #--------------------------------------------------------------------------

    def on_selection_change(self, selections):
        """ Handles the tree viewer selections changing """

        if selections:
            selection = selections[0]
            if isinstance(selection, File):
                self.resource = selection
                self.complete = True
            else:
                self.resource = None
                self.complete = False

# EOF -------------------------------------------------------------------------
