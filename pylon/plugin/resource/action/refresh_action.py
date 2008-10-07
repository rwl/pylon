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
#  Date:   24/07/2008
#
#------------------------------------------------------------------------------

""" Defines an action for refreshing a resource """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import dirname

from enthought.io.api import File
from enthought.traits.api import Bool, Instance
from enthought.pyface.action.api import Action
from enthought.pyface.api import ImageResource
from enthought.plugins.workspace.i_workspace import IWorkspace

import enthought.plugins.workspace.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = dirname(enthought.plugins.workspace.api.__file__)

WORKSPACE_VIEW = "enthought.plugins.workspace.workspace_view"

#------------------------------------------------------------------------------
#  "RefreshAction" class:
#------------------------------------------------------------------------------

class RefreshAction(Action):
    """ Defines an action for refreshing a resource  """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "Re&fresh"

    # Keyboard accelerator:
    accelerator = "F5"

    # The action's image (displayed on tool bar tools etc):
    image = ImageResource("refresh", search_path=[IMAGE_LOCATION])

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def perform(self, event):
        """ Perform the action """

        selections = self.window.selection

        if selections:
            selection = selections[0]
            if isinstance(selection, File):
                view = self.window.get_view_by_id(WORKSPACE_VIEW)
                if view is not None:
                    view.tree_viewer.refresh(selection)


# EOF -------------------------------------------------------------------------
