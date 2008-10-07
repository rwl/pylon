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

""" Workspace plug-in action set """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.envisage.ui.action.api import Action, Group, Menu, ToolBar

from enthought.envisage.ui.workbench.api import WorkbenchActionSet

#------------------------------------------------------------------------------
#  "WorkspaceActionSet" class:
#------------------------------------------------------------------------------

class WorkspaceActionSet(WorkbenchActionSet):
    """ Workspace plug-in action set """

    #--------------------------------------------------------------------------
    #  "ActionSet" interface:
    #--------------------------------------------------------------------------

    # The action set"s globally unique identifier:
    id = "enthought.plugins.workspace.action_set"

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
            name="&Edit", path="MenuBar", after="File",
            groups=["UndoGroup", "ClipboardGroup", "PreferencesGroup"]
        ),
        Menu(
            name="&Navigate", path="MenuBar", after="Edit"
        )
    ]

    tool_bars = [
        ToolBar(
            id="enthought.plugins.workspace.workspace_tool_bar",
            name="WorkspaceToolBar",
            groups=["FileGroup", "ImportGroup", "NavigationGroup"]
        )
    ]

    actions = [
        Action(
            path="MenuBar/File/New", group="OtherGroup",
            class_name="enthought.plugins.workspace.action.new_resource_action:"
            "NewResourceAction"
        ),
        Action(
            path="MenuBar/File/New", group="ContainerGroup",
            class_name="enthought.plugins.workspace.action.new_folder_action:"
            "NewFolderAction"
        ),
        Action(
            path="MenuBar/File", group="CloseGroup",
            class_name="enthought.plugins.workspace.action.close_action:"
            "CloseAction"
        ),
        Action(
            path="MenuBar/File", group="CloseGroup",
            class_name="enthought.plugins.workspace.action.close_all_action:"
            "CloseAllAction"
        ),
        Action(
            path="MenuBar/File", group="SaveGroup",
            class_name="enthought.plugins.workspace.action.save_action:"
            "SaveAction"
        ),
        Action(
            path="MenuBar/File", group="SaveGroup",
            class_name="enthought.plugins.workspace.action.save_as_action:"
            "SaveAsAction"
        ),
        Action(
            path="MenuBar/File", group="SaveGroup",
            class_name="enthought.plugins.workspace.action.save_all_action:"
            "SaveAllAction"
        ),
        Action(
            path="MenuBar/File", group="ImportGroup",
            class_name="enthought.plugins.workspace.action.import_action:"
            "ImportAction"
        ),
        Action(
            path="MenuBar/File", group="ImportGroup",
            class_name="enthought.plugins.workspace.action.export_action:"
            "ExportAction"
        ),
        Action(
            path="MenuBar/File", group="ResourceGroup",
            class_name="enthought.plugins.workspace.action.refresh_action:"
            "RefreshAction"
        ),
        Action(
            path="MenuBar/File", group="ResourceGroup",
            class_name="enthought.plugins.workspace.action.properties_action:"
            "PropertiesAction"
        ),
        Action(
            path="MenuBar/Edit", group="ClipboardGroup",
            class_name="enthought.plugins.workspace.action.copy_action:"
            "CopyAction"
        ),
        Action(
            path="MenuBar/Edit", group="ClipboardGroup",
            class_name="enthought.plugins.workspace.action.delete_action:"
            "DeleteAction"
        ),
        Action(
            path="MenuBar/Edit", group="ClipboardGroup",
            class_name="enthought.plugins.workspace.action.move_action:"
            "MoveAction"
        ),
        Action(
            path="MenuBar/Edit", group="ClipboardGroup",
            class_name="enthought.plugins.workspace.action.rename_action:"
            "RenameAction"
        ),
        Action(
            path="MenuBar/Navigate",
            class_name="enthought.plugins.workspace.action.up_action:"
            "UpAction"
        ),
        Action(
            path="MenuBar/Navigate",
            class_name="enthought.plugins.workspace.action.home_action:"
            "HomeAction"
        ),
        Action(
            path="MenuBar/Navigate",
            class_name="enthought.plugins.workspace.action.location_action:"
            "LocationAction"
        ),
        # Toolbar actions
        Action(
            path="ToolBar/WorkspaceToolBar", group="FileGroup",
            class_name="enthought.plugins.workspace.action.new_resource_action:"
            "NewResourceAction"
        ),
        Action(
            path="ToolBar/WorkspaceToolBar", group="FileGroup",
            class_name="enthought.plugins.workspace.action.save_action:"
            "SaveAction"
        ),
        Action(
            path="ToolBar/WorkspaceToolBar", group="FileGroup",
            class_name="enthought.plugins.workspace.action.save_all_action:"
            "SaveAllAction"
        ),
        Action(
            path="ToolBar/WorkspaceToolBar", group="ImportGroup",
            class_name="enthought.plugins.workspace.action.import_action:"
            "ImportAction"
        ),
        Action(
            path="ToolBar/WorkspaceToolBar", group="ImportGroup",
            class_name="enthought.plugins.workspace.action.export_action:"
            "ExportAction"
        ),
        Action(
            path="ToolBar/WorkspaceToolBar", group="NavigationGroup",
            class_name="enthought.plugins.workspace.action.up_action:"
            "UpAction"
        ),
        Action(
            path="ToolBar/WorkspaceToolBar", group="NavigationGroup",
            class_name="enthought.plugins.workspace.action.home_action:"
            "HomeAction"
        )
    ]

