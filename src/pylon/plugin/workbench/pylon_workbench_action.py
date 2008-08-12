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

""" Custom workbench actions for Pylon """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname

from enthought.traits.api import Instance, Bool

from enthought.pyface.api import ImageResource

from enthought.pyface.action.api import Action

from enthought.envisage.ui.workbench.action.api import \
    ExitAction, EditPreferencesAction, AboutAction

from enthought.envisage.ui.workbench.workbench_window import WorkbenchWindow

import pylon.ui.api

#------------------------------------------------------------------------------
#  "NewWindowAction" class:
#------------------------------------------------------------------------------

class NewWindowAction(Action):
    """ An action that opens a new workbench window """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action.
    description = "Open a new workbench window"

    # The action"s image (displayed on tool bar tools etc).
#    image = ImageResource("window")

    # The action"s name (displayed on menus/tool bar tools etc).
    name = "&New Window"

    # A short description of the action used for tooltip text etc.
    tooltip = "New workbench window"

    #--------------------------------------------------------------------------
    #  "NewWindowAction" interface:
    #--------------------------------------------------------------------------

    window = Instance(WorkbenchWindow)

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def perform(self, event):
        """ Perform the action """

        window = self.window.workbench.create_window(
            position=self.window.application.window_position,
            size=self.window.application.window_size
        )
        window.open()

#------------------------------------------------------------------------------
#  "NewEditorAction" class:
#------------------------------------------------------------------------------

class NewEditorAction(Action):
    """ An action that opens a new workbench window """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action.
    description = "Open a new editor"

    # The action"s image (displayed on tool bar tools etc).
#    image = ImageResource("window", search_path=[IMAGE_PATH])

    # The action"s name (displayed on menus/tool bar tools etc).
    name = "New &Editor"

    # A short description of the action used for tooltip text etc.
    tooltip = "New editor"

    # Is the action enabled?
    enabled = Bool(False)

    #--------------------------------------------------------------------------
    #  "NewEditorAction" interface:
    #--------------------------------------------------------------------------

    window = Instance(WorkbenchWindow)

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def perform(self, event):
        """ Perform the action """

        editor = self.window.active_editor

        if editor is not None:
            self.window.edit(editor.obj, type(editor), use_existing=False)

    #--------------------------------------------------------------------------
    #  "NewEditorAction" interface:
    #--------------------------------------------------------------------------

    def _active_editor_changed_for_window(self, new):
        """ Enables the action if the window has one or more open editors """

        if new is not None:
            self.enabled = True
        else:
            self.enabled = False

#------------------------------------------------------------------------------
#  "ExitAction" class:
#------------------------------------------------------------------------------

class ExitAction(ExitAction):
    """ An action that exits the workbench. """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action.
    description = "Exit the Pylon application"

    # The action"s image (displayed on tool bar tools etc).
    image = None#ImageResource("exit")

    # The action"s name (displayed on menus/tool bar tools etc).
    name = "E&xit"

    # A short description of the action used for tooltip text etc.
    tooltip = "Exit Pylon"

    # Keyboard accelerator:
    accelerator = "Alt+X"

#------------------------------------------------------------------------------
#  "PreferencesAction" class:
#------------------------------------------------------------------------------

class PreferencesAction(EditPreferencesAction):
    """ An action that displays the preferences dialog. """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # The action"s image (displayed on tool bar tools etc).
    image = None#ImageResource("preferences")

#------------------------------------------------------------------------------
#  "AboutAction" class:
#------------------------------------------------------------------------------

class AboutAction(AboutAction):
    """ An action that shows the "About" dialog. """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action.
    description = "Display information about Pylon"

    # The action"s image (displayed on tool bar tools etc).
    image = ImageResource("about")

    # A short description of the action used for tooltip text etc.
    tooltip = "Display information about Pylon"

#------------------------------------------------------------------------------
#  "UndoAction" class:
#------------------------------------------------------------------------------

class UndoAction(Action):
    """ An action that undoes the active editors last action """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Undo last edit"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "&Undo"

    # A short description of the action used for tooltip text etc:
    tooltip = "Undo (Ctrl+Z)"

    # Keyboard accelerator:
    accelerator = "Ctrl+Z"

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def perform(self, event):
        """ Perform the action. """

        editor = self.window.active_editor

        editor.ui.history.undo()

# EOF -------------------------------------------------------------------------
