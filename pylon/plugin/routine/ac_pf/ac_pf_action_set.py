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

""" An action set for the AC Power Flow plug-in """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.envisage.ui.action.api import Action, Group, Menu, ToolBar

from enthought.envisage.ui.workbench.api import WorkbenchActionSet

#------------------------------------------------------------------------------
#  "ACPFActionSet" class:
#------------------------------------------------------------------------------

class ACPFActionSet(WorkbenchActionSet):
    """ An action set for the AC Power Flow routine """

    #--------------------------------------------------------------------------
    #  "ActionSet" interface:
    #--------------------------------------------------------------------------

    # The action set"s globally unique identifier.
    id = "pylon.plugin.routine.ac_pf.action_set"

    menus = [
        Menu(
            name="&Run", path="MenuBar", before="Help",
            groups=["ShortcutGroup", "RunAsGroup"]
        ),
        Menu(
            name="&Run As", path="Workspace", group="SubMenuGroup",
            groups=["RoutineGroup"]
        )
    ]

    tool_bars = [
        ToolBar(
            id="pylon.plugin.pylon_action_set.pylon_tool_bar",
            name="Routine", groups=["RunGroup"],
            after="enthought.plugins.workspace.workspace_tool_bar"
        )
    ]

    actions = [
        Action(
            path="MenuBar/Run", group="RunAsGroup",
            class_name="pylon.plugin.routine.ac_pf.ac_pf_action:ACPFAction"
        ),
#        Action(
#            path="ToolBar/Routine",
#            class_name="pylon.plugin.routine.ac_pf.ac_pf_action:ACPFAction"
#        )
        Action(
            path="Workspace/Run As", group="RoutineGroup",
            class_name="pylon.plugin.routine.ac_pf.ac_pf_action:ACPFAction"
        )
    ]

    #--------------------------------------------------------------------------
    #  "WorkbenchActionSet" interface:
    #--------------------------------------------------------------------------

    # The Ids of the perspectives that the action set is enabled in.
#    visible_for_perspectives = ["Pylon"]

# EOF -------------------------------------------------------------------------
