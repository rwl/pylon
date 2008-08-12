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
#  Date:   14/06/2008
#
#------------------------------------------------------------------------------

""" Defines a wizard page for resource selection """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import expanduser, join, exists

from enthought.traits.api import Instance, Bool
from enthought.pyface.wizard.api import WizardPage
from enthought.plugins.workspace.workspace_resource import Workspace, File
from enthought.plugins.workspace.workspace_tree_viewer import \
    WorkspaceTreeViewer

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

        tree_viewer = WorkspaceTreeViewer(
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
