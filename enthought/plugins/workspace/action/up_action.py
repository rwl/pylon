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

""" Defines an action for moving the workspace to the parent directory """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import dirname

from enthought.traits.api import Bool, Instance
from enthought.pyface.api import ImageResource
from enthought.pyface.action.api import Action
from enthought.envisage.ui.workbench.api import WorkbenchWindow

import enthought.plugins.workspace.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = dirname(enthought.plugins.workspace.api.__file__)

WORKSPACE_VIEW = "enthought.plugins.workspace.workspace_view"

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
        from enthought.plugins.workspace.i_workspace import IWorkspace

        workspace = self.window.application.get_service(IWorkspace)

        workspace.path = dirname(workspace.absolute_path)

        view = self.window.get_view_by_id(WORKSPACE_VIEW)
        if view is not None:
            # Note that we always offer the service via its name, but look
            # it up via the actual protocol.
            from enthought.plugins.workspace.i_workspace import IWorkspace
            workspace = self.window.application.get_service(IWorkspace)
            view.tree_viewer.refresh(workspace)

# EOF -------------------------------------------------------------------------
