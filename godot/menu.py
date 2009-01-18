#------------------------------------------------------------------------------
#  Copyright (c) 2008 Richard W. Lincoln
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#  IN THE SOFTWARE.
#------------------------------------------------------------------------------

""" Model view menus, menu items and toolbars. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname

from enthought.pyface.api import ImageResource
from enthought.traits.ui.menu import MenuBar, ToolBar, Menu, Action

#------------------------------------------------------------------------------
#  File actions:
#------------------------------------------------------------------------------

new_action = Action(name="&New", accelerator="Ctrl+N", action="new_model",
    image=ImageResource("new"), tooltip="New (Ctrl+N)")

open_action = Action(name="&Open", accelerator="Ctrl+O", action="open_file",
    image=ImageResource("open"), tooltip="Open (Ctrl+O)")

save_action = Action(name="&Save", accelerator="Ctrl+S", action="save",
    image=ImageResource("save"), tooltip="Save (Ctrl+S)")

# Action to revert all changes.
revert_action = Action(name="Revert", action="_on_revert",
    defined_when="ui.history is not None", enabled_when="ui.history.can_undo")

# Action to close the view window.
close_action = Action(name="E&xit", accelerator="Alt+X", action="_on_close",
    image=ImageResource("exit"), tooltip="Exit (Alt+X)")

#------------------------------------------------------------------------------
#  Edit actions:
#------------------------------------------------------------------------------

# Action to undo last change.
undo_action = Action(name="Undo", action="_on_undo", accelerator="Ctrl+Z",
    defined_when="ui.history is not None", enabled_when="ui.history.can_undo",
    image=ImageResource("undo"), tooltip="Undo (Ctrl+Z)")

# Action to redo last undo.
redo_action = Action(name="Redo", action="_on_redo", accelerator="Ctrl+Y",
    defined_when="ui.history is not None", enabled_when="ui.history.can_redo",
    image=ImageResource("redo.png"), tooltip="Redo (Ctrl+Y)")

#------------------------------------------------------------------------------
#  View actions:
#------------------------------------------------------------------------------

configure_graph_action = Action(name="&Graph Attributes", accelerator="Ctrl+G",
    action="configure_graph", image=ImageResource("table"),
    tooltip="Graph Attributes (Ctrl+G)")

#------------------------------------------------------------------------------
#  Graph actions:
#------------------------------------------------------------------------------

node_action = Action(name="&Node", accelerator="Alt+N", action="add_node",
    image=ImageResource("add"), tooltip="Node (Alt+N)")

edge_action = Action(name="&Edge", accelerator="Alt+E", action="add_edge",
    image=ImageResource("add2"), tooltip="Edge (Alt+E)")

#------------------------------------------------------------------------------
#  Help actions:
#------------------------------------------------------------------------------

# Action to show help for the graph.
help_action = Action(name="Help", action="show_help",
    image=ImageResource("help.png"), tooltip="Help")

about_action = Action(name="About Godot", action="about_godot",
    image=ImageResource("about"), tooltip="About Godot")

#------------------------------------------------------------------------------
#  Menus:
#------------------------------------------------------------------------------

file_menu = Menu(
    "|", # Hack suggested by Brennan Williams to achieve correct ordering
    new_action, "_",
    open_action, save_action, revert_action, "_",
    close_action, name="&File"
)

edit_menu = Menu("|", undo_action, redo_action, name="&Edit")

view_menu = Menu("|", configure_graph_action, name="&View")

graph_menu = Menu("|", node_action, edge_action, name="&Graph")

help_menu = Menu("|", help_action, "_", about_action, name="&Help")

menubar = MenuBar(file_menu, edit_menu, view_menu, graph_menu, help_menu)

#------------------------------------------------------------------------------
#  Godot "ToolBar" instance:
#------------------------------------------------------------------------------

toolbar = ToolBar(
    "|", #close_action, "_",
    new_action, open_action, save_action, "_",
    undo_action, redo_action, "_",
    node_action, edge_action, configure_graph_action,
    show_tool_names=False, #show_divider=False
)

# EOF -------------------------------------------------------------------------
