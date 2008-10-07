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

""" Defines a wizard for swarm resource creation """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import pickle as pickle

from os.path import expanduser, join, exists, splitext, join

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
    
from enthought.plugins.workspace.workspace_resource_editor import \
    FileIResourceAdapter

from pylon.pyreto.api import MarketEnvironment

from pyqle.api import Swarm

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

WORKSPACE_VIEW = "enthought.plugins.workspace.workspace_view"

#------------------------------------------------------------------------------
#  "SwarmWizardPage" class:
#------------------------------------------------------------------------------

class SwarmWizardPage(WizardPage):
    """ Wizard page for swarm creation """

    swarm_name = Str

    csp = Instance(ContainerSelectionPage)

    # Absolute path for the project
    abs_path = Property(Str, depends_on=["swarm_name"])

    # A label with instructions
    _label = Property(Str, depends_on=["swarm_name"])

    # Has the swarm's name been changed
    _named = Bool(False)

    # The default view
    traits_view = View(
        Group(
            Heading("Swarm"),
            Item("_label", style="readonly", show_label=False),
            "_",
        ),
        Item("swarm_name")
    )

    #--------------------------------------------------------------------------
    #  "SwarmWizardPage" interface:
    #--------------------------------------------------------------------------

    @cached_property
    def _get_abs_path(self):
        """ Property getter """

        return join(self.csp.directory, self.swarm_name)


    @cached_property
    def _get__label(self):
        """ Property getter """

        if (exists(self.abs_path)) and (len(self.swarm_name) != 0):
            l = "A swarm with that name already exists."
            self.complete = False
        elif len(self.swarm_name) == 0 and self._named:
            l = "Swarm name must be specified."
            self.complete = False
        elif self.swarm_name[-4:] != ".pyr":
            l = "The swarm file name must end in '.pyr'."
            self.complete = False
        elif len(self.swarm_name) == 0:
            l = "Create a new swarm model resource."
            self.complete = False
        else:
            l = "Create a new swarm model resource."
            self.complete = True

        return l


    def _swarm_name_changed(self):
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
#  "SwarmWizard" class:
#------------------------------------------------------------------------------

class SwarmWizard(SimpleWizard):
    """ A wizard for swarm resource creation """

    # The dialog title
    title = Str("New Swarm")

    #--------------------------------------------------------------------------
    #  "SwarmWizard" interface:
    #--------------------------------------------------------------------------

    window = Instance(WorkbenchWindow)

    finished = Event

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, window, **traits):
        """ Returns a SwarmWizard """

        self.window = window
        workspace = window.application.get_service(IWorkspace)

        csp = ContainerSelectionPage(id="container_page", workspace=workspace)
        swp = SwarmWizardPage(id="swarm_page", csp=csp)

        self.pages = [csp, swp]

        super(SwarmWizard, self).__init__(**traits)

    #--------------------------------------------------------------------------
    #  "SwarmWizard" interface:
    #--------------------------------------------------------------------------

    def _finished_fired(self):
        """ Performs the swarm resource creation if the wizard is
        finished successfully.

        """

        workspace = self.window.application.get_service(IWorkspace)

        csp = self.pages[0]
        swp = self.pages[1]

        file = IOFile(join(csp.directory, swp.swarm_name))
        if not file.exists:
            name, ext = splitext(swp.swarm_name)
            env = MarketEnvironment(network=None)
            swarm = Swarm(name=name, environment=env)
#            file.create_file(contents=pickle.dumps(swarm))
            resource = FileIResourceAdapter(file)
            resource.save(swarm)

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
