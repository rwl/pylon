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

""" Defines an action for closing the current editor """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import dirname

from enthought.traits.api import Bool, Instance
from enthought.pyface.api import ImageResource
from enthought.pyface.action.api import Action
from enthought.envisage.ui.workbench.workbench_window import WorkbenchWindow

import enthought.plugins.workspace.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = dirname(enthought.plugins.workspace.api.__file__)

#------------------------------------------------------------------------------
#  "CloseAction" class:
#------------------------------------------------------------------------------

class CloseAction(Action):
    """ An action for closing the current editor """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Close the current editor"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "&Close"

    # A short description of the action used for tooltip text etc:
    tooltip = "Close (Ctrl+W)"

    # Keyboard accelerator:
    accelerator = "Ctrl+W"

    # Is the action enabled?
    enabled = Bool(False)

    #--------------------------------------------------------------------------
    #  "CloseAction" interface:
    #--------------------------------------------------------------------------

    window = Instance(WorkbenchWindow)

    #--------------------------------------------------------------------------
    #  "object" interface:
    #--------------------------------------------------------------------------

#    def __init__(self, **traits):
#        """ Returns a new CloseAction """
#        super(CloseAction, self).__init__(**traits)
#
#        if traits.has_key("window"):
#            traits["window"].on_trait_change(
#                self.on_editors_change, "editors_items"
#            )

    #--------------------------------------------------------------------------
    #  "CloseAction" interface:
    #--------------------------------------------------------------------------

    def _selection_changed_for_window(self, event):
        """ Enables the action if the window has editors """

        if self.window.editors:
            self.enabled = True
        else:
            self.enabled = False

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def perform(self, event):
        """ Perform the action """

        editor = self.window.active_editor

        if editor is not None:
            self.window.close_editor(editor)

# EOF -------------------------------------------------------------------------
