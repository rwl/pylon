#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard W. Lincoln
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

""" Defines a wizard for import PSS/E data files.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import pickle as pickle

from os.path import exists, basename, splitext, join

from enthought.io.api import File as IOFile
from enthought.traits.api import Str, File, Instance, Event
from enthought.pyface.wizard.api import SimpleWizard
from enthought.envisage.ui.workbench.workbench_window import WorkbenchWindow

from puddle.resource.i_workspace import IWorkspace
from puddle.resource.wizard.file_import_page import FileImportPage
from puddle.resource.action.open_action import OpenAction
from puddle.resource.resource_adapter import PickleFileIResourceAdapter
from puddle.resource.wizard.container_selection_page import \
    ContainerSelectionPage

from pylon.readwrite.api import read_psse

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

WORKSPACE_VIEW = "puddle.resource.resource_view"

#------------------------------------------------------------------------------
#  "PSSEImportPage" class:
#------------------------------------------------------------------------------

class PSSEImportPage(FileImportPage):
    """ Defines a wizard page for PSSE data file selection.
    """
    file_type = Str("PSS/E")

    data_file = File(exists=True,
        filter=["PSS/E Files (*.raw)|*.raw", "All Files|*.*"])

#------------------------------------------------------------------------------
#  "PSSEImportWizard" class:
#------------------------------------------------------------------------------

class PSSEImportWizard(SimpleWizard):
    """ Defines a wizard for importing a PSSE data file
    """

    # The dialog title
    title = Str("Import PSSE")

    #--------------------------------------------------------------------------
    #  "PSATImportWizard" interface:
    #--------------------------------------------------------------------------

    window = Instance(WorkbenchWindow)

    finished = Event

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, window, **traits):
        """ Returns a PSSEImportWizard.
        """
        self.window = window
        workspace = window.application.get_service(IWorkspace)

        csp = ContainerSelectionPage(id="container_page", workspace=workspace)
        fip = PSSEImportPage(id="file_page")

        self.pages = [csp, fip]

        super(PSSEImportWizard, self).__init__(**traits)


    def _finished_fired(self):
        """ Performs the network resource creation if the wizard is
            finished successfully.
        """
        workspace = self.window.application.get_service(IWorkspace)

        csp = self.pages[0]
        fip = self.pages[1]

        name, ext = splitext(basename(fip.data_file))
        file = IOFile(join(csp.directory, name+".pkl"))
        if not file.exists:
            n = read_psse(fip.data_file)
            resource = PickleFileIResourceAdapter(file)
            resource.save(n)

        self._open_resource(file)

        self._refresh_container(workspace)


    def _open_resource(self, file):
        """ Makes the file the current selection and opens it.
        """
        self.window.selection = [file]
        OpenAction(window=self.window).perform(event=None)


    def _refresh_container(self, container):
        """ Refreshes the workspace tree view.
        """
        view = self.window.get_view_by_id(WORKSPACE_VIEW)
        if view is not None:
            view.tree_viewer.refresh(container)

# EOF -------------------------------------------------------------------------