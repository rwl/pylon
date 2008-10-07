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

""" Defines classes for creating a new resource with a wizard """

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

from enthought.plugins.workspace.wizard.container_selection_page import \
    ContainerSelectionPage

from enthought.envisage.ui.workbench.workbench_window import WorkbenchWindow

from enthought.plugins.workspace.i_workspace import IWorkspace
from enthought.plugins.workspace.action.open_action import OpenAction

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

WORKSPACE_VIEW = "enthought.plugins.workspace.workspace_view"

#------------------------------------------------------------------------------
#  "ResourceWizardPage" class:
#------------------------------------------------------------------------------

class ResourceWizardPage(WizardPage):
    """ Wizard page for resource creation """

    #--------------------------------------------------------------------------
    #  ResourceWizardPage interface:
    #--------------------------------------------------------------------------

    # The folder name
    resource_name = Str

    csp = Instance(ContainerSelectionPage)

    # Absolute path for the resource
    abs_path = Property(Str, depends_on=["resource_name"])

    # A label with advice
    _label = Property(
        Str("Create a new resource."), depends_on=["resource_name"]
    )

    # Has the folder's name been changed
    _named = Bool(False)

    # The default view
    traits_view = View(
        Group(
            Heading("Resource"),
            Item("_label", style="readonly", show_label=False),
            "_",
        ),
        Item("resource_name", label="Name")
    )

    @cached_property
    def _get_abs_path(self):
        """ Property getter """

        return join(self.csp.directory, self.resource_name)


    @cached_property
    def _get__label(self):
        """ Property getter """

        if (exists(self.abs_path)) and (len(self.resource_name) != 0):
            l = "A resource with that name already exists."
            self.complete = False
        elif len(self.resource_name) == 0 and self._named:
            l = "Resource name must be specified"
            self.complete = False
        elif len(self.resource_name) == 0:
            l = "Create a new resource."
            self.complete = False
        else:
            l = "Create a new resource."
            self.complete = True

        return l


    def _resource_name_changed(self):
        """ Sets a flag when the name is changed """

        self._named = True

    #--------------------------------------------------------------------------
    #  "WizardPage" interface:
    #--------------------------------------------------------------------------

    def create_page(self, parent):
        """ Create the wizard page. """

        ui = self.edit_traits(parent=parent, kind='subpanel')

        return ui.control

#------------------------------------------------------------------------------
#  "BaseResourceWizard" class:
#------------------------------------------------------------------------------

class BaseResourceWizard(SimpleWizard):
    """ A base wizard for resource creation.  This will just create a file
    at the location specified in the wizard pages.  Override the
    _finished_fired() method in a subclass for other resource types.

    """

    # The dialog title
    title = Str("New Resource")

    #--------------------------------------------------------------------------
    #  "FolderWizard" interface:
    #--------------------------------------------------------------------------

    window = Instance(WorkbenchWindow)

    finished = Event

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, window, **traits):
        """ Returns a BaseResourceWizard """

        self.window = window

        workspace = window.application.get_service(IWorkspace)

        container_page = ContainerSelectionPage(
            id="container_page", workspace=workspace
        )

        resource_page = ResourceWizardPage(
            id="resource_page", csp=container_page
        )

        self.pages = [container_page, resource_page]

        super(BaseResourceWizard, self).__init__(**traits)

    #--------------------------------------------------------------------------
    #  "BaseResourceWizard" interface:
    #--------------------------------------------------------------------------

    def _finished_fired(self):
        """ This will just create a file at the location specified in the
        wizard pages.  Override this method in a subclass for other resource
        types.

        """

        container_page = self.pages[0]
        resource_page = self.pages[1]

        resource = File(resource_page.abs_path)
        resource.create_file()

        self._open_resource(file)
        # FIXME: Refresh the parent folder not the whole tree
        workspace = self.window.application.get_service(IWorkspace)
        self._refresh_container(workspace)


    def _open_resource(self, resource):
        """ Makes the file the current selection and opens it """

        self.window.selection = [resource]
        OpenAction(window=self.window).perform(event=None)


    def _refresh_container(self, container):
        """ Refreshes the workspace tree view """

        view = self.window.get_view_by_id(WORKSPACE_VIEW)
        if view is not None:
            view.tree_viewer.refresh(container)

# EOF -------------------------------------------------------------------------
