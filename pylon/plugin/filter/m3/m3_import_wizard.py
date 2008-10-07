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

""" Defines a wizard for import M3 data files """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import pickle as pickle

from os.path import exists, basename, splitext, join

from enthought.io.api import File as IOFile
from enthought.traits.api import Str, File, Instance, Event
from enthought.pyface.wizard.api import SimpleWizard
from enthought.envisage.ui.workbench.workbench_window import WorkbenchWindow
from enthought.plugins.workspace.i_workspace import IWorkspace
from enthought.plugins.workspace.wizard.file_import_page import FileImportPage
from enthought.plugins.workspace.action.open_action import OpenAction
from enthought.plugins.workspace.wizard.container_selection_page import \
    ContainerSelectionPage

from pylon.filter.api import M3Importer

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

WORKSPACE_VIEW = "enthought.plugins.workspace.workspace_view"

#------------------------------------------------------------------------------
#  "M3ImportPage" class:
#------------------------------------------------------------------------------

class M3ImportPage(FileImportPage):
    """ Defines a wizard page for M3 data file selection """

    file_type = Str("M3")

#------------------------------------------------------------------------------
#  "M3ImportWizard" class:
#------------------------------------------------------------------------------

class M3ImportWizard(SimpleWizard):
    """ Defines a wizard for importing a M3 data file """

    # The dialog title
    title = Str("Import M3")

    #--------------------------------------------------------------------------
    #  "PSATImportWizard" interface:
    #--------------------------------------------------------------------------

    window = Instance(WorkbenchWindow)

    finished = Event

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, window, **traits):
        """ Returns a M3ImportWizard """

        self.window = window
        workspace = window.application.get_service(IWorkspace)

        csp = ContainerSelectionPage(id="container_page", workspace=workspace)
        fip = M3ImportPage(id="file_page")

        self.pages = [csp, fip]

        super(M3ImportWizard, self).__init__(**traits)


    def _finished_fired(self):
        """ Performs the network resource creation if the wizard is
        finished successfully.

        """

        workspace = self.window.application.get_service(IWorkspace)

        csp = self.pages[0]
        fip = self.pages[1]

        name, ext = splitext(basename(fip.data_file))
        file = IOFile(join(csp.directory, name+".pyl"))
        if not file.exists:
            n = M3Importer().parse_file(fip.data_file)
            file.create_file(contents=pickle.dumps(n))

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