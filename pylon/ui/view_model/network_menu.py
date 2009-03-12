#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard W. Lincoln
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

""" View model menus and menu items.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname

from enthought.pyface.api import ImageResource
from enthought.traits.ui.menu import MenuBar, ToolBar, Menu, Action

from desktop_menu import file_menu, menubar, toolbar

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = join(dirname(__file__), "../images")

#------------------------------------------------------------------------------
#  File actions:
#------------------------------------------------------------------------------

import_matpower_action = Action( name    = "&MATPOWER",
                                 action  = "read_matpower",
                                 image   = ImageResource("matpower",
                                     search_path = [IMAGE_LOCATION]),
                                 tooltip = "Import MATPOWER data file" )

import_psse_action = Action( name    = "&PSS/E",
                             action  = "read_psse",
                             image   = ImageResource("psse",
                                 search_path = [IMAGE_LOCATION]),
                             tooltip = "Import PTI PSS/E data file" )

import_psat_action = Action( name    = "P&SAT",
                             action  = "read_psat",
                             image   = ImageResource("psat",
                                search_path = [IMAGE_LOCATION]),
                             tooltip = "Import PSAT data file" )

export_matpower_action = Action( name    = "&MATPOWER",
                                 action  = "write_matpower",
                                 image   = ImageResource("matpower",
                                     search_path = [IMAGE_LOCATION]),
                                 tooltip = "Export to MATPOWER data file" )

#------------------------------------------------------------------------------
#  View actions:
#------------------------------------------------------------------------------

tree_view_action = Action( name        = "Tree",
                           accelerator = "F1",
                           action      = "toggle_tree",
                           image       = ImageResource("tree",
                               search_path = [IMAGE_LOCATION]),
                           tooltip     = "Tree view (F1)" )

network_table_action = Action( name        = "Network Table",
                               accelerator = "F2",
                               action      = "show_network_table",
                               image       = ImageResource("branch_table",
                                   search_path=[IMAGE_LOCATION]),
                               tooltip     = "Network Table (F2)" )

interactive_graph_action = Action(
    name="&Interactive Graph", accelerator="F3",
    action="toggle_interactive",
#    image=ImageResource("graph.png", search_path=[IMAGE_LOCATION]),
    tooltip="Disables/Enables interactive graph (F3)",
    style="toggle"
)

map_view_action = Action(
    name="&Map", accelerator="F4", action="show_map_view",
    image=ImageResource("graph.png", search_path=[IMAGE_LOCATION]),
    tooltip="Map View (F4)"
)

pf_report_action = Action(
    name="PF Report", accelerator="F5", action="display_pf_report",
    tooltip="Power Flow Report View (F5)"
)

opf_report_action = Action(
    name="OPF Report", accelerator="F6", action="display_opf_report",
    tooltip="Optimal Power Flow Report View (F6)"
)

#bus_plot_action = Action(
#    name="Bu&s Plot", accelerator="F5", action="bus_plot",
#    image=ImageResource("bus_plot.png", search_path=[IMAGE_LOCATION]),
#    tooltip="Bus Plot (F5)"
#)

#branch_plot_action = Action(
#    name="Br&anch Plot", accelerator="F6", action="branch_plot",
#    image=ImageResource("branch_plot.png", search_path=[IMAGE_LOCATION]),
#    tooltip="Branch Plot (F6)"
#)

#------------------------------------------------------------------------------
#  Network actions:
#------------------------------------------------------------------------------

bus_action = Action(
    name="B&us", accelerator="Ctrl+B", action="add_bus",
    image=ImageResource("add.png", search_path=[IMAGE_LOCATION]),
    tooltip="Bus (Ctrl+B)"
)

branch_action = Action(
    name="B&ranch", accelerator="Ctrl+R", action="add_branch",
    image=ImageResource("add2.png", search_path=[IMAGE_LOCATION]),
    tooltip="Branch (Ctrl+R)"
)

dcpf_action = Action(
    name="&DC PF", accelerator="Ctrl+1", action="dcpf",
    image=ImageResource("blank.png", search_path=[IMAGE_LOCATION]),
    tooltip="Run DC PF (Ctrl+1)"
)

dcopf_action = Action(
    name="DC &OPF", accelerator="Ctrl+2", action="dcopf",
    image=ImageResource("blank.png", search_path=[IMAGE_LOCATION]),
    tooltip="Run DC OPF (Ctrl+2)"
)

acpf_action = Action(
    name="AC &PF", accelerator="Ctrl+3", action="acpf",
    image=ImageResource("blank.png", search_path=[IMAGE_LOCATION]),
    tooltip="Run AC PF (Ctrl+3)"
)

acopf_action = Action(
    name="AC OP&F", accelerator="Ctrl+4", action="acopf",
    image=ImageResource("blank.png", search_path=[IMAGE_LOCATION]),
    tooltip="Run DC OPF (Ctrl+4)"
)

#------------------------------------------------------------------------------
#  Menus:
#------------------------------------------------------------------------------

import_menu = Menu(import_psat_action, import_matpower_action,
                   import_psse_action, name="&Import")

export_menu = Menu(export_matpower_action, name="&Export")

file_menu.insert(0, import_menu)
file_menu.insert(0, export_menu)

view_menu = Menu("|", tree_view_action,
                 network_table_action, map_view_action, pf_report_action,
                 opf_report_action, "_", interactive_graph_action,
#                 "_", bus_plot_action, branch_plot_action,
                 name="&View")

network_menu = Menu("|", dcpf_action, dcopf_action, acpf_action, acopf_action,
    "_", bus_action, branch_action, name="&Network")

#------------------------------------------------------------------------------
#  Action managers:
#------------------------------------------------------------------------------

network_menubar = menubar
network_menubar.insert(2, view_menu)
network_menubar.insert(3, network_menu)

network_toolbar = toolbar
network_toolbar.append(bus_action)
network_toolbar.append(branch_action)
network_toolbar.append(network_table_action)

# EOF -------------------------------------------------------------------------
