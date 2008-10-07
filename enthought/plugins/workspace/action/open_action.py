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
from enthought.traits.api import Bool, Instance
from enthought.pyface.action.api import Action
from enthought.envisage.ui.workbench.workbench_window import WorkbenchWindow

from enthought.plugins.workspace.resource_editor import ResourceEditor

logger = logging.getLogger(__name__)

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

EDITORS = "enthought.plugins.workspace.editors"

#------------------------------------------------------------------------------
#  "OpenAction" class:
#------------------------------------------------------------------------------

class OpenAction(Action):
    """ Defines an action that open the current resource """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Open the active resource"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "Open"

    # A short description of the action used for tooltip text etc:
    tooltip = "Open"

    # Is the action enabled?
    enabled = Bool(True)

    # Is the action visible?
    visible = Bool(False)

    #--------------------------------------------------------------------------
    #  "CloseAction" interface:
    #--------------------------------------------------------------------------

    window = Instance(WorkbenchWindow)

    #--------------------------------------------------------------------------
    #  "OpenAction" interface:
    #--------------------------------------------------------------------------

    def _selection_changed_for_window(self, selections):
        """ Makes the action visible iff a File is selected """

        if selections:
            selection = selections[0]
            # Enable the action if a valid editor has been contributed
            editors = self.window.application.get_extensions(EDITORS)
            exts = [ext for factory in editors for ext in factory().extensions]
            if isinstance(selection, File) and (selection.ext in exts):
                self.enabled = True
            else:
                self.enabled = False
        else:
            self.enabled = False

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def _enabled_default(self):
        """ Trait initialiser """

        sel = self.window.selection

        editors = self.window.application.get_extensions(EDITORS)
        exts = [ext for factory in editors for ext in factory().extensions]
        if sel and isinstance(sel[0], File) and (sel[0].ext in exts):
            return True
        else:
            return False


    def _visible_default(self):
        """ Trait initialiser """

        sel = self.window.selection

        editors = self.window.application.get_extensions(EDITORS)
        exts = [ext for factory in editors for ext in factory().extensions]
        if sel and isinstance(sel[0], File) and (sel[0].ext in exts):
            return True
        else:
            return False


    def perform(self, event):
        """ Performs the action """

        app = self.window.application
        editors = [factory() for factory in app.get_extensions(EDITORS)]

        selections = self.window.selection
        if selections:
            # Use the first of the selected objects
            selection = selections[0]
            if isinstance(selection, File):
                valid_editors = [
                    e for e in editors if selection.ext in e.extensions
                ]
                if valid_editors:
                    for editor in valid_editors:
                        if editor.default:
                            break
                    else:
                        editor = valid_editors[0]
                    default_editor = app.import_symbol(editor.editor_class)
                    self.window.edit(selection, default_editor)
                else:
                    # FIXME: Show info dialog?
                    pass

# EOF -------------------------------------------------------------------------
