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

""" PQ load component """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import uuid

from enthought.traits.api import \
    HasTraits, String, Int, Float, List, Trait, Instance, Bool, \
    Range, Default, Property, Enum, Delegate

from pylon.ui.load_view import load_view

#------------------------------------------------------------------------------
#  "Load" class:
#------------------------------------------------------------------------------

class Load(HasTraits):
    """ PQ """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    traits_view = load_view

    id = String(desc="unique identifier")

    name = String("l", desc="load name")

#    rating_s = Float(desc="power rating (MVA)")
#
#    rating_v = Float(desc="voltage rating (p.u.)")

    p = Float(1.0, desc="active power demand (p.u.)")

    q = Float(0.1, desc="reactive power demand (p.u.)")

#    v_max = Float(desc="maximum voltage (p.u.)")
#
#    v_min = Float(desc="minimum voltage (p.u.)")
#
#    z = Bool(desc="allow conversion to impedance (p.u.)")

    in_service = Bool(True, desc="connection status")

    # OPF ---------------------------------------------------------------------

#    p_direction = Bool(desc="active power direction. Used in both "
#        "continuation power flow and optimal power flow analysis (p.u.)")
#
#    q_direction = Bool(desc="reactive power direction. Used in both "
#        "continuation power flow and optimal power flow analysis (p.u.)")
#
#    p_max_bid = Float(desc="maximum active power bid (p.u.)")
#
#    p_min_bid = Float(desc="minimum active power bid (p.u.)")
#
#    # An output of the OPF routine
#    p_bid = Float(
#        desc="optimal active power bid (p.u.)",
#        style="readonly"
#    )
#
#    p_cost_fixed = Float(desc="fixed cost (active power) (GBP/h)")
#
#    p_cost_proportional = Float(desc="proportional cost (active power) "
#        "(GBP/MWh)")
#
#    p_cost_quadratic = Float(desc="quadratic cost (active power) "
#        "(GBP/MW^2h)")
#
#    q_cost_fixed = Float(desc="fixed cost (reactive power) (GBP/h)")
#
#    q_cost_proportional = Float(desc="proportional cost (reactive power) "
#        "(GBP/MVarh)")
#
#    q_cost_quadratic = Float(desc="quadratic cost (reactive power) "
#        "(GBP/MVar^2h)")
#
#    u = Bool(desc="commitment variable")
#
#    cost_tie = Float(desc="tie breaking cost (GBP/MWh)")
#
#    q_max = Float(desc="maximum reactive power (p.u.)")
#
#    q_min = Float(desc="minimum reactive power (p.u.)")
#
#    cost_congestion_up = Float(desc="congestion up cost (GBP/h)")
#
#    cost_congestion_down = Float(desc="congestion down cost (GBP/h)")
#
#    # Demand profile ----------------------------------------------------------
#
#    winter_weekday = List(
#        Float,
#        desc="daily profile for winter working day (%)"
#    )
#
#    winter_weekend = List(
#        Float,
#        desc="daily profile for winter weekend (%)"
#    )
#
#    summer_weekday = List(
#        Float,
#        desc="daily profile for summer working day (%)"
#    )
#
#    summer_weekend = List(
#        Float,
#        desc="daily profile for summer weekend (%)"
#    )
#
#    spring_weekday = List(
#        Float,
#        desc="daily profile for spring/autumn working day (%)"
#    )
#
#    spring_weekend = List(
#        Float,
#        desc="daily profile for spring/autumn weekend (%)"
#    )
#
#    days = List(Float, desc="profile for days of the week (%)")
#
#    weeks = List(Float, desc="profile for weeks of the year (%)")
#
#    alpha = Int(desc="kind of day")
#
#    beta = Int(desc="day of the week")
#
#    gamma = Int(desc="week of the year")
#
#    # Ramping -----------------------------------------------------------------
#
#    rate_up = Float(desc="ramp up rate (p.u./h)")
#
#    rate_down = Float(desc="ramp down rate (p.u./h)")
#
#    min_period_up = Int(desc="minimum # of periods up (h)")
#
#    min_period_down = Int(desc="minimum # of periods down (h)")
#
#    n_period_up = Int(desc="number of periods up")
#
#    n_period_down = Int(desc="number of periods down")

#    # Induction machine -------------------------------------------------------
#    slip = Range(0, 100, value=10, desc="The difference between the supply "
#        "frequency and the machine rotation frequency")
#
#
#    # TODO: Confirm description accuracy
#    reactance_magnetising = Float(desc="The reactance placed in parallel with "
#        "the terminals that is used to represent the current required to induce "
#        "a flux in the stator winding")
#
#    resistance_stator = Float("The stator resistance")
#
#    reactance_stator = Float("The stator reactance")
#
#    # TODO: Find model types
#    motor_model = Enum("Induction", desc="The model used for the motor")
#
#    resistance_rotor = Float(desc="The rotor resistance")
#
#    reactance_rotor = Float(desc="The rotor reactance")
#
#    resistance_start = Float(desc="Startup rotor resistance")
#
#    reactance_start = Float(desc="Startup rotor reactance")
#
#    b = Float(desc="Torque-speed coefficient")
#
#    c = Float(desc="Torque-speed coefficient")
#
#    inertia = Float(desc="Inertia constant in Ws/VA")
#
#    trip_voltage = Float(desc="Voltage below which the machine will be "
#        "disconnected")
#
#    trip_time = Float(desc="The time required for disconnection")
#
#    lockout_time = Float(desc="The time after trip beyond which reconnection "
#        "will not be attempted")
#
#    underspeed = Float(desc="Lower rotational speed limit")
#
#    overspeed = Float(desc="Upper rotational speed limit")
#
#    t_reconnect = Float(desc="The time required for reconnection")
#
#    v_reconnect = Float(desc="The threshold voltage for reconnection")
#
#    n_reconnect_max = Int(desc="The maximum number of automatic reconnect "
#        "attempts")
#
#    p_stator = Property
#
#    q_stator = Property
#
#    p_rotor = Property
#
#    q_rotor = Property
#
#    p_mechanical = Property
#
#    power_factor = Property
#
#    efficiency = Property(Float, depends_on=["p_stator", "p_mechanical"])
#
#    current = Property
#
#    torque = Property

    #--------------------------------------------------------------------------
    #  String representation of the object:
    #--------------------------------------------------------------------------

    def __str__(self): return self.name

    #--------------------------------------------------------------------------
    #  Generate unique identifier:
    #--------------------------------------------------------------------------

    def _id_default(self):
        return self.name + "-#" + uuid.uuid4().hex[:6]

    #--------------------------------------------------------------------------
    #  Property getters:
    #--------------------------------------------------------------------------

#    def _get_p_stator(self):
#        return
#
#    def _get_q_stator(self):
#        return
#
#    def _get_p_rotor(self):
#        return
#
#    def _get_q_rotor(self):
#        return
#
#    def _get_p_mechanical(self):
#        return
#
#    def _get_power_factor(self):
#        return
#
#    def _get_efficiency(self):
#        return
#
#    def _get_current(self):
#        return
#
#    def _get_torque(self):
#        return

# EOF -------------------------------------------------------------------------
