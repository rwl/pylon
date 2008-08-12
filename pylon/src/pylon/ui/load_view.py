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

""" Power system PQ load class extended for GUI editing. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os import path

from enthought.traits.api import \
    HasTraits, String, Instance, Delegate, Any, Property, List

from enthought.traits.ui.api import \
    Item, Group, View, InstanceEditor, HGroup, VGroup, Tabbed

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
    Item(name="p"),
    Item(name="q"),
)

#------------------------------------------------------------------------------
#  Load view:
#------------------------------------------------------------------------------


load_view = View(
    VGroup(
        Group(
            Item(name="name"),
            Item(name="in_service"),
#            Item(
#                name="bus",
#                editor=InstanceEditor(
#                    name="buses",
#                    editable=False,
#                    label="Connected to:"
#                )
#            ),
#            Item(name="rating_s"),
#            Item(name="rating_v"),
            label="Traits",
            show_border=True
        ),
        Group(
            Item(name="p"),
            Item(name="q"),
#            Item(name="v_max"),
#            Item(name="v_min"),
            label="Power Flow",
            show_border=True
        ),
#        Group(
#            Item(name="p_max_bid"),
#            Item(name="p_min_bid"),
#            Item(name="p_bid"),
#            Item(name="p_cost_fixed"),
#            Item(name="p_cost_proportional"),
#            Item(name="p_cost_quadratic"),
#            Item(name="q_cost_fixed"),
#            Item(name="q_cost_proportional"),
#            Item(name="q_cost_quadratic"),
#            Item(name="rate_up"),
#            Item(name="rate_down"),
#            Item(name="min_period_up"),
#            Item(name="min_period_down"),
#            label="OPF"
#        ),
#        Group(
#            Item(name="slip"),
#            Item(name="reactance_magnetising"),
#            Item(name="resistance_stator"),
#            Item(name="reactance_stator"),
#            Item(name="resistance_start"),
#            Item(name="reactance_start"),
#            Item(name="b"),
#            Item(name="c"),
#            Item(name="inertia"),
#            Item(name="trip_voltage"),
#            Item(name="lockout_time"),
#            Item(name="underspeed"),
#            Item(name="overspeed"),
#            Item(name="t_reconnect"),
#            Item(name="v_reconnect"),
#            Item(name="p_stator"),
#            Item(name="q_stator"),
#            Item(name="p_rotor"),
#            Item(name="q_rotor"),
#            Item(name="p_mechanical"),
#            Item(name="power_factor"),
#            Item(name="efficiency"),
#            Item(name="current"),
#            Item(name="torque"),
#            label="Induction machine"
#        )
    ),
#    title='PQ Load properties',
#    icon = ImageResource(path.join(ICON_LOCATION, 'frame.ico')),
    resizable = True,
    scrollable=True,
    buttons=["OK", "Cancel", "Help"]
)

# EOF -------------------------------------------------------------------------
