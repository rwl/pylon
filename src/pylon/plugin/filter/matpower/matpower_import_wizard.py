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

""" Defines a wizard for import of MATPOWER data files """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import pickle as pickle

from os.path import exists, basename, splitext, join

from enthought.traits.api import \
    File, cached_property, Event, Str, Property, Instance

from enthought.io.api import File as IOFile
from enthought.traits.ui.api import View, Group, Item, Heading
from enthought.pyface.wizard.api import SimpleWizard, WizardPage
from enthought.envisage.ui.workbench.workbench_window import WorkbenchWindow
from enthought.plugins.workspace.i_workspace import IWorkspace
from enthought.plugins.workspace.wizard.file_import_page import FileImportPage
from enthought.plugins.workspace.action.open_action import OpenAction

from enthought.plugins.workspace.wizard.container_selection_page import \
    ContainerSelectionPage
    
from enthought.plugins.workspace.workspace_resource_editor import \
    FileIResourceAdapter

from pylon.filter.api import MATPOWERImporter

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

WORKSPACE_VIEW = "enthought.plugins.workspace.workspace_view"

#------------------------------------------------------------------------------
#  "MATPOWERImportPage" class:
#------------------------------------------------------------------------------

class MATPOWERImportPage(FileImportPage):
    """ Defines a wizard page for MATPOWER data file selection """

    file_type = Str("MATPOWER")

    data_file = File(
        exists=True, filter=["MATPOWER Files (*.m)|*.m|All Files (*.*)|*.*"]
    )

#    traits_view = View(
#        Group(
#            Heading("MATPOWER"),
#            Item("_label", style="readonly", show_label=False),
#            "_",
#        ),
#        Item("data_file")
#    )

#------------------------------------------------------------------------------
#  "MATPOWERImportWizard" class:
#------------------------------------------------------------------------------

class MATPOWERImportWizard(SimpleWizard):
    """ Defines a wizard for importing a MATPOWER data file """

    # The dialog title
    title = Str("Import MATPOWER")

    #--------------------------------------------------------------------------
    #  "MATPOWERImportWizard" interface:
    #--------------------------------------------------------------------------

    window = Instance(WorkbenchWindow)

    finished = Event

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, window, **traits):
        """ Returns a MATPOWERImportWizard """

        self.window = window
        workspace = window.application.get_service(IWorkspace)

        csp = ContainerSelectionPage(id="container_page", workspace=workspace)
        mip = MATPOWERImportPage(id="file_page")

        self.pages = [csp, mip]

        super(MATPOWERImportWizard, self).__init__(**traits)


    def _finished_fired(self):
        """ Performs the network resource creation if the wizard is
        finished successfully.

        """

        workspace = self.window.application.get_service(IWorkspace)

        csp = self.pages[0]
        mip = self.pages[1]

        name, ext = splitext(basename(mip.data_file))
        file = IOFile(join(csp.directory, name+".pyl"))
        if not file.exists:
            n = MATPOWERImporter().parse_file(mip.data_file)
#            file.create_file(contents=pickle.dumps(n))
            resource = FileIResourceAdapter(file)
            resource.save(n)

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
