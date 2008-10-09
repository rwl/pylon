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
#  Date:   14/06/2008
#
#------------------------------------------------------------------------------

""" An action for opening a Python script from the file system """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import exists

from enthought.io.api import File
from enthought.pyface.api import ImageResource, FileDialog, CANCEL
from enthought.pyface.action.api import Action

from enthought.plugins.workspace.action.open_action import OpenAction

#from python_workbench_editor import PythonWorkbenchEditor

#------------------------------------------------------------------------------
#  "OpenFileAction" class:
#------------------------------------------------------------------------------

class OpenFileAction(Action):
    """ An action for opening a Python script from the file system """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Open a file on the file system"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "Open File&..."

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def perform(self, event):
        """ Perform the action. """

        dialog = FileDialog(
            parent = self.window.control,
            title="Open File",
            action = "open",
#            default_directory="/tmp",
            wildcard = FileDialog.WILDCARD_PY
        )
        if dialog.open() != CANCEL:
            file = File(dialog.path)
#            self.window.edit(file, PythonWorkbenchEditor)

            self.window.selection = [file]
            OpenAction(window=self.window).perform(event=None)

        return

# EOF -------------------------------------------------------------------------
