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

""" Toolkit independent network views """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os import path

from enthought.traits.api import \
    HasTraits, Instance, List, File, Property, Bool, String, Any

from enthought.traits.ui.api import \
    View, Group, Item, InstanceEditor, Tabbed, TreeEditor, \
    TreeNode, Label, VGroup, HGroup, spring

from enthought.traits.ui.menu import NoButtons, OKCancelButtons
from enthought.pyface.image_resource import ImageResource
from enthought.naming.unique_name import make_unique_name

#from enthought.chaco.chaco_plot_editor import ChacoPlotItem

from pylon.ui.bus_view import bus_view
from pylon.ui.bus_table import buses_table_editor
from pylon.ui.branch_view import branch_view
from pylon.ui.branch_table import branches_table_editor
from pylon.ui.generator_table import all_generators_table_editor
from pylon.ui.load_table import all_loads_table_editor

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

frame_icon = ImageResource("frame.ico")

#------------------------------------------------------------------------------
#  Minimal "View" instance:
#------------------------------------------------------------------------------

minimal_view = View(
    Group(
        Item(name="name", style="simple"),
        "_",
        Item(name="mva_base", label="Base MVA", style="simple"),
        Item(name="slack_model", style="readonly"),
        "_",
        Item(name="n_buses", label="Buses", style="readonly"),
    #    Item(name="n_branches", label="Branches", style="readonly"),
        Item(name="n_generators", label="Generators", style="readonly"),
    ),
    id="network_view.minimal_view",
    buttons=OKCancelButtons
)

#------------------------------------------------------------------------------
#  Buses "View" instance:
#------------------------------------------------------------------------------

buses_view = View(
    Item(
        name="buses", show_label=False,
        editor=buses_table_editor, id=".buses_table"
    ),
    id="network_view.buses_view", title="Buses",
    icon=frame_icon, resizable=True, style="custom",
    close_result=True, buttons=["OK"],
    width=.4, height=.5
)

#------------------------------------------------------------------------------
#  Branches "View" instance:
#------------------------------------------------------------------------------

branches_view = View(
    Group(
        Item(
            name="branches", show_label=False,
            editor=branches_table_editor, id=".branches_table"
        )
    ),
    id="network_view.branches_view", title="Branches",
    icon=frame_icon, resizable=True, style="custom",
    close_result=True, buttons=["OK"],
    width=.5, height=.5
)

#------------------------------------------------------------------------------
#  All genetrators "View" instance:
#------------------------------------------------------------------------------

all_generators_view = View(
    Group(
        Item(
            name="generators", show_label=False,
            editor=all_generators_table_editor, id=".generators_table"
        )
    ),
    id="pylon.ui.network_view.all_generators_view"
)

#------------------------------------------------------------------------------
#  All loads "View" instance:
#------------------------------------------------------------------------------

all_loads_view = View(
    Group(
        Item(
            name="loads", show_label=False,
            editor=all_loads_table_editor, id=".loads_table"
        )
    ),
    id="pylon.ui.network_view.all_loads_view"
)

#------------------------------------------------------------------------------
#  Pylon "View" instance:
#------------------------------------------------------------------------------

network_view = View(
    VGroup(
        HGroup(
            Item(name="name", style="simple"),
            Item(name="mva_base", label="Base MVA", style="simple")
        ),
        Tabbed(
            Group(
                Item(
                    name="buses", show_label=False,
                    editor=buses_table_editor,
                    id=".network_buses_table"
                ),
                label="Buses",
#                dock="tab"
            ),
            Group(
                Item(
                    name="branches", show_label=False,
                    editor=branches_table_editor,
                    id=".network_branches_table"
                ),
                label="Branches",
#                dock="tab"
            ),
            Group(
                Item(
                    name="generators", show_label=False,
                    editor=all_generators_table_editor,
                    id=".network_generators_table"
                ),
                label="_generators"
            ),
            Group(
                Item(
                    name="loads", show_label=False,
                    editor=all_loads_table_editor,
                    id=".network_loads_table"
                ),
                label="_loads"
            ),
            dock="tab", springy=True
        ),
    ),
    id="pylon.ui.network_view.network_view",
    icon=frame_icon, resizable=True,
    style="custom", kind="livemodal", buttons=OKCancelButtons,
#    width=.81, height=.81
)

#------------------------------------------------------------------------------
#  Pylon "View" instance:
#------------------------------------------------------------------------------

bus_plot_view = View(
#    Group(
#        ChacoPlotItem(
#            "bus_indexes", "v_phases",
#            type="scatter",
#
#            # Basic axis and label properties
#            show_label=False,
#            resizable=True,
#            orientation="h",
#            title="Bus voltage phases",
#            x_label="Buses",
#            y_label="Va (p.u.)",
#
#            # Plot properties
#            color="red",
#            bgcolor="white",
#
#            # Specific to scatter plot
#            marker="circle",
#            marker_size=6,
#            outline_color="none",
#
#            # Border, padding properties
#            border_visible=True,
#            border_width=1,
#            padding_bg_color="white"
#        )
#    ),
    id="network_view.bus_plot_view",
    icon=frame_icon,
    resizable=True,
    style="custom",
    width=.81,
    height=.81,
    kind="live",
    buttons=NoButtons,
)

# EOF -------------------------------------------------------------------------
