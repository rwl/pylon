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

""" Resource plug-in action set """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.envisage.ui.action.api import Action, Group, Menu, ToolBar

from enthought.envisage.ui.workbench.api import WorkbenchActionSet

#------------------------------------------------------------------------------
#  "ResourceActionSet" class:
#------------------------------------------------------------------------------

class ResourceActionSet(WorkbenchActionSet):
    """ Resource plug-in action set """

    #--------------------------------------------------------------------------
    #  "ActionSet" interface:
    #--------------------------------------------------------------------------

    # The action set"s globally unique identifier:
    id = "pylon.plugin.resource.action_set"

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
            id="pylon.plugin.resource.resource_tool_bar",
            name="ResourceToolBar",
            groups=["FileGroup", "ImportGroup", "NavigationGroup"]
        )
    ]

    actions = [
        Action(
            path="MenuBar/File/New", group="OtherGroup",
            class_name="pylon.plugin.resource.action.new_resource_action:"
            "NewResourceAction"
        ),
        Action(
            path="MenuBar/File/New", group="ContainerGroup",
            class_name="pylon.plugin.resource.action.new_folder_action:"
            "NewFolderAction"
        ),
        Action(
            path="MenuBar/File", group="CloseGroup",
            class_name="pylon.plugin.resource.action.close_action:"
            "CloseAction"
        ),
        Action(
            path="MenuBar/File", group="CloseGroup",
            class_name="pylon.plugin.resource.action.close_all_action:"
            "CloseAllAction"
        ),
        Action(
            path="MenuBar/File", group="SaveGroup",
            class_name="pylon.plugin.resource.action.save_action:"
            "SaveAction"
        ),
        Action(
            path="MenuBar/File", group="SaveGroup",
            class_name="pylon.plugin.resource.action.save_as_action:"
            "SaveAsAction"
        ),
        Action(
            path="MenuBar/File", group="SaveGroup",
            class_name="pylon.plugin.resource.action.save_all_action:"
            "SaveAllAction"
        ),
        Action(
            path="MenuBar/File", group="ImportGroup",
            class_name="pylon.plugin.resource.action.import_action:"
            "ImportAction"
        ),
        Action(
            path="MenuBar/File", group="ImportGroup",
            class_name="pylon.plugin.resource.action.export_action:"
            "ExportAction"
        ),
        Action(
            path="MenuBar/File", group="ResourceGroup",
            class_name="pylon.plugin.resource.action.refresh_action:"
            "RefreshAction"
        ),
        Action(
            path="MenuBar/File", group="ResourceGroup",
            class_name="pylon.plugin.resource.action.properties_action:"
            "PropertiesAction"
        ),
        Action(
            path="MenuBar/Edit", group="ClipboardGroup",
            class_name="pylon.plugin.resource.action.copy_action:"
            "CopyAction"
        ),
        Action(
            path="MenuBar/Edit", group="ClipboardGroup",
            class_name="pylon.plugin.resource.action.delete_action:"
            "DeleteAction"
        ),
        Action(
            path="MenuBar/Edit", group="ClipboardGroup",
            class_name="pylon.plugin.resource.action.move_action:"
            "MoveAction"
        ),
        Action(
            path="MenuBar/Edit", group="ClipboardGroup",
            class_name="pylon.plugin.resource.action.rename_action:"
            "RenameAction"
        ),
        Action(
            path="MenuBar/Navigate",
            class_name="pylon.plugin.resource.action.up_action:"
            "UpAction"
        ),
        Action(
            path="MenuBar/Navigate",
            class_name="pylon.plugin.resource.action.home_action:"
            "HomeAction"
        ),
        Action(
            path="MenuBar/Navigate",
            class_name="pylon.plugin.resource.action.location_action:"
            "LocationAction"
        ),
        # Toolbar actions
        Action(
            path="ToolBar/ResourceToolBar", group="FileGroup",
            class_name="pylon.plugin.resource.action.new_resource_action:"
            "NewResourceAction"
        ),
        Action(
            path="ToolBar/ResourceToolBar", group="FileGroup",
            class_name="pylon.plugin.resource.action.save_action:"
            "SaveAction"
        ),
        Action(
            path="ToolBar/ResourceToolBar", group="FileGroup",
            class_name="pylon.plugin.resource.action.save_all_action:"
            "SaveAllAction"
        ),
        Action(
            path="ToolBar/ResourceToolBar", group="ImportGroup",
            class_name="pylon.plugin.resource.action.import_action:"
            "ImportAction"
        ),
        Action(
            path="ToolBar/ResourceToolBar", group="ImportGroup",
            class_name="pylon.plugin.resource.action.export_action:"
            "ExportAction"
        ),
        Action(
            path="ToolBar/ResourceToolBar", group="NavigationGroup",
            class_name="pylon.plugin.resource.action.up_action:"
            "UpAction"
        ),
        Action(
            path="ToolBar/ResourceToolBar", group="NavigationGroup",
            class_name="pylon.plugin.resource.action.home_action:"
            "HomeAction"
        )
    ]

