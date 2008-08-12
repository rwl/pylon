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
Power system generator classes extended for GUI editing.

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os import path

from enthought.traits.api import \
    HasTraits, String, Instance, Delegate, Any, Property, List

from enthought.traits.ui.api import \
    Item, Group, View, InstanceEditor, HGroup, VGroup, Tabbed, RangeEditor

#from enthought.chaco.chaco_plot_editor import ChacoPlotItem

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
    Item(name="p"),
    Item(name="p_max"),
    Item(name="p_min"),
    "_",
    Item(name="q", enabled_when="q_limited"),
    Item(name="q_max", enabled_when="q_limited"),
    Item(name="q_min", enabled_when="q_limited"),
    "_",
    Item(name="p_cost", style="readonly"),
    Item(name="cost_model"),
    Item(
        name="cost_coeffs",
        height=200,
        visible_when="cost_model=='Polynomial'",
        show_label=False
    ),
    Item(
        name="pwl_points",
        height=200,
        visible_when="cost_model=='Piecewise Linear'",
        show_label=False
    ),
)

#------------------------------------------------------------------------------
#  Generator view:
#------------------------------------------------------------------------------

generator_view = View(
    VGroup(
        VGroup(
            Group(
                Item(name="name"),
                Item(name="in_service"),
            ),
#            Group(
#                Item(name="rating_s"),
#                Item(name="rating_v"),
#                Item(name="v_max"),
#                Item(name="v_min"),
#            ),
            Group(
                Item(
                    name="p",
#                    editor=RangeEditor(
#                        high_name="p_max",
#                        low_name="p_min",
##                        format="%.1f",
##                        label_width=28,
#                        mode="auto"
#                    )
                ),
                Item(name="p_max"),
                Item(name="p_min"),
                "_",
                Item(
                    name="q",
                    editor=RangeEditor(
                        high_name="q_max",
                        low_name="q_min",
                        mode="auto"
                    ),
                    enabled_when="q_limited"
                ),
                Item(name="q_max"),
                Item(name="q_min"),
            ),
            label="Power Flow", show_border=True
        ),
        HGroup(
#            VGroup(
#                Group(
#                    Item(name="p_max_bid"),
#                    Item(name="p_min_bid"),
#                    Item(name="p_bid"),
#                    label="Bids",
#                    show_border=True
#                ),
#                Group(
#                    Item(name="rate_up"),
#                    Item(name="rate_down"),
#                    Item(name="min_period_up"),
#                    Item(name="min_period_down"),
#                    Item(name="initial_period_up"),
#                    Item(name="initial_period_down"),
#                ),
#            ),
            Group(
                Item(name="p_cost", style="readonly"),
                Item(name="cost_model"),
                Item(
                    name="cost_coeffs",
                    height=200,
                    visible_when="cost_model=='Polynomial'",
                    show_label=False
                ),
                Item(
                    name="pwl_points",
                    height=200,
                    visible_when="cost_model=='Piecewise Linear'",
                    show_label=False
                ),
#                Item(name="cost_startup"),
#                Item(name="cost_shutdown"),
#                Item(name="p_cost_fixed"),
#                Item(name="p_cost_proportional"),
#                Item(name="p_cost_quadratic"),
#                Item(name="q_cost_fixed"),
#                Item(name="q_cost_proportional"),
#                Item(name="q_cost_quadratic"),
#                label="Costs"
            ),
#            Group(
#                ChacoPlotItem(
#                    "xdata", "ydata",
#                    type="line",
#
#                    # Basic axis and label properties
#                    show_label=False,
#                    resizable=True,
#                    orientation="h",
#                    title="Cost curve",
#                    x_label="Real power (p.u.)",
#                    y_label="Cost (GBP)",
#
#                    # Plot properties
#                    color="green",
#                    bgcolor="white",
#
#                    # Specific to scatter plot
#                    marker="circle",
#                    marker_size=2,
#                    outline_color="none",
#
#                    # Border, padding properties
#                    border_visible=True,
#                    border_width=1,
#                    padding_bg_color="lightgray"
#                )
#            ),
            label="OPF", show_border=True
        ),
#        HGroup(
#            Group(
#                Item(name="v_objective"),
#                Item(name="p_generated"),
#                Item(name="q_generated"),
#                Item(name="resistance_ps"),
#                Item(name="reactance_ps"),
#                Item(name="resistance_zs"),
#                Item(name="reactance_zs"),
#                Item(name="resistance_d_axis_transient"),
#                Item(name="time_constant_d_axis_transient"),
#                Item(name="resistance_d_axis_subtransient"),
#                Item(name="time_constant_d_axis_subtransient"),
#                Item(name="resistance_q_axis_transient"),
#                Item(name="time_constant_q_axis_transient"),
#                Item(name="resistance_q_axis_subtransient"),
#                Item(name="time_constant_q_axis_subtransient"),
#                Item(name="inertia"),
#                Item(name="damping_factor"),
#                Item(name="reactance_potier"),
#                Item(name="saturation_factor"),
#                Item(name="p_max_mech"),
#                Item(name="q_max_mech"),
#                Item(name="s_max_mech")
#            ),
#            label="Synchronous Machine"
#        ),
#        HGroup(
#            Group(
#                Item(name="slip"),
#                Item(name="reactance_magnetising"),
#                Item(name="resistance_stator"),
#                Item(name="reactance_stator"),
#                Item(name="motor_model"),
#                Item(name="resistance_rotor"),
#                Item(name="reactance_rotor"),
#                Item(name="resistance_start"),
#                Item(name="reactance_start"),
#                Item(name="b"),
#                Item(name="c"),
#            ),
#            Group(
#                Item(name="inertia"),
#                Item(name="trip_voltage"),
#                Item(name="trip_time"),
#                Item(name="lockout_time"),
#                Item(name="underspeed"),
#                Item(name="overspeed"),
#                Item(name="reconnect_time"),
#                Item(name="reconnect_volt"),
#                Item(name="n_reconnect_max"),
#                Item(name="feed_busbar"),
#                Item(name="df_power_factor"),
#                Item(name="is_q_exported"),
#                Item(name="rotor_reference_frame")
#            ),
#            Group(
#                Item(name="p_stator"),
#                Item(name="q_stator"),
#                Item(name="p_rotor"),
#                Item(name="q_stator"),
#                Item(name="p_mechanical"),
#                Item(name="power_factor"),
#                Item(name="efficiency"),
#                Item(name="current"),
#                Item(name="torque"),
#            ),
#            label="DFIG"
#        )
        dock="tab"
    ),
#    title="Generator properties",
#    icon=ImageResource(path.join(ICON_LOCATION, "frame.ico")),
    id="default_generator_view",
    resizable=True,
#    scrollable=True,
    buttons=["OK", "Cancel", "Help"]
)

# EOF -------------------------------------------------------------------------
