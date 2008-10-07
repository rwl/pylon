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

""" Defines an action for deleting resources from the workspace """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import dirname

from enthought.io.api import File
from enthought.traits.api import Bool, Instance
from enthought.pyface.api import ImageResource, confirm, YES
from enthought.pyface.action.api import Action
from enthought.envisage.ui.workbench.workbench_window import WorkbenchWindow

import enthought.plugins.workspace.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = dirname(enthought.plugins.workspace.api.__file__)

WORKSPACE_VIEW = "enthought.plugins.workspace.workspace_view"

#------------------------------------------------------------------------------
#  "DeleteAction" class:
#------------------------------------------------------------------------------

class DeleteAction(Action):
    """ Defines an action for deleting resources from the workspace """

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    # A longer description of the action:
    description = "Delete the selected resource"

    # The action"s name (displayed on menus/tool bar tools etc):
    name = "&Delete"

    # A short description of the action used for tooltip text etc:
    tooltip = "Delete resource"

    # Keyboard accelerator:
    accelerator = "Delete"

    # The action's image (displayed on tool bar tools etc):
    image = ImageResource("delete", search_path=[IMAGE_LOCATION])

    #--------------------------------------------------------------------------
    #  "CloseAction" interface:
    #--------------------------------------------------------------------------

    window = Instance(WorkbenchWindow)

    #--------------------------------------------------------------------------
    #  "DeleteAction" interface:
    #--------------------------------------------------------------------------

    def _selection_changed_for_window(self, selections):
        """ Enables the action if the window has editors """

        self.enabled = self._is_enabled(selections)


    def _enabled_default(self):
        """ Trait initialiser """

        selections = self.window.selection

        return self._is_enabled(selections)


    def _is_enabled(self, selections):
        """ Returns true if the action should be enabled """

        if selections and isinstance(selections[0], File):
            return True
        else:
            return False

    #--------------------------------------------------------------------------
    #  "Action" interface:
    #--------------------------------------------------------------------------

    def perform(self, event):
        """ Perform the action """

        selection = self.window.selection[0]

        retval = confirm(
            self.window.control, title="Delete Resources",
            message="Are you sure you want to delete '%s' from\n"
            "the file system" % (selection.name+selection.ext)
        )

        if retval == YES:
            selection.delete()

            # Close any editors of the deleted resource
            for editor in self.window.editors[:]:
                if editor.obj is selection:
                    self.window.close_editor(editor)

            # Refresh the workspace tree view
            view = self.window.get_view_by_id(WORKSPACE_VIEW)
            if view is not None:
                from enthought.plugins.workspace.i_workspace import IWorkspace
                workspace = self.window.application.get_service(IWorkspace)
                # Refresh the parent directory and not the whole tree
                view.tree_viewer.refresh(workspace)

# EOF -------------------------------------------------------------------------
