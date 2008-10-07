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

from enthought.traits.api import Bool

from enthought.pyface.api import ImageResource

from enthought.pyface.action.api import Action

import enthought.plugins.workspace.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = dirname(enthought.plugins.workspace.api.__file__)

#------------------------------------------------------------------------------
#  "SaveAllAction" class:
#------------------------------------------------------------------------------

class SaveAllAction(Action):
    """ Defines an action that save the contents of all dirty editors """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Save all unsaved changes"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "Sav&e All"

    # A short description of the action used for tooltip text etc:
    tooltip = "Save All (Shift+Ctrl+S)"

    # The action's image (displayed on tool bar tools etc):
    image = ImageResource("save_all", search_path=[IMAGE_LOCATION])

    # Keyboard accelerator
    accelerator = "Shift+Ctrl+S"

    # Is the action enabled?
    enabled = Bool(False)

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

    def __init__(self, **traits):
        """ Returns a new SaveAllAction """
        super(SaveAllAction, self).__init__(**traits)

        if traits.has_key("window"):
            traits["window"].on_trait_change(
                self.on_editors_change, "editors_items"
            )

    #--------------------------------------------------------------------------
    #  "SaveAllAction" interface:
    #--------------------------------------------------------------------------

    def on_editors_change(self, event):
        """ Sets up static event handlers for all workbench editors """

        for editor in event.removed:
            editor.on_trait_change(self.on_editor_dirt, "dirty", remove=True)

        for editor in event.added:
            editor.on_trait_change(self.on_editor_dirt, "dirty")

        # Perform an sweep of the editors
        self.on_editor_dirt(None)


#    @on_trait_change("window.editors.dirty")
    def on_editor_dirt(self, dirty):
        """ Enables the action when any editor is dirty """

        self.enabled = bool([e for e in self.window.editors if e.dirty])

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def perform(self, event):
        """ Performs the action """

        for editor in self.window.editors:
            editor.save()

# EOF -------------------------------------------------------------------------
