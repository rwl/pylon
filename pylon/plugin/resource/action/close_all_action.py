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

""" Defines an action for closing all editors """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import dirname

from enthought.traits.api import Bool
from enthought.pyface.api import ImageResource
from enthought.pyface.action.api import Action

import pylon.plugin.resource.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = dirname(pylon.plugin.resource.api.__file__)

#------------------------------------------------------------------------------
#  "CloseAllAction" class:
#------------------------------------------------------------------------------

class CloseAllAction(Action):
    """ An action for closing all editors """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Close all editors"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "C&lose All"

    # A short description of the action used for tooltip text etc:
    tooltip = "Close All (Shift+Ctrl+W)"

    # Keyboard accelerator:
    accelerator = "Shift+Ctrl+W"

    # Is the action enabled?
    enabled = Bool(False)

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, **traits):
        """ Returns a new CloseAllAction """
        super(CloseAllAction, self).__init__(**traits)

        if traits.has_key("window"):
            traits["window"].on_trait_change(
                self.on_editors_change, "editors_items"
            )

    #--------------------------------------------------------------------------
    #  "CloseAllAction" interface:
    #--------------------------------------------------------------------------

    def on_editors_change(self, event):
        """ Enables the action if the window has editors """

        if self.window.editors:
            self.enabled = True
        else:
            self.enabled = False

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def perform(self, event):
        """ Perform the action. """

        editors = self.window.editors[:]

        for editor in editors:
            self.window.close_editor(editor)

# EOF -------------------------------------------------------------------------
