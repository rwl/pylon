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

import logging

from enthought.io.api import File
from enthought.traits.api import Bool, Str, List, Delegate, Instance
from enthought.pyface.action.api import Action
from enthought.plugins.workspace.editor import Editor
from enthought.envisage.ui.workbench.workbench_window import WorkbenchWindow

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  "OpenWithAction" class:
#------------------------------------------------------------------------------

class OpenWithAction(Action):
    """ Defines an action that open the current resource """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # The action"s name (displayed on menus/tool bar tools etc):
    name = Delegate("editor")

    # The action's image (displayed on tool bar tools etc):
    image = Delegate("editor")

    # Is the action enabled?
    enabled = Bool(True)

    # Is the action visible?
    visible = Bool(True)

    #--------------------------------------------------------------------------
    #  "OpenWithAction" interface:
    #--------------------------------------------------------------------------

    # The workbench window that the menu is part of.
    window = Instance(WorkbenchWindow)

    # The editor extension
    editor = Instance(Editor)

    #--------------------------------------------------------------------------
    #  "OpenWithAction" interface:
    #--------------------------------------------------------------------------

    def _selection_changed_for_window(self, new):
        """ Makes the action visible iff a File with a valid extension
        is selected

        """

#        print "SELECTION CHANGED (OPEN WITH):", new

        if len(new) == 1:
            sel = new[0]
            if isinstance(sel, File) and (sel.ext in self.editor.extensions):
#                    self.visible = True
                    self.enabled = True
            else:
#                self.visible = False
                self.enabled = False
        else:
#            self.visible = False
            self.enabled = False

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def _enabled_default(self):
        """ Trait initialiser """

        if self.window.selection:
            sel = self.window.selection[0]
            if isinstance(sel, File) and (sel.ext in self.editor.extensions):
                return True
            else:
                return False
        else:
            return False


#    def _visible_default(self):
#        """ Trait initialiser """
#
#        if self.window.selection:
#            sel = self.window.selection[0]
#            if isinstance(sel, File) and (sel.ext in self.editor.extensions):
#                return True
#            else:
#                return False
#        else:
#            return False


    def perform(self, event):
        """ Performs the action """

        selections = self.window.selection
        if selections:
            # Use the first of the selected objects
            selection = selections[0]

            app = self.window.application
            editor = app.import_symbol(self.editor.editor_class)
            self.window.edit(selection, editor)


# EOF -------------------------------------------------------------------------
