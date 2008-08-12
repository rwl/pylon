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

""" Defines an action for closing all editors """

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
