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

"""
Controllers for network view model.

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname

from enthought.pyface.image_resource import ImageResource

from enthought.traits.ui.menu import MenuBar, ToolBar, Menu, Action

import pylon.ui.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

ICON_LOCATION = join(dirname(pylon.ui.api.__file__), "images")

#------------------------------------------------------------------------------
#  File actions:
#------------------------------------------------------------------------------

new_action = Action(
    name="&New",
    accelerator="Ctrl+N",
    action="new",
    image=ImageResource("new.png", search_path=[ICON_LOCATION]),
    tooltip="New (Ctrl+N)"
)

open_action = Action(
    name="&Open",
    accelerator="Ctrl+O",
    action="open",
    image=ImageResource("open.png", search_path=[ICON_LOCATION]),
    tooltip="Open (Ctrl+O)"
)

save_action = Action(
    name="&Save",
    accelerator="Ctrl+S",
    action="save",
    image=ImageResource("save.png", search_path=[ICON_LOCATION]),
    tooltip="Save (Ctrl+S)"
)

# The standard "revert all changes" action
RevertAction = Action(
    name="Revert",
    action="_on_revert",
    defined_when="ui.history is not None",
    enabled_when="ui.history.can_undo"
)

matpower_action = Action(
    name="&MATPOWER",
    action="matpower",
    image=ImageResource("matpower.png", search_path=[ICON_LOCATION]),
    tooltip="Import MATPOWER data file"
)

psse_action = Action(
    name="&PSS/E",
    action="psse",
    image=ImageResource("psse.png", search_path=[ICON_LOCATION]),
    tooltip="Import PTI PSS/E data file"
)

psat_action = Action(
    name="P&SAT",
    action="psat",
    image=ImageResource("psat.png", search_path=[ICON_LOCATION]),
    tooltip="Import PSAT data file"
)

export_graph_action = Action(
    name="&Graph",
    action="export_graph",
    image=ImageResource("dot.png", search_path=[ICON_LOCATION]),
    tooltip="Export graph"
)

# The standard "close window" action
CloseAction = Action(
    name="E&xit",
    accelerator="Alt+X",
    action="_on_close",
    image=ImageResource("exit.png", search_path=[ICON_LOCATION]),
    tooltip="Exit (Alt+X)"
)

file_menu = Menu(
    "|", # Hack suggested by Brennan Williams to achieve correct ordering
    new_action,
    "_",
    open_action,
    save_action,
    RevertAction,
    "_",
    Menu(psat_action, matpower_action, psse_action, name="&Import"),
    Menu(export_graph_action, name="&Export"),
    "_",
    CloseAction,
    name="&File"
)

#------------------------------------------------------------------------------
#  Edit actions:
#------------------------------------------------------------------------------

# The standard "undo last change" action
UndoAction = Action(
    name="Undo",
    action="_on_undo",
    defined_when="ui.history is not None",
    enabled_when="ui.history.can_undo",
    accelerator="Ctrl+Z",
    image=ImageResource("undo.png", search_path=[ICON_LOCATION]),
    tooltip="Undo (Ctrl+Z)"
)

# The standard "redo last undo" action
RedoAction = Action(
    name="Redo",
    action="_on_redo",
    defined_when="ui.history is not None",
    enabled_when="ui.history.can_redo",
    accelerator="Ctrl+Y",
    image=ImageResource("redo.png", search_path=[ICON_LOCATION]),
    tooltip="Redo (Ctrl+Y)"
)

preferences_action = Action(
    name="&Preferences...",
#    accelerator="Ctrl+E",
    action="preferences",
    image=ImageResource("preferences.png", search_path=[ICON_LOCATION]),
    tooltip="Preferences"
)

#------------------------------------------------------------------------------
#  View actions:
#------------------------------------------------------------------------------

tree_action = Action(
    name="Tree",
    accelerator="F1",
    action="toggle_tree",
    image=ImageResource("tree.png", search_path=[ICON_LOCATION]),
    tooltip="Tree view (F1)"
)

buses_action = Action(
    name="B&us Table",
    accelerator="F2",
    action="show_buses",
    image=ImageResource("bus_table.png", search_path=[ICON_LOCATION]),
    tooltip="Bus Table (F2)"
)

branches_action = Action(
    name="B&ranch Table",
    accelerator="F3",
    action="show_branches",
    image=ImageResource("branch_table.png", search_path=[ICON_LOCATION]),
    tooltip="Branch Table (F3)"
)

fast_draw_action = Action(
    name="&Fast Draw",
    accelerator="F4",
    action="draw_fast",
    style="toggle",
    image=ImageResource("graph.png", search_path=[ICON_LOCATION]),
    tooltip="Disables/Enables interactive graph (F4)"
)

bus_plot_action = Action(
    name="Bu&s Plot",
    accelerator="F5",
    action="bus_plot",
    image=ImageResource("bus_plot.png", search_path=[ICON_LOCATION]),
    tooltip="Bus Plot (F5)"
)

branch_plot_action = Action(
    name="Br&anch Plot",
    accelerator="F6",
    action="branch_plot",
    image=ImageResource("branch_plot.png", search_path=[ICON_LOCATION]),
    tooltip="Branch Plot (F6)"
)

view_menu = Menu(
    "|",
    tree_action,
    buses_action,
    branches_action,
    "_",
    fast_draw_action,
    "_",
    bus_plot_action,
    branch_plot_action,
    name="&View"
)

#------------------------------------------------------------------------------
#  Network actions:
#------------------------------------------------------------------------------

bus_action = Action(
    name="B&us",
    accelerator="Ctrl+B",
    action="add_bus",
    image=ImageResource("add.png", search_path=[ICON_LOCATION]),
    tooltip="Bus (Ctrl+B)"
)

branch_action = Action(
    name="B&ranch",
    accelerator="Ctrl+R",
    action="add_branch",
    image=ImageResource("add2.png", search_path=[ICON_LOCATION]),
    tooltip="Branch (Ctrl+R)"
)

dcopf_action = Action(
    name="DC &OPF",
    accelerator="F12",
    action="dcopf",
    image=ImageResource("blank.png", search_path=[ICON_LOCATION]),
    tooltip="Run DC OPF (F12)"
)

#------------------------------------------------------------------------------
#  Graph actions:
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
#  Help actions:
#------------------------------------------------------------------------------

# The standard "show help" action
HelpAction = Action(
    name="Help",
    action="show_help",
    image=ImageResource("help.png", search_path=[ICON_LOCATION]),
    tooltip="Help"
)

about_action = Action(
    name="About Pylon",
    action="about",
    image=ImageResource("about.png", search_path=[ICON_LOCATION]),
    tooltip="About Pylon"
)

#------------------------------------------------------------------------------
#  Pylon "MenuBar" instance:
#------------------------------------------------------------------------------

menubar = MenuBar(
    file_menu,
    Menu("|", UndoAction, RedoAction, "_", preferences_action, name="&Edit"),
    view_menu,
    Menu("|", dcopf_action, "_", bus_action, branch_action, name="&Network"),
#    Menu(dot_action, name="&Graph"),
    Menu("|", HelpAction, "_", about_action, name="&Help"),
)

#------------------------------------------------------------------------------
#  Pylon "ToolBar" instance:
#------------------------------------------------------------------------------

toolbar = ToolBar(
    "|", # Hack suggested by Brennan Williams to achieve correct ordering
    CloseAction,
    "_",
    new_action,
    open_action,
    save_action,
    "_",
    UndoAction,
    RedoAction,
    "_",
    fast_draw_action,
    "_",
    bus_action,
    branch_action,
    buses_action,
    branches_action,
    bus_plot_action,
    branch_plot_action,
    show_tool_names=False,
#    show_divider=False
)

# EOF -------------------------------------------------------------------------
