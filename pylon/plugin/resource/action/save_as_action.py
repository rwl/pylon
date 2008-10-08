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

""" Defines an action for saving to a new name """

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

#------------------------------------------------------------------------------
#  "SaveAsAction" class:
#------------------------------------------------------------------------------

class SaveAsAction(Action):
    """ Defines an action that save the contents of the current editor to
    a new name.

    """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Save the active editor's changes to a new file"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "Save As..."

    # A short description of the action used for tooltip text etc:
    tooltip = "Save As"

    # The action's image (displayed on tool bar tools etc):
    image = ImageResource("save_as", search_path=[IMAGE_LOCATION])

    # Is the action enabled?
    enabled = Bool(False)

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

#    def __init__(self, **traits):
#        """ Returns a new SaveAction """
#        super(SaveAction, self).__init__(**traits)
#
#        if traits.has_key("window"):
#            traits["window"].on_trait_change(
#                self.on_editor_change, "active_editor"
#            )
#
#    #--------------------------------------------------------------------------
#    #  "SaveAction" interface:
#    #--------------------------------------------------------------------------
#
#    def on_editor_change(self, obj, name, old, new):
#        """ Sets up static event handlers for change in the clean state
#        of the active editor
#
#        """
#
#        if old is not None:
#            old.on_trait_change(self.active_editor_dirt, "dirty", remove=True)
#
#        if new is not None:
#            new.on_trait_change(self.active_editor_dirt, "dirty")
#            self.active_editor_dirt(dirty=new.dirty)

    #--------------------------------------------------------------------------
    #  "SaveAction" interface:
    #--------------------------------------------------------------------------

    window = Instance(WorkbenchWindow)

    #--------------------------------------------------------------------------
    #  "SaveAction" interface:
    #--------------------------------------------------------------------------

    def _active_editor_changed_for_window(self):
        """ Enables the action if the window has editors """

        if self.window.editors:
            self.enabled = True
        else:
            self.enabled = False

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def perform(self, event):
        """ Performs the action """

        active_editor = self.window.active_editor
        if self.enabled and (active_editor is not None):
            active_editor.save_as()

# EOF -------------------------------------------------------------------------
