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

#from enthought.plugins.workspace.workspace_resource import Workspace

#------------------------------------------------------------------------------
#  "FolderSelectionWizardPage" class:
#------------------------------------------------------------------------------

class FolderSelectionWizardPage(WizardPage):
    """ Wizard page for parent folder selection """

    # The workspace from which the folder may be selected
    workspace = Instance(File, allow_none=False)

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