#------------------------------------------------------------------------------
#  "ContextMenuActionSet" class:
#------------------------------------------------------------------------------

class ContextMenuActionSet(WorkbenchActionSet):
    """ Action set for the resource view context menu """

    #--------------------------------------------------------------------------
    #  "ActionSet" interface:
    #--------------------------------------------------------------------------

    # The action set"s globally unique identifier:
    id = "pylon.plugin.resource.context_menu_action_set"

    # The menus in this set
    menus = [
        Menu(
            name="&New", path="Resource", group="NewGroup",
            groups=["ContainerGroup", "ComponentGroup", "OtherGroup"]
        ),
        Menu(
            name="Open With", path="Resource", group="OpenGroup",
            class_name="pylon.plugin.resource.action.open_with_menu_manager:"
            "OpenWithMenuManager"
        )
    ]

    # The groups in this set
    groups = [
        Group(path="Resource", id="NewGroup"),
        Group(path="Resource", id="OpenGroup"),
        Group(path="Resource", id="EditGroup"),
        Group(path="Resource", id="ImportGroup"),
        Group(path="Resource", id="RefreshGroup"),
        Group(path="Resource", id="SubMenuGroup"),
        Group(path="Resource", id="PropertiesGroup")
    ]

    # The actions in this set
    actions = [
        Action(
            name="Folder", path="Resource/New", group="ContainerGroup",
            id="pylon.plugin.resource.new_project_action",
            class_name="pylon.plugin.resource.action.new_folder_action:"
            "NewFolderAction"
        ),
        Action(
            path="Resource/New", group="OtherGroup",
            class_name="pylon.plugin.resource.action.new_resource_action:"
            "NewResourceAction"
        ),
        Action(
            name="Open", path="Resource",
            group="OpenGroup", before="Open With",
            id="pylon.plugin.resource.open_action",
            class_name="pylon.plugin.resource.action.open_action:"
            "OpenAction"
        ),
        Action(
            name="&Copy...", path="Resource", group="EditGroup",
            class_name="pylon.plugin.resource.action.copy_action:"
            "CopyAction"
        ),
        Action(
            name="&Delete", path="Resource", group="EditGroup",
            class_name="pylon.plugin.resource.action.delete_action:"
            "DeleteAction"
        ),
        Action(
            name="Mo&ve...", path="Resource", group="EditGroup",
            class_name="pylon.plugin.resource.action.move_action:"
            "MoveAction"
        ),
        Action(
            name="Rena&me...", path="Resource", group="EditGroup",
            class_name="pylon.plugin.resource.action.rename_action:"
            "RenameAction"
        ),
        Action(
            name="Import...", path="Resource", group="ImportGroup",
            class_name="pylon.plugin.resource.action.import_action:"
            "ImportAction"
        ),
        Action(
            name="Export...", path="Resource", group="ImportGroup",
            class_name="pylon.plugin.resource.action.export_action:"
            "ExportAction"
        ),
        Action(
            name="Refresh", path="Resource", group="RefreshGroup",
            class_name="pylon.plugin.resource.action.refresh_action:"
            "RefreshAction"
        ),
        Action(
            name="Properties", path="Resource", group="PropertiesGroup",
            class_name="pylon.plugin.resource.action.properties_action:"
            "PropertiesAction"
        )
    ]

    # A mapping from human-readable names to globally unique IDs
#    aliases = {"Resource": "pylon.plugin.resource.context_menu"}

# EOF -------------------------------------------------------------------------