#------------------------------------------------------------------------------
#  "ContextMenuActionSet" class:
#------------------------------------------------------------------------------

class ContextMenuActionSet(WorkbenchActionSet):
    """ Action set for the workspace view context menu """

    #--------------------------------------------------------------------------
    #  "ActionSet" interface:
    #--------------------------------------------------------------------------

    # The action set"s globally unique identifier:
    id = "enthought.plugins.workspace.context_menu_action_set"

    # The menus in this set
    menus = [
        Menu(
            name="&New", path="Workspace", group="NewGroup",
            groups=["ContainerGroup", "ComponentGroup", "OtherGroup"]
        ),
        Menu(
            name="Open With", path="Workspace", group="OpenGroup",
            class_name="enthought.plugins.workspace.action."
            "open_with_menu_manager:OpenWithMenuManager"
        )
    ]

    # The groups in this set
    groups = [
        Group(path="Workspace", id="NewGroup"),
        Group(path="Workspace", id="OpenGroup"),
        Group(path="Workspace", id="EditGroup"),
        Group(path="Workspace", id="ImportGroup"),
        Group(path="Workspace", id="RefreshGroup"),
        Group(path="Workspace", id="SubMenuGroup"),
        Group(path="Workspace", id="PropertiesGroup")
    ]

    # The actions in this set
    actions = [
        Action(
            name="Folder", path="Workspace/New", group="ContainerGroup",
            id="enthought.plugins.workspace.new_project_action",
            class_name="enthought.plugins.workspace.action.new_folder_action:"
            "NewFolderAction"
        ),
        Action(
            path="Workspace/New", group="OtherGroup",
            class_name="enthought.plugins.workspace.action.new_resource_action:"
            "NewResourceAction"
        ),
        Action(
            name="Open", path="Workspace",
            group="OpenGroup", before="Open With",
            id="enthought.plugins.workspace.open_action",
            class_name="enthought.plugins.workspace.action.open_action:"
            "OpenAction"
        ),
        Action(
            name="&Copy...", path="Workspace", group="EditGroup",
            class_name="enthought.plugins.workspace.action.copy_action:"
            "CopyAction"
        ),
        Action(
            name="&Delete", path="Workspace", group="EditGroup",
            class_name="enthought.plugins.workspace.action.delete_action:"
            "DeleteAction"
        ),
        Action(
            name="Mo&ve...", path="Workspace", group="EditGroup",
            class_name="enthought.plugins.workspace.action.move_action:"
            "MoveAction"
        ),
        Action(
            name="Rena&me...", path="Workspace", group="EditGroup",
            class_name="enthought.plugins.workspace.action.rename_action:"
            "RenameAction"
        ),
        Action(
            name="Import...", path="Workspace", group="ImportGroup",
            class_name="enthought.plugins.workspace.action.import_action:"
            "ImportAction"
        ),
        Action(
            name="Export...", path="Workspace", group="ImportGroup",
            class_name="enthought.plugins.workspace.action.export_action:"
            "ExportAction"
        ),
        Action(
            name="Refresh", path="Workspace", group="RefreshGroup",
            class_name="enthought.plugins.workspace.action.refresh_action:"
            "RefreshAction"
        ),
        Action(
            name="Properties", path="Workspace", group="PropertiesGroup",
            class_name="enthought.plugins.workspace.action.properties_action:"
            "PropertiesAction"
        )
    ]

    # A mapping from human-readable names to globally unique IDs
#    aliases = {"Workspace": "enthought.plugins.workspace.context_menu"}

# EOF -------------------------------------------------------------------------
