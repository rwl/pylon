# Copyright (C) 2011 Richard Lincoln
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from os.path import join, dirname

from enthought.pyface.image_resource import ImageResource

from enthought.traits.ui.menu import MenuBar, ToolBar, Menu, Action

import pylon.case

ICON_LOCATION = join(dirname(pylon.case.__file__), "images")

## File actions

new_action = Action(
    name="&New",
    accelerator="Ctrl+N",
    action="on_new",
    image=ImageResource("new.png", search_path=[ICON_LOCATION]),
    tooltip="New (Ctrl+N)"
)

open_action = Action(
    name="&Open",
    accelerator="Ctrl+O",
    action="on_open",
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

saveas_action = Action(
    name="&Save As...",
    accelerator="Ctrl+Shift+S",
    action="save",
    image=ImageResource("save_as.png", search_path=[ICON_LOCATION]),
    tooltip="Save As (Ctrl+Shift+S)"
)

# The standard "revert all changes" action
RevertAction = Action(
    name="Revert",
    action="_on_revert",
    defined_when="ui.history is not None",
    enabled_when="ui.history.can_undo"
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
    saveas_action,
    RevertAction,
    "_",
    CloseAction,
    name="&File"
)

## Edit actions

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
    action="on_preferences",
    image=ImageResource("preferences.png", search_path=[ICON_LOCATION]),
    tooltip="Preferences"
)

## View actions

tree_action = Action(
    name="Show Tree",
    accelerator="F1",
    action="toggle_tree",
    image=ImageResource("tree.png", search_path=[ICON_LOCATION]),
    tooltip="Tree view (F1)"
)

graph_action = Action(
    name="Show Graph",
    accelerator="F2",
    action="show_graph",
    image=ImageResource("graph.png", search_path=[ICON_LOCATION]),
    tooltip="Show Graph (F2)"
)

map_action = Action(
    name="Show Map",
    accelerator="F3",
    action="show_map",
    image=ImageResource("map.png", search_path=[ICON_LOCATION]),
    tooltip="Show Map (F3)"
)

view_menu = Menu(
    "|",
    tree_action,
    "_",
    graph_action,
    map_action,
    name="&View"
)

## Run menu

dcopf_action = Action(
    name="DC &OPF",
    accelerator="F12",
    action="dcopf",
    image=ImageResource("blank.png", search_path=[ICON_LOCATION]),
    tooltip="Run DC OPF (F12)"
)

## Help actions

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

## Menubar

menubar = MenuBar(
    file_menu,
    Menu("|", UndoAction, RedoAction, "_", preferences_action, name="&Edit"),
    view_menu,
    Menu("|", dcopf_action, name="&Run"),
#    Menu(dot_action, name="&Graph"),
    Menu("|", HelpAction, "_", about_action, name="&Help"),
)

## Toolbar

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
    show_tool_names=False,
#    show_divider=False
)
