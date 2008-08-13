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

""" An action for creating a new Python script """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import exists

from enthought.io.api import File
from enthought.pyface.api import ImageResource, FileDialog, CANCEL
from enthought.pyface.action.api import Action

from enthought.plugins.workspace.action.open_action import OpenAction

#from python_workbench_editor import PythonWorkbenchEditor
from enthought.plugins.text_editor.editor.text_editor import TextEditor

#------------------------------------------------------------------------------
#  "NewFileAction" class:
#------------------------------------------------------------------------------

class NewFileAction(Action):
    """ An action for creating a new Python script """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Create a new file"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "File"

    # A short description of the action used for tooltip text etc:
    tooltip = "Create a File"

    # The action's image (displayed on tool bar tools etc):
    image = ImageResource("new")

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def perform(self, event):
        """ Perform the action. """

        file = File("")
        self.window.edit(file, TextEditor)

#        self.window.selection = [file]
#        OpenAction(window=self.window).perform(event=None)

        return

# EOF -------------------------------------------------------------------------
