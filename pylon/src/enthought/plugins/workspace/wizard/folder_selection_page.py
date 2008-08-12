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

""" Defines classes for use as dialog boxes with the workspace plug-in """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import expanduser, join, exists

from enthought.io.api import File

from enthought.traits.api import \
    HasTraits, Directory, Bool, Str, Property, Instance, cached_property

from enthought.pyface.wizard.api import SimpleWizard, WizardPage

from enthought.plugins.workspace.workspace_tree_viewer import \
    WorkspaceTreeViewer, AllowOnlyFolders

from enthought.plugins.workspace.workspace_resource import Workspace

#------------------------------------------------------------------------------
#  "FolderSelectionWizardPage" class:
#------------------------------------------------------------------------------

class FolderSelectionWizardPage(WizardPage):
    """ Wizard page for parent folder selection """

    # The workspace from which the folder may be selected
    workspace = Instance(Workspace, allow_none=False)

    # The selected parent folder
    folder = Instance(File)

    #--------------------------------------------------------------------------
    #  "WizardPage" interface:
    #--------------------------------------------------------------------------

    def create_page(self, parent):
        """ Create the wizard page. """

        tree_viewer = WorkspaceTreeViewer(
            parent=parent, input=self.workspace,
#            filters=[AllowOnlyFolders()],
            show_root=False
        )

        tree_viewer.on_trait_change(self.on_selection_change, "selection")

        return tree_viewer.control


    def on_selection_change(self, selection):
        """ Relates the folder selected in the tree viewer to the wizard
        page's folder trait.

        """

        if selection:
            self.folder = selection[0]


    def _folder_changed(self, new):
        """ Complete the wizard when an existing folder is set """

        if (new is not None) and new.exists:
            self.complete = True
        else:
            self.complete = False

# EOF -------------------------------------------------------------------------
