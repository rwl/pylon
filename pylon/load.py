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

""" Defines PQ load components.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from itertools import cycle

from enthought.traits.api import \
    HasTraits, String, Int, Float, List, Trait, Instance, Bool, \
    Range, Default, Property, Enum, Delegate, Disallow, on_trait_change

from pylon.ui.load_view import load_view

#------------------------------------------------------------------------------
#  Percentage trait definition:
#------------------------------------------------------------------------------

percent_trait = Range(low=0.0, high=100.0, value=100.0)

#------------------------------------------------------------------------------
#  "Load" class:
#------------------------------------------------------------------------------

class Load(HasTraits):
    """ Defines a PQ load component.
    """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # Obsolete identifier.
    id = Disallow

    # Human readable identifier.
    name = String("l", desc="load name")

    p = Float(1.0, desc="active power demand (p.u.)")

    q = Float(0.1, desc="reactive power demand (p.u.)")

    # Apparent power rating.
#    s_rating = Float(desc="power rating (MVA)")

    # Voltage rating.
#    v_rating = Float(desc="voltage rating (p.u.)")

    # Maximum voltage.
#    v_max = Float(desc="maximum voltage (p.u.)")

    # Minimum voltage.
#    v_min = Float(desc="minimum voltage (p.u.)")

    # Allow conversion to impedance.
#    z = Bool(desc="allow conversion to impedance (p.u.)")

    # Is the load in service?
    online = Bool(True, desc="connection status")

    #--------------------------------------------------------------------------
    #  Demand profile trait definitions:
    #--------------------------------------------------------------------------

    # Maximum active power (p.u.).
    p_max = Float(desc="maximum reactive power (p.u.)")

    # Minimum active power (p.u.).
    p_min = Float(desc="minimum reactive power (p.u.)")

    # Active power profile (%).
    p_profile = List(percent_trait, [100])

    # Iterator that cycles through the active power profile indefinitely.
    _p_cycle = Trait(cycle, transient=True)

    @on_trait_change("p_profile,p_profile_items")
    def reset_profile(self):
        """ Handles the profile changing and allows the iterator to be reset.
        """
        self._p_cycle = cycle(self.p_profile)


    # Profiled active power output.
    p_profiled = Property

    def _get_p_profiled(self):
        """ Property getter. Returns the active power profiled between the
            maximum and minimum according to the 'p_profile' percentages.
        """
        percent = self._p_cycle.next()
        return (percent / 100) * (self.p_max - self.p_min)

#    winter_weekday = List(percent_trait,
#        desc="daily profile for winter working day (%)")

#    winter_weekend = List(percent_trait,
#        desc="daily profile for winter weekend (%)")

#    summer_weekday = List(percent_trait,
#        desc="daily profile for summer working day (%)")

#    summer_weekend = List(percent_trait,
#        desc="daily profile for summer weekend (%)")

#    spring_weekday = List(percent_trait,
#        desc="daily profile for spring/autumn working day (%)")

#    spring_weekend = List(percent_trait,
#        desc="daily profile for spring/autumn weekend (%)")

#    days = List(percent_trait, desc="profile for days of the week (%)")

#    weeks = List(percent_trait, desc="profile for weeks of the year (%)")

    # Kind of day.
#    alpha = Int(desc="kind of day")

    # Day of the week.
#    beta = Int(desc="day of the week")

    # Week of the year.
#    gamma = Int(desc="week of the year")

    # OPF ---------------------------------------------------------------------

    # Active power direction.
#    p_direction = Bool(desc="active power direction. Used in both "
#        "continuation power flow and optimal power flow analysis (p.u.)")

    # Reactive power direction.
#    q_direction = Bool(desc="reactive power direction. Used in both "
#        "continuation power flow and optimal power flow analysis (p.u.)")

    # Maximum active power bid (p.u.).
#    p_max_bid = Float(desc="maximum active power bid (p.u.)")

    # Maximum active power bid (p.u.).
#    p_min_bid = Float(desc="minimum active power bid (p.u.)")

#    # An output of the OPF routine
#    p_bid = Float(desc="optimal active power bid (p.u.)", style="readonly")

    # Active power fixed cost.
#    p_cost_fixed = Float(desc="fixed cost (active power) (GBP/h)")

    # Active power proportional cost.
#    p_cost_proportional = Float(desc="proportional cost (active power) "
#        "(GBP/MWh)")

    # Active power quadratic cost.
#    p_cost_quadratic = Float(desc="quadratic cost (active power) "
#        "(GBP/MW^2h)")

    # Reactive power fixed cost.
#    q_cost_fixed = Float(desc="fixed cost (reactive power) (GBP/h)")

    # Reactive power proportional cost.
#    q_cost_proportional = Float(desc="proportional cost (reactive power) "
#        "(GBP/MVarh)")

    # Reactive power quadratic cost.
#    q_cost_quadratic = Float(desc="quadratic cost (reactive power) "
#        "(GBP/MVar^2h)")

    # Is the unit committed?
#    u = Bool(desc="commitment variable")

    # Tie breaking cost.
#    cost_tie = Float(desc="tie breaking cost (GBP/MWh)")

    # Congestion up cost.
#    cost_congestion_up = Float(desc="congestion up cost (GBP/h)")

    # Congestion down cost.
#    cost_congestion_down = Float(desc="congestion down cost (GBP/h)")

    #--------------------------------------------------------------------------
    #  Ramping trait definitions:
    #--------------------------------------------------------------------------

    # Ramp up rate.
#    rate_up = Float(desc="ramp up rate (p.u./h)")

    # Ramp down rate.
#    rate_down = Float(desc="ramp down rate (p.u./h)")

    # Minimum # of periods up.
#    min_period_up = Int(desc="minimum # of periods up (h)")

    # Minimum # of periods down.
#    min_period_down = Int(desc="minimum # of periods down (h)")

    # Number of periods up.
#    n_period_up = Int(desc="number of periods up")

    # Number of periods down.
#    n_period_down = Int(desc="number of periods down")

    #--------------------------------------------------------------------------
    #  Induction machine trait definitions:
    #--------------------------------------------------------------------------

    # Difference between supply frequency and machine rotation frequency.
#    slip = Range(0, 100, value=10, desc="difference between the supply "
#        "frequency and the machine rotation frequency")

    # Reactance placed in parallel with the terminals that is used to represent
    # the current required to induce a flux in the stator winding.
#    # TODO: Confirm description accuracy
#    reactance_magnetising = Float(desc="reactance placed in parallel "
#        "with the terminals that is used to represent the current required "
#        "to induce a flux in the stator winding")

    # Stator resistance.
#    r_stator = Float("stator resistance")

    # Stator reactance.
#    x_stator = Float("stator reactance")

    # Model used for the motor.
#    # TODO: Find model types
#    motor_model = Enum("Induction", desc="model used for the motor")

    # Rotor resistance.
#    r_rotor = Float(desc="rotor resistance")

    # Rotor reactance.
#    reactance_rotor = Float(desc="rotor reactance")

    # Startup rotor resistance.
#    r_start = Float(desc="startup rotor resistance")

    # Startup rotor reactance.
#    reactance_start = Float(desc="startup rotor reactance")

    # Torque-speed coefficient.
#    b = Float(desc="torque-speed coefficient")

    # Torque-speed coefficient.
#    c = Float(desc="torque-speed coefficient")

    # Inertia constant in Ws/VA.
#    inertia = Float(desc="inertia constant in Ws/VA")

    # Voltage below which the machine will be disconnected.
#    trip_voltage = Float(desc="voltage below which the machine will be "
#        "disconnected")

    # Time required for disconnection.
#    trip_time = Float(desc="time required for disconnection")

    # Time after trip beyond which reconnection will not be attempted.
#    lockout_time = Float(desc="The time after trip beyond which reconnection "
#        "will not be attempted")

    # Lower rotational speed limit.
#    underspeed = Float(desc="lower rotational speed limit")

    # Upper rotational speed limit.
#    overspeed = Float(desc="upper rotational speed limit")

    # Time required for reconnection.
#    t_reconnect = Float(desc="The time required for reconnection")

    # Threshold voltage for reconnection.
#    v_reconnect = Float(desc="threshold voltage for reconnection")

    # Maximum number of automatic reconnect attempts.
#    n_reconnect_max = Int(desc="maximum number of automatic reconnect "
#        "attempts")

#    p_stator = Property
#    q_stator = Property
#    p_rotor = Property
#    q_rotor = Property

#    p_mechanical = Property

#    power_factor = Property

#    efficiency = Property(Float, depends_on=["p_stator", "p_mechanical"])

#    current = Property

#    torque = Property

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = load_view

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
