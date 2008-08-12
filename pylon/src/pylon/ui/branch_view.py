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
Power system branch classes extended for GUI editing.

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os import path

from enthought.traits.api import \
    HasTraits, String, Instance, Delegate, Any, Property, List

from enthought.traits.ui.api import \
    Item, Group, View, InstanceEditor, HGroup, VGroup, Tabbed, RangeEditor

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

ICON_LOCATION = path.join(path.dirname(__file__), "images")

#------------------------------------------------------------------------------
#  Minimal view:
#------------------------------------------------------------------------------

minimal_view = View(
    Item(name="name"),
    Item(name="in_service"),
    "_",
    Item(
        name="source_bus",
        editor=InstanceEditor(name="buses", editable=False)
    ),
    Item(
        name="target_bus",
        editor=InstanceEditor(name="buses", editable=False)
    ),
    "_",
    Item(name="r"),
    Item(name="x"),
    Item(name="b"),
    "_",
    Item(name="ratio"),
    Item(name="phase_shift"),

)

#------------------------------------------------------------------------------
#  Branch view:
#------------------------------------------------------------------------------

branch_view = View(
    VGroup(
        Group(
            Item(name="name"),
            Item(name="in_service"),
            "_",
            Item(
                name="source_bus",
                editor=InstanceEditor(name="buses", editable=False)
            ),
            Item(
                name="target_bus",
                editor=InstanceEditor(name="buses", editable=False)
            ),
#            "_",
#            Item(name="rating_s"),
#            Item(name="rating_v"),
#            Item(name="rating_f"),
#            "_",
#            Item(name="s_max"),
#            Item(name="i_max"),
#            Item(name="p_max"),
#            "_",
#            Item(name="p_source"),
#            Item(name="p_target"),
#            Item(name="q_source"),
#            Item(name="q_target"),
            show_border=True,
            label="Traits"
        ),
        Group(
            Item(name="r"),
            Item(name="x"),
            Item(name="b"),
#            Item(name="r_zero"),
#            Item(name="x_zero"),
            show_border=True,
            label="Line"
        ),
        Group(
            Item(name="ratio"),
            Item(name="phase_shift"),
#            Item(
#                name="phase_shift",
#                editor=RangeEditor(
#                    high_name="phase_shift_max",
#                    low_name="phase_shift_min",
##                    format="%.1f",
##                    label_width=28,
#                    mode="auto"
#                )
#            ),
            Item(name="phase_shift_max"),
            Item(name="phase_shift_min"),
#            Item(name="phase_shift_increment"),
#            Item(name="winding"),
#            Item(name="tap_position"),
#            Item(name="tap_increment"),
#            Item(name="tap_position_max"),
#            Item(name="tap_position_min"),
#            Item(name="v_objective"),
#            Item(name="v_relay_bandwidth"),
#            "_",
#            Item(name="phase_shift"),
#            Item(name="phase_shift_increment"),
#            Item(name="phase_shift_max"),
#            Item(name="phase_shift_min"),
#            "_",
#            Item(name="delta_max"),
#            Item(name="delta_min"),
            show_border=True,
            label="Transformer"
        )
    ),
#    title="Branch properties",
#    icon = ImageResource(path.join(ICON_LOCATION, "frame.ico")),
    resizable = True,
    scrollable=True,
    buttons=["OK", "Cancel", "Help"]
)

# EOF -------------------------------------------------------------------------
