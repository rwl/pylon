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

""" Defines an action for refreshing a resource """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import dirname

from enthought.io.api import File
from enthought.traits.api import Bool, Instance
from enthought.pyface.action.api import Action
from enthought.pyface.api import ImageResource

from pylon.plugin.resource.i_workspace import IWorkspace

import pylon.plugin.resource.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = dirname(pylon.plugin.resource.api.__file__)

WORKSPACE_VIEW = "pylon.plugin.resource.resource_view"

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
