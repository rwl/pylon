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

""" Defines classes for creating a new folder with a wizard """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import expanduser, join, exists

from enthought.io.api import File

from enthought.traits.api import \
    HasTraits, Directory, Bool, Str, Property, Instance, cached_property, \
    Delegate, Event

from enthought.traits.ui.api import \
    View, Item, Group, Label, Heading, DirectoryEditor

from enthought.traits.ui.menu import OKCancelButtons
from enthought.pyface.wizard.api import SimpleWizard, WizardPage
from enthought.pyface.api import OK
from enthought.envisage.ui.workbench.api import WorkbenchWindow

from enthought.plugins.workspace.wizard.container_selection_page import \
    ContainerSelectionPage

from enthought.plugins.workspace.i_workspace import IWorkspace

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

WORKSPACE_VIEW = "enthought.plugins.workspace.workspace_view"

#------------------------------------------------------------------------------
#  "FolderWizardPage" class:
#------------------------------------------------------------------------------

class FolderWizardPage(WizardPage):
    """ Wizard page for folder creation """

    #--------------------------------------------------------------------------
    #  FolderWizardPage interface:
    #--------------------------------------------------------------------------

    # The folder name
    folder_name = Str

    csp = Instance(ContainerSelectionPage)
    # The location for the new project
#    parent_folder = Delegate("csp", "folder")

    # Absolute path for the project
#    abs_path = Property(Str, depends_on=["folder_name"])#, "parent_folder"])

    # A label with advice
#    _label = Property(
#        Str("Create a new folder resource."),
#        depends_on=["folder_name"]
#    )

    # Has the folder's name been changed
    _named = Bool(False)

    # The default view
    traits_view = View(
        Group(
            Heading("Folder"),
#            Item("_label", style="readonly", show_label=False),
            "_",
        ),
        Item("folder_name")
    )

#    @cached_property
#    def _get_abs_path(self):
#        """ Property getter """
#
#        return join(self.csp.directory, self.folder_name)


#    @cached_property
#    def _get__label(self):
#        """ Property getter """
#
#        abs_path = join(self.csp.directory, self.folder_name)
#        if (exists(abs_path)) and (len(self.folder_name) != 0):
#            l = "A folder with that name already exists."
#            self.complete = False
#        elif len(self.folder_name) == 0 and self._named:
#            l = "Folder name must be specified"
#            self.complete = False
#        elif len(self.folder_name) == 0:
#            l = "Create a new folder resource."
#            self.complete = False
#        else:
#            l = "Create a new folder resource."
#            self.complete = True
#
#        return l


    def _folder_name_changed(self):
        """ Sets a flag when the name is changed """

        self._named = True

        self.complete = True

    #--------------------------------------------------------------------------
    #  "WizardPage" interface:
    #--------------------------------------------------------------------------

    def create_page(self, parent):
        """ Create the wizard page. """

        ui = self.edit_traits(parent=parent, kind='subpanel')

        return ui.control

#------------------------------------------------------------------------------
#  "FolderWizard" class:
#------------------------------------------------------------------------------

class FolderWizard(SimpleWizard):
    """ A wizard for folder creation """

    # The dialog title
    title = Str("New Folder")

    #--------------------------------------------------------------------------
    #  "FolderWizard" interface:
    #--------------------------------------------------------------------------

    window = Instance(WorkbenchWindow)

    finished = Event

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, window, **traits):
        """ Returns a FolderWizard """

        if window is not None:
            self.window = window
            workspace = window.application.get_service(IWorkspace)
        else:
            workspace = None

        csp = ContainerSelectionPage(id="container_page", workspace=workspace)
        fwp = FolderWizardPage(id="folder_page")#, csp=csp)

        self.pages = [csp, fwp]

        super(FolderWizard, self).__init__(window=window, **traits)

    #--------------------------------------------------------------------------
    #  "FolderWizard" interface:
    #--------------------------------------------------------------------------

    def _finished_fired(self):
        """ Performs the folder resource creation if the wizard is
        finished successfully.

        """

        pass

        csp = self.pages[0]
        fwp = self.pages[1]

        path = join(csp.directory, fwp.folder_name)
        folder = File(path)
        folder.create_folder()

        # Refresh the workspace tree view
        view = self.window.get_view_by_id(WORKSPACE_VIEW)
        if view is not None:
            # FIXME: Refresh the parent folder not the whole tree
            workspace = self.window.application.get_service(IWorkspace)
            wtv = view.tree_viewer.refresh(workspace)

if __name__ == "__main__":
    wizard = FolderWizard(window=None)
    # Create and open the wizard.
    if wizard.open() == OK:
        print 'Wizard completed successfully'
    else:
        print 'Wizard cancelled'

# EOF -------------------------------------------------------------------------
