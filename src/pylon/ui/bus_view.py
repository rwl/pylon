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

""" Toolkit independent Bus views """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os import path

from enthought.traits.ui.api import \
    View, Group, Item, InstanceEditor, Tabbed, HGroup, VGroup

from enthought.traits.ui.menu import NoButtons, OKCancelButtons
from enthought.pyface.image_resource import ImageResource

from generator_table import generators_table_editor
from load_table import loads_table_editor

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

ICON_LOCATION = path.join(path.dirname(__file__), "images")

#------------------------------------------------------------------------------
#  Minimal view:
#------------------------------------------------------------------------------

minimal_view = View(
    Item(name="name"),
    "_",
    Item(
        name="slack", enabled_when="has_generation",
        tooltip="To be slack one or more attached Generator required"
    ),
    Item(name="type", style="readonly"),
    "_",
    Item(name="v_amplitude_guess", style="text"),
    Item(name="v_phase_guess"),
    Item(name="g_shunt"),
    "_",
    Item(name="n_generators", style="readonly", label="Generators"),
    Item(name="n_loads", style="readonly", label="Loads"),
#    Item(name="p_supply", style="readonly"),
#    Item(name="q_supply", style="readonly"),
#    Item(name="p_demand", style="readonly"),
#    Item(name="q_demand", style="readonly"),
    buttons=OKCancelButtons
)

#------------------------------------------------------------------------------
#  Bus view:
#------------------------------------------------------------------------------

bus_view = View(
    VGroup(
        VGroup(
            Group(
                Item(name="name"),
                Item(
                    name="slack",
                    enabled_when="has_generation",
                    tooltip="To be made slack one or more "
                        "attached Generator is requisite"
                ),
                Item(name="type", style="readonly"),
#                Item(name="n_generators", style="readonly"),
#                Item(name="n_loads", style="readonly"),
#                Item(name="p_supply", style="readonly"),
#                Item(name="q_supply", style="readonly"),
#                Item(name="p_demand", style="readonly"),
#                Item(name="q_demand", style="readonly")
            ),
            Group(
#                Item(name="v_nominal"),
                Group(
                    Item(name="v_amplitude_guess"),
                    Item(name="v_phase_guess"),
                    label="Initial voltage",
                    show_border=True
                ),
#                Item(name="v_max"),
#                Item(name="v_min"),
#                Item(name="v_amplitude"),
#                Item(name="v_phase"),
                Item(name="g_shunt"),
            )
        ),
        Tabbed(
            Group(
                Item(
                    name="generators",
                    show_label=False,
                    editor=generators_table_editor,
                    id=".generators_table"
                ),
                label="Generators"
            ),
            Group(
                Item(
                    name="loads",
                    show_label=False,
                    editor=loads_table_editor,
                    id=".loads_table"
                ),
                label="Loads"
            ),
            dock="tab", springy=True
        ),
    ),
    id="pylon.ui.bus_view",
#    dock="fixed",
#    title="Bus properties",
    icon=ImageResource(path.join(ICON_LOCATION, "frame.ico")),
    resizable=True,
#    scrollable=True,
    buttons=OKCancelButtons
)

#------------------------------------------------------------------------------
#  Generators view:
#------------------------------------------------------------------------------

generators_view = View(
    Item(
        name="generators",
        show_label=False,
        editor=generators_table_editor,
        id=".generators_table"
    ),
    id="pylon.ui.bus_view.generators_view",
#    dock="tab"
#    dock="fixed",
    icon=ImageResource("frame.ico", search_path=[ICON_LOCATION]),
    resizable=True, #scrollable=True,
    buttons=OKCancelButtons
)

#------------------------------------------------------------------------------
#  Loads view:
#------------------------------------------------------------------------------

loads_view = View(
    Item(
        name="loads", show_label=False,
        editor=loads_table_editor,
        id=".loads_table"
    ),
    id="pylon.ui.bus_view.loads_view",
#    dock="tab"
#    dock="fixed",
    icon=ImageResource("frame.ico", search_path=[ICON_LOCATION]),
    resizable=True, #scrollable=True,
    buttons=OKCancelButtons
)

# EOF -------------------------------------------------------------------------
