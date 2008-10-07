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
#  Date:   09/07/2008
#
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

import enthought.plugins.workspace.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = dirname(enthought.plugins.workspace.api.__file__)

WORKSPACE_VIEW = "enthought.plugins.workspace.workspace_view"

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
        from enthought.plugins.workspace.i_workspace import IWorkspace
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
