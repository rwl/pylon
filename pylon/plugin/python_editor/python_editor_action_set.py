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

"""
An action set for the Python editor plug-in

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.envisage.ui.action.api import Action, Group, Menu, ToolBar

from enthought.envisage.ui.workbench.api import WorkbenchActionSet

from python_workbench_editor import PythonWorkbenchEditor

#------------------------------------------------------------------------------
#  "PythonEditorActionSet" class:
#------------------------------------------------------------------------------

class PythonEditorActionSet(WorkbenchActionSet):
    """ An action set for the Python editor plug-in """

    #--------------------------------------------------------------------------
    #  "ActionSet" interface:
    #--------------------------------------------------------------------------

    # The action set"s globally unique identifier:
    id = "enthought.plugins.python_editor.action_set"

    menus = [
        Menu(
            name="&File", path="MenuBar",
            groups=[
                "OpenGroup", "CloseGroup", "SaveGroup",
                "ImportGroup", "ResourceGroup", "ExitGroup"
            ]
        ),
        Menu(
            name="&New", path="MenuBar/File", group="OpenGroup",
            groups=["ContainerGroup", "ComponentGroup", "OtherGroup"]
        ),
        Menu(
            name="&Run", path="MenuBar", after="Edit",
            groups=["ShortcutGroup", "RunAsGroup"]
        ),
        Menu(
            name="&Run As", path="Workspace", group="SubMenuGroup",
            groups=["RoutineGroup"]
        )
    ]

    actions = [
        Action(
            path="MenuBar/File/New", group="ComponentGroup",
            class_name="enthought.plugins.python_editor.new_file_action:"
            "NewFileAction"
        ),
        Action(
            path="MenuBar/File", group="OpenGroup",
            class_name="enthought.plugins.python_editor.open_file_action:"
            "OpenFileAction"
        ),
        Action(
            name="File", path="Workspace/New", group="ComponentGroup",
            id="enthought.plugins.python_editor.new_file_action",
            class_name="enthought.plugins.python_editor.new_file_action:"
            "NewFileAction"
        ),
        Action(
            path="MenuBar/Run", group="RunAsGroup",
            class_name="enthought.plugins.python_editor.python_run_action:"
            "PythonRunAction"
        ),
        Action(
            path="Workspace/Run As", group="RoutineGroup",
            class_name="enthought.plugins.python_editor.python_run_action:"
            "PythonRunAction"
        )
    ]

# EOF -------------------------------------------------------------------------
