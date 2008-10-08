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

""" Defines an action for moving the workspace to a new location """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import dirname, expanduser

from enthought.traits.api import Bool, Instance
from enthought.pyface.api import ImageResource
from enthought.pyface.action.api import Action
from enthought.envisage.ui.workbench.workbench_window import WorkbenchWindow

from move_action import DirectorySelection

import pylon.plugin.resource.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = dirname(pylon.plugin.resource.api.__file__)

WORKSPACE_VIEW = "pylon.plugin.resource.resource_view"

#------------------------------------------------------------------------------
#  "LocationAction" class:
#------------------------------------------------------------------------------

class LocationAction(Action):
    """ An action for moving the workspace to a new location """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Move the workspace to a new location"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "&Location..."

    # A short description of the action used for tooltip text etc:
    tooltip = "Move workspace location"

    # Keyboard accelerator:
    accelerator = "Ctrl+L"

    # The action's image (displayed on tool bar tools etc):
#    image = ImageResource("home_folder", search_path=[IMAGE_LOCATION])

    #--------------------------------------------------------------------------
    #  "LocationAction" interface:
    #--------------------------------------------------------------------------

    window = Instance(WorkbenchWindow)

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def perform(self, event):
        """ Perform the action """

        # Note that we always offer the service via its name, but look it up
        # via the actual protocol.
        from pylon.plugin.resource.i_workspace import IWorkspace
        workspace = self.window.application.get_service(IWorkspace)

        ds = DirectorySelection(directory=dirname(workspace.absolute_path))

        retval = ds.edit_traits(parent=self.window.control, kind="livemodal")

        if retval.result:
            workspace.path = ds.directory

            # Refresh the workspace tree view
            view = self.window.get_view_by_id(WORKSPACE_VIEW)
            if view is not None:
                view.tree_viewer.refresh(workspace)

# EOF -------------------------------------------------------------------------
