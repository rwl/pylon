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

""" Workspace plug-in actions """

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

#------------------------------------------------------------------------------
#  "SaveAction" class:
#------------------------------------------------------------------------------

class SaveAction(Action):
    """ Defines an action that save the contents of the current editor to
    the workspace

    """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Save the active editor's changes"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "Save"

    # A short description of the action used for tooltip text etc:
    tooltip = "Save (Ctrl+S)"

    # The action's image (displayed on tool bar tools etc):
    image = ImageResource("save", search_path=[IMAGE_LOCATION])

    # Keyboard accelerator
    accelerator = "Ctrl+S"

    # Is the action enabled?
    enabled = Bool(False)

    #--------------------------------------------------------------------------
    #  "SaveAction" interface:
    #--------------------------------------------------------------------------

    window = Instance(WorkbenchWindow)

    #--------------------------------------------------------------------------
    #  "SaveAction" interface:
    #--------------------------------------------------------------------------

    def _active_editor_changed_for_window(self, obj, name, old, new):
        """ Sets up static event handlers for change in the clean state
        of the active editor

        """

        if old is not None:
            old.on_trait_change(self.active_editor_dirt, "dirty", remove=True)

        if new is not None:
            new.on_trait_change(self.active_editor_dirt, "dirty")
            self.active_editor_dirt(dirty=new.dirty)

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

    #--------------------------------------------------------------------------
    #  "SaveAction" interface:
    #--------------------------------------------------------------------------

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


    def active_editor_dirt(self, dirty):
        """ Enables the action if the active editor is dirty """

        if dirty:
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
            active_editor.save()

# EOF -------------------------------------------------------------------------
