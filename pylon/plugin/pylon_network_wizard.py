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

""" Defines a wizard for network resource creation """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import pickle as pickle

from os.path import expanduser, join, exists, splitext

from enthought.io.api import File as IOFile

from enthought.traits.api import \
    HasTraits, Directory, Bool, Str, Float, Property, Instance, \
    cached_property, Event

from enthought.traits.ui.api import \
    View, Item, Group, Label, Heading, DirectoryEditor

from enthought.traits.ui.menu import OKCancelButtons
from enthought.pyface.wizard.api import SimpleWizard, WizardPage
from enthought.envisage.ui.workbench.workbench_window import WorkbenchWindow

from enthought.plugins.workspace.i_workspace import IWorkspace
from enthought.plugins.workspace.action.open_action import OpenAction

from enthought.plugins.workspace.wizard.container_selection_page import \
    ContainerSelectionPage

from enthought.plugins.workspace.resource_editor import PickledProvider

from pylon.api import Network

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

WORKSPACE_VIEW = "enthought.plugins.workspace.workspace_view"

#------------------------------------------------------------------------------
#  "NetworkWizardPage" class:
#------------------------------------------------------------------------------

class NetworkWizardPage(WizardPage):
    """ Wizard page for Network creation """

    network_name = Str

    base_mva = Float(100.0, desc="the base apparent power (MVA)")

    csp = Instance(ContainerSelectionPage)

    # Absolute path for the project
    abs_path = Property(Str, depends_on=["network_name"])

    # A label with advice
    _label = Property(
        Str("Create a new network model resource."),
        depends_on=["network_name"]
    )

    # Has the network's name been changed
    _named = Bool(False)

    # The default view
    traits_view = View(
        Group(
            Heading("Network"),
            Item("_label", style="readonly", show_label=False),
            "_",
        ),
        Item("network_name")
    )

    @cached_property
    def _get_abs_path(self):
        """ Property getter """

        return join(self.csp.directory, self.network_name)


    @cached_property
    def _get__label(self):
        """ Property getter """

        if (exists(self.abs_path)) and (len(self.network_name) != 0):
            l = "A network with that name already exists."
            self.complete = False
        elif len(self.network_name) == 0 and self._named:
            l = "Network name must be specified."
            self.complete = False
        elif self.network_name[-4:] != ".pyl":
            l = "The network file name must end in '.pyl'."
            self.complete = False
        elif len(self.network_name) == 0:
            l = "Create a new network model resource."
            self.complete = False
        else:
            l = "Create a new network model resource."
            self.complete = True

        return l


    def _network_name_changed(self):
        """ Sets a flag when the name is changed """

        self._named = True

    #--------------------------------------------------------------------------
    #  "WizardPage" interface:
    #--------------------------------------------------------------------------

    def create_page(self, parent):
        """ Creates the wizard page """

        ui = self.edit_traits(parent=parent, kind="subpanel")

        return ui.control

#------------------------------------------------------------------------------
#  "NetworkWizard" class:
#------------------------------------------------------------------------------

class NetworkWizard(SimpleWizard):
    """ A wizard for network resource creation """

    # The dialog title
    title = Str("New Network")

    #--------------------------------------------------------------------------
    #  "NetworkWizard" interface:
    #--------------------------------------------------------------------------

    window = Instance(WorkbenchWindow)

    finished = Event

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, window, **traits):
        """ Returns a NetworkWizard """

        self.window = window
        workspace = window.application.get_service(IWorkspace)

        csp = ContainerSelectionPage(id="container_page", workspace=workspace)
        nwp = NetworkWizardPage(id="network_page", csp=csp)

        self.pages = [csp, nwp]

        super(NetworkWizard, self).__init__(**traits)

    #--------------------------------------------------------------------------
    #  "NetworkWizard" interface:
    #--------------------------------------------------------------------------

    def _finished_fired(self):
        """ Performs the network resource creation if the wizard is
        finished successfully.

        """

        workspace = self.window.application.get_service(IWorkspace)

        csp = self.pages[0]
        nwp = self.pages[1]

        file = IOFile(join(csp.directory, nwp.network_name))
        if not file.exists:
            name, ext = splitext(nwp.network_name)
            n = Network(name=name, mva_base=nwp.base_mva)
#            file.create_file(contents=pickle.dumps(n))
            PickledProvider().do_save(file, n)

        self._open_resource(file)

        self._refresh_container(workspace)


    def _open_resource(self, file):
        """ Makes the file the current selection and opens it """

        self.window.selection = [file]
        OpenAction(window=self.window).perform(event=None)


    def _refresh_container(self, container):
        """ Refreshes the workspace tree view """

        view = self.window.get_view_by_id(WORKSPACE_VIEW)
        if view is not None:
            view.tree_viewer.refresh(container)

# EOF -------------------------------------------------------------------------
