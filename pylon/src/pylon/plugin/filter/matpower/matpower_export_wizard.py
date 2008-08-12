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

""" Defines a wizard for exporting a resources to a MATPOWER data file """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import pickle as pickle

from os.path import exists, basename, splitext

from enthought.traits.api import \
    File, cached_property, Event, Str, Property, Instance

from enthought.pyface.wizard.api import SimpleWizard
from enthought.envisage.ui.workbench.workbench_window import WorkbenchWindow
from enthought.plugins.workspace.i_workspace import IWorkspace
from enthought.plugins.workspace.wizard.file_export_page import FileExportPage

from enthought.plugins.workspace.wizard.resource_selection_page import \
    ResourceSelectionPage

from enthought.plugins.workspace.resource_editor import PickledProvider

from pylon.filter.api import MATPOWERExporter

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

WORKSPACE_VIEW = "enthought.plugins.workspace.workspace_view"

#------------------------------------------------------------------------------
#  "MATPOWERExportPage" class:
#------------------------------------------------------------------------------

class MATPOWERExportPage(FileExportPage):
    """ Defines a wizard page for MATPOWER data file selection """

    file_type = Str("MATPOWER")

    data_file = File(
        exists=False, filter=["MATPOWER Files (*.m)|*.m", "All Files|*.*"]
    )

#------------------------------------------------------------------------------
#  "MATPOWERExportWizard" class:
#------------------------------------------------------------------------------

class MATPOWERExportWizard(SimpleWizard):
    """ Defines a wizard for exporting a resource to a MATPOWER data file """

    # The dialog title
    title = Str("Export MATPOWER")

    #--------------------------------------------------------------------------
    #  "MATPOWERExportWizard" interface:
    #--------------------------------------------------------------------------

    window = Instance(WorkbenchWindow)

    finished = Event

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, window, **traits):
        """ Returns a MATPOWERExportWizard """

        self.window = window
        workspace = window.application.get_service(IWorkspace)

        rsp = ResourceSelectionPage(id="resource_page", workspace=workspace)
        fep = MATPOWERExportPage(id="file_page")

        self.pages = [rsp, fep]

        super(MATPOWERExportWizard, self).__init__(**traits)

    #--------------------------------------------------------------------------
    #  "MATPOWERExportWizard" interface:
    #--------------------------------------------------------------------------

    def _finished_fired(self):
        """ Exports the selected resource to the selected file """

        workspace = self.window.application.get_service(IWorkspace)

        rsp = self.pages[0]
        fep = self.pages[1]

        n = PickledProvider().create_document(rsp.resource)
        MATPOWERExporter().export_network(n, fep.data_file)

# EOF -------------------------------------------------------------------------
