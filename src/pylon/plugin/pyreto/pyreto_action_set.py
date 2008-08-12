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

""" Defines action sets for the Pyreto plug-in """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.envisage.ui.action.api import Action, Group, Menu, ToolBar

from enthought.envisage.ui.workbench.api import WorkbenchActionSet

#------------------------------------------------------------------------------
#  "PyretoWorkbenchActionSet" class:
#------------------------------------------------------------------------------

class PyretoWorkbenchActionSet(WorkbenchActionSet):
    """ An action set for the Pyreto plug-in """

    #--------------------------------------------------------------------------
    #  "ActionSet" interface:
    #--------------------------------------------------------------------------

    # The action set"s globally unique identifier.
    id = "pylon.plugin.pyreto.workbench_action_set"

    # The menus in this set
    menus = [
        Menu(
            name="&New", path="MenuBar/File", group="OpenGroup",
            groups=["ContainerGroup", "ComponentGroup", "OtherGroup"]
        ),
    ]

    # The actions in this set
    actions = [
        Action(
            path="MenuBar/File/New", group="ComponentGroup",
            class_name="pylon.plugin.pyreto.pyreto_action:NewSwarmAction"
        )
    ]

#------------------------------------------------------------------------------
#  "PyretoWorkspaceActionSet" class:
#------------------------------------------------------------------------------

class PyretoWorkspaceActionSet(WorkbenchActionSet):
    """ Actions contributed to the Workspace plug-in """

    #--------------------------------------------------------------------------
    #  "ActionSet" interface:
    #--------------------------------------------------------------------------

    # The action set"s globally unique identifier.
    id = "pylon.plugin.pyreto.workspace_action_set"

    # The actions in this set
    actions = [
        Action(
            path="Workspace/New", group="ComponentGroup",
            class_name="pylon.plugin.pyreto.pyreto_action:NewSwarmAction"
        )
    ]

# EOF -------------------------------------------------------------------------
