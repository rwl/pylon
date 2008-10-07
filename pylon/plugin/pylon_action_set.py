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

""" Action sets for the Pylon plug-in """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.envisage.ui.action.api import Action, Group, Menu, ToolBar

from enthought.envisage.ui.workbench.api import WorkbenchActionSet

#------------------------------------------------------------------------------
#  "PylonWorkbenchActionSet" class:
#------------------------------------------------------------------------------

class PylonWorkbenchActionSet(WorkbenchActionSet):
    """ A set of workbench related actions for the Pylon plug-in """

    #--------------------------------------------------------------------------
    #  "ActionSet" interface:
    #--------------------------------------------------------------------------

    # The action set"s globally unique identifier.
    id = "pylon.plugin.workbench_action_set"

    menus = [
        Menu(
            name="&New", path="MenuBar/File", group="OpenGroup",
            groups=["ContainerGroup", "ComponentGroup", "OtherGroup"]
        ),
    ]

    actions = [
        Action(
            path="MenuBar/File/New", group="ComponentGroup",
            class_name="pylon.plugin.pylon_action:NewNetworkAction"
        )
    ]

#------------------------------------------------------------------------------
#  "PylonWorkspaceActionSet" class:
#------------------------------------------------------------------------------

class PylonWorkspaceActionSet(WorkbenchActionSet):
    """ Defines a set of actions for use with the workspace plug-in """

    #--------------------------------------------------------------------------
    #  "ActionSet" interface:
    #--------------------------------------------------------------------------

    # The action set"s globally unique identifier.
    id = "pylon.plugin.workspace_action_set"

    # The actions in this set
    actions = [
        Action(
            path="Workspace/New", group="ComponentGroup",
            class_name="pylon.plugin.pylon_action:NewNetworkAction"
        )
    ]

# EOF -------------------------------------------------------------------------
