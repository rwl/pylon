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

""" Model view menus and menu items """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import dirname

from enthought.pyface.api import ImageResource

from enthought.traits.ui.menu import MenuBar, ToolBar, Menu, Action

import pylon.ui.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = dirname(pylon.ui.api.__file__)

#------------------------------------------------------------------------------
#  File menu actions:
#------------------------------------------------------------------------------

new_action = Action(
    name="&New", accelerator="Ctrl+N", action="new",
    image=ImageResource("new", search_path=[IMAGE_LOCATION]),
    tooltip="New (Ctrl+N)", enabled_when="False"
)

open_action = Action(
    name="&Open", accelerator="Ctrl+O", action="open",
    image=ImageResource("open", search_path=[IMAGE_LOCATION]),
    tooltip="Open (Ctrl+O)"
)

save_action = Action(
    name="&Save", accelerator="Ctrl+S", action="save",
    image=ImageResource("save", search_path=[IMAGE_LOCATION]),
    tooltip="Save (Ctrl+S)"
)

# The standard "revert all changes" action
revert_action = Action(
    name="Revert", action="_on_revert",
    defined_when="ui.history is not None",
    enabled_when="ui.history.can_undo"
)

# The standard "close window" action
close_action = Action(
    name="E&xit", accelerator="Alt+X", action="_on_close",
    image=ImageResource("exit", search_path=[IMAGE_LOCATION]),
    tooltip="Exit (Alt+X)"
)

#------------------------------------------------------------------------------
#  Edit menu actions:
#------------------------------------------------------------------------------

# The standard "undo last change" action
undo_action = Action(
    name="Undo", action="_on_undo", accelerator="Ctrl+Z",
    defined_when="ui.history is not None",
    enabled_when="ui.history.can_undo",
    image=ImageResource("undo", search_path=[IMAGE_LOCATION]),
    tooltip="Undo (Ctrl+Z)"
)

# The standard "redo last undo" action
redo_action = Action(
    name="Redo", action="_on_redo", accelerator="Ctrl+Y",
    defined_when="ui.history is not None",
    enabled_when="ui.history.can_redo",
    image=ImageResource("redo", search_path=[IMAGE_LOCATION]),
    tooltip="Redo (Ctrl+Y)"
)

preferences_action = Action(
    name="&Preferences...", action="preferences",
    image=ImageResource("preferences", search_path=[IMAGE_LOCATION]),
    tooltip="Preferences"
)

#------------------------------------------------------------------------------
#  Circuit actions:
#------------------------------------------------------------------------------

bus_action = Action(name="&Bus", action="new_bus")
line_action = Action(name="&Line", action="new_line")
transformer_action = Action(name="&Transformer", action="new_transformer")
generator_action = Action(name="&Generator", action="new_generator")
load_action = Action(name="&Load", action="new_load")

voltage_source_action = Action(
    name="&Voltage Source", action="new_voltage_source"
)

current_source_action = Action(
    name="&Current Source", action="new_current source"
)

fault_action = Action(name="&Fault", action="new_fault")
capacitor_action = Action(name="C&apacitor", action="new_capacitor")

capacitor_control_action = Action(
    name="Ca&pacitor Control", action="new_capacitor_control"
)

regulator_control_action = Action(
    name="&Regulator Control", action="new_regulator_control"
)

#------------------------------------------------------------------------------
#  Help actions:
#------------------------------------------------------------------------------

# The standard "show help" action
help_action = Action(
    name="Help", action="show_help",
    image=ImageResource("help", search_path=[IMAGE_LOCATION])
)

about_action = Action(
    name="About", action="about",
    image=ImageResource("about", search_path=[IMAGE_LOCATION])
)

#------------------------------------------------------------------------------
#  Menus and menu bar:
#------------------------------------------------------------------------------

file_menu = Menu(
    "|", new_action, "_", open_action, save_action, revert_action, "_",
    close_action, name="&File"
)

edit_menu = Menu(
    "|", undo_action, redo_action, "_", preferences_action, name="&Edit"
)

circuit_menu = Menu(
    "|", bus_action, line_action, transformer_action, generator_action,
    load_action, voltage_source_action, current_source_action, fault_action,
    capacitor_action, capacitor_control_action, regulator_control_action,
    name="&Circuit"
)

help_menu = Menu(about_action, name="&Help")

menu_bar = MenuBar(file_menu, edit_menu, circuit_menu, help_menu)

#------------------------------------------------------------------------------
#  Tool bar:
#------------------------------------------------------------------------------

tool_bar = ToolBar(
    "|", #close_action, "_",
    new_action, open_action, save_action, "_",
    undo_action, redo_action,
    show_tool_names=False,
)

# EOF -------------------------------------------------------------------------
