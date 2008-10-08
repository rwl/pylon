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

""" Defines an action for moving the workspace to the parent directory """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import dirname

from enthought.traits.api import Bool, Instance
from enthought.pyface.api import ImageResource
from enthought.pyface.action.api import Action
from enthought.envisage.ui.workbench.api import WorkbenchWindow

import pylon.plugin.resource.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = dirname(pylon.plugin.resource.api.__file__)

WORKSPACE_VIEW = "pylon.plugin.resource.resource_view"

#------------------------------------------------------------------------------
#  "UpAction" class:
#------------------------------------------------------------------------------

class UpAction(Action):
    """ Defines an action for moving the workspace to the parent directory """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Move workspace to the parent directory"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "&Up"

    # A short description of the action used for tooltip text etc:
    tooltip = "Open parent directory"

    # Keyboard accelerator:
    accelerator = "Alt+Up"

    # The action's image (displayed on tool bar tools etc):
    image = ImageResource("up", search_path=[IMAGE_LOCATION])

    #--------------------------------------------------------------------------
    #  "UpAction" interface:
    #--------------------------------------------------------------------------

    window = Instance(WorkbenchWindow)

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

#    def __init__(self, **traits):
#        """ Returns a new UpAction """
#        super(UpAction, self).__init__(**traits)

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def perform(self, event):
        """ Perform the action """

        # Note that we always offer the service via its name, but look it up
        # via the actual protocol.
        from pylon.plugin.resource.i_workspace import IWorkspace

        workspace = self.window.application.get_service(IWorkspace)

        workspace.path = dirname(workspace.absolute_path)

        view = self.window.get_view_by_id(WORKSPACE_VIEW)
        if view is not None:
            workspace = self.window.application.get_service(IWorkspace)
            view.tree_viewer.refresh(workspace)

# EOF -------------------------------------------------------------------------
