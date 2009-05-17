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

""" Defines power system generator components.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging

from numpy import linspace, pi, array, power

from enthought.traits.api import \
    HasTraits, String, Int, Float, List, Trait, Instance, Bool, Range, \
    Property, Enum, Any, Delegate, Tuple, Array, Disallow, cached_property

#from pylon.traits import ConvexPiecewise

from pylon.ui.generator_view import generator_view

#------------------------------------------------------------------------------
#  Logging:
#------------------------------------------------------------------------------

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

#------------------------------------------------------------------------------
#  "Generator" class:
#------------------------------------------------------------------------------

class Generator(HasTraits):
    """ Fixes voltage magnitude and active power injected at the bus
        or when at its reactive power limit fixes active and reactive power
        injected.
    """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # Human readable identifier.
    name = String("g", desc="generator name")

    # Total MVA base of this machine
    # FIXME: default to self.bus.base_mva
    base_mva = Float(desc="total MVA base of this machine")

    # Voltage amplitude setpoint (PV) (p.u.).
    v_amplitude = Float(1.0, desc="voltage amplitude setpoint (PV) (p.u.)")

    # Maximum voltage (p.u.).
#    v_max = Float(desc="maximum voltage (p.u.)")

    # Minimum voltage (p.u.).
#    v_min = Float(desc="minimum voltage (p.u.)")

    # Active power output (p.u.).
#    p = Float(1.0, desc="active power (p.u.)")
    p = Range(value=1.0, low="p_min", high="p_max", desc="active power (p.u.)")

    # Maximum real power output rating (p.u.).
    p_max = Float(5.0, desc="maximum real power output (p.u.)")

    # Minimum real power output rating (p.u.).
    p_min = Float(0.0, desc="minimum real power output (p.u.)")

    # Reactive power output (p.u.).
#    q = Float(0.0, style='readonly', desc="reactive power output (p.u.)")
    q = Range(value=0.0, low="q_min", high="q_max",
              desc="reactive power output (p.u.)")

    # Maximum reactive power rating (p.u.).
    q_max = Float(3.0, desc="maximum reactive power (PV) (p.u.)")

    # Minimum reactive power (p.u.).
    q_min = Float(-3.0, desc="minimum reactive power (PV) (p.u.)")

    # Is the generator at its reactive power limit?
    q_limited = Bool(False, style="readonly",
        desc="true if generator at reactive power limit")

    def _q_changed(self, new):
        """ Handles the reactive power limit of the generator.
        """
        if self.q_min <= new <= self.q_max:
            self.q_limited = False
        else:
            self.q_limited = True


    # Apparent power rating (MVA).
#    s_rating = Float(desc="power rating MVA (p.u.)")

    # Voltage rating.
#    v_rating = Float(desc="voltage rating kV (p.u.)")

    mu_p_max = Float(style="readonly")
    mu_p_min = Float(style="readonly")
    mu_q_max = Float(style="readonly")
    mu_q_min = Float(style="readonly")

    # Allow conversion to impedance.
#    z = Bool(desc="allow conversion to impedance (PQ)")

    # Loss participation coefficient.
#    zeta = Float(desc="loss participation coefficient")

    # Is the generator in service?
    online = Bool(True, desc="connection status")

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = generator_view

    #--------------------------------------------------------------------------
    #  OPF traits:
    #--------------------------------------------------------------------------

    # The output power that the Generator is despatched to generate
    # as a result of solving the OPF problem:
    p_despatch = Float(desc="a result of the OPF (p.u.)")
#    p_despatch = Range(low="p_min_bid", high="p_max_bid",
#                       desc="OPF result (p.u.)")

    # Maximum active power output bid.  Used in OPF routines.  Should be less
    # than or equal to p_max.  Defaults to p_max.
#    p_max_bid = Float(5.0, desc="maximum active power bid (p.u.)")
#    p_max_bid = Range(value="p_max", low="p_min_bid", high="p_max",
#                      desc="maximum active power bid (p.u.)")
    p_max_bid = Property(Float,
#                         Range(value="p_max", low="p_min_bid", high="p_max"),
#                         depends_on=["p_max", "p_min_bid"],
                         desc="maximum active power bid (p.u.)")
    _p_max_bid = Float

    def __p_max_bid_default(self):
        return self.p_max

    def _get_p_max_bid(self):
        """ Property getter.
        """
        return self._p_max_bid

    def _set_p_max_bid(self, value):
        """ Property setter.
        """
        if value > self.p_max:
            self._p_max_bid = self.p_max
        elif value < self.p_min_bid:
            self._p_max_bid = self.p_min_bid
        else:
            self._p_max_bid = value

#    def _p_max_bid_changed(self, new):
#        """ Static event handler.
#        """
#        if new > self.p_max:
#            self.p_max_bid = self.p_max

    # Minimum active power bid. Used in OPF routines.  Should be greater than
    # or equal to p_min. Defaults to p_min.
#    p_min_bid = Float(0.0, desc="minimum active power bid (p.u.)")
#    p_min_bid = Range(value="p_min", low="p_min", high="p_max_bid",
#                      desc="minimum active power bid (p.u.)")
    p_min_bid = Property(Float,
#                         Range(value="p_min", low="p_min", high="p_max_bid"),
#                         depends_on=["p_min", "p_max_bid"],
                         desc="minimum active power bid (p.u.)")
    _p_min_bid = Float

    def __p_min_bid_default(self):
        return self.p_min

    def _get_p_min_bid(self):
        """ Property getter.
        """
        return self._p_min_bid

    def _set_p_min_bid(self, value):
        """ Property setter.
        """
        if value < self.p_min:
            self._p_min_bid = self.p_min
        elif value > self.p_max_bid:
            self._p_min_bid = self.p_max_bid
        else:
            self._p_min_bid = value

#    def _p_min_bid_changed(self, new):
#        """ Static event handler.
#        """
#        if new < self.p_min:
#            self.p_min_bid = self.p_min

    # Actual active power bid.
#    p_bid = Float(desc="actual active power bid (p.u.)")

    # Start up cost (GBP).
    c_startup = Float(desc="start up cost (GBP)")

    # Shut down cost (GBP)
    c_shutdown = Float(desc="shut down cost (GBP)")

    # Model type used to define the generator cost.
    cost_model = Enum("Polynomial", "Piecewise Linear")

#    polynomial = List(Float, [1.0, 0.1, 0.01])

    # Only quadratic polynomial cost curves supported
    cost_coeffs = Tuple(Float(1.0), Float(0.1), Float(0.01),
        desc="polynomial cost curve coefficients")

    #  Points of the piecewise linear cost curve.
    pwl_points = List(Tuple(Float, Float, labels=["x", "y"], cols=2),
        [(0.0, 0.0), (1.0, 1.0)])
#    pwl_points = ConvexPiecewise # FIXME: Implement trait with validation.

    # Real power cost at current output.
    p_cost = Property(Float, desc="generator real power output cost",
        depends_on=["p", "cost_coeffs", "pwl_points", "cost_model"])

    # Cost to produce one extra MW.
    p_cost_marginal = Property(Float, desc="cost to produce one extra MW",
        depends_on=["p_cost"])

    # Plot data.
    xdata = Property(Array, depends_on=["p_min", "p_max", "pw_linear"])
    ydata = Property(Array, depends_on=["cost_coeffs", "pwl_points"])

    #--------------------------------------------------------------------------
    #  Trait initialisers:
    #--------------------------------------------------------------------------

    def _p_max_bid_default(self):
        """ Trait initialiser.
        """
        return self.p_max


    def _p_min_bid_default(self):
        """ Trait initialiser.
        """
        return self.p_min

    #--------------------------------------------------------------------------
    #  Property getters:
    #--------------------------------------------------------------------------

    @cached_property
    def _get_p_cost(self):
        """ Real power cost given power output and the current cost function
        """
        if self.cost_model == "Polynomial":
            x = self.p
            c0, c1, c2 = self.cost_coeffs
            cost = c0 + c1*x + c2*x**2
            logger.debug("Generator [%s] cost (polynomial) set to: %f" %
                (self, cost))
            return cost

        elif self.cost_model == "Piecewise Linear":
            p = self.p
            points = self.pwl_points
            n_points = len(points)
            if n_points == 0:
                cost = 0
                logger.debug("No pw points. Cost: %f" % cost)
                return cost
            elif n_points == 1:
                x, y = points[0]
                cost = y
                logger.debug("One pw point (%f, %f). Cost: %f" % (x, y, cost))
                return cost
            else:
                # Handle power being before first point
                # FIXME: Implement robust pw linear model
                x0, y0 = points[0]
                if p <= x0:
                    cost = y0
                    logger.debug("Generator power less then lowest pw point. "
                        "Cost set to: %f" % cost)
                    return cost
                # Handle power being above last point
                xn, yn = points[n_points-1]
                if p >= xn:
                    cost = yn
                    logger.debug("Generator power greater then last pw point. "
                        "Cost set to: %f" % cost)
                    return cost
                # Compute the cost for the piece
                for i in range(n_points-1):
                    x1, y1 = points[i]
                    x2, y2 = points[i+1]
                    if p > x1 and p < x2:
                        # y = mx + c
                        m = (y2-y1)/(x2-x1)
                        cost = m*p + y1
                        logger.debug( "Generator [%s] cost (pw linear) set "
                            "to: %f" % (self, cost))
                        return cost
        else:
            logger.error("Invalid cost model [%s]" % self.cost_model)


    def _get_p_cost_marginal(self):
        """ Property getter.
        """
#        if self.cost_model == "Polynomial":
#            x = 1
#            c0, c1, c2 = self.cost_coeffs
#            return c0*x**2 + c1*x + c2
#        else:
#            logger.warn("PW linear cost model not supported for marginal "
#                "cost property")
        if self.p != 0.0:
            return self.p_cost / self.p
        else:
            return 0.0

    #--------------------------------------------------------------------------
    #  Cost curve plot data:
    #--------------------------------------------------------------------------

    @cached_property
    def _get_xdata(self):
        """ Like Python range, but with (potentially) real-valued arrays.
            a = numpy.arange(start, stop, increment)

            Create array of equally-spaced points using specified number of
            points.
            b = numpy.linspace(start, stop, num_elements)
        """
        if self.cost_model is "Polynomial":
            xdata = linspace(self.p_min, self.p_max, 10)
#            print "POLYNOMIAL XDATA:", xdata
            return xdata
#        elif self.cost_model is "Piecewise Linear":
        else:
            xdata = array([x for x, y in self.pwl_points])
#            print "PIECEWISE XDATA:", xdata
            return xdata
#        else:
#            raise ValueError

    @cached_property
    def _get_ydata(self):
        """ Property getter.
        """
        if self.cost_model is "Polynomial":
            ydata = []
            for x in self.xdata:
                y = 0
                c0, c1, c2 = self.cost_coeffs
                y = c0*x**2 + c1*x + c2
                ydata.append(y)
#            print "POLYNOMIAL YDATA", ydata
            return array(ydata)
#        elif self.cost_model is "Piecewise Linear":
        else:
            ydata = array([y for x, y in self.pwl_points])
#            print "PIECEWISE YDATA", ydata
            return ydata
#        else:
#            raise ValueError

#    p_cost_fixed = Float(
#        desc="fixed cost (active power) (GBP/h)",
#        label="Pcost (fixed)"
#    )

#    p_cost_proportional = Float(
#        desc="proportional cost (active power) (GBP/MWh)",
#        label="Pcost (proportional)"
#    )

#    p_cost_quadratic = Float(
#        desc="quadratic cost (active power) (GBP/MW^2h)",
#        label="Pcost (quadratic)"
#    )

#    q_cost_fixed = Float(
#        desc="fixed cost (reactive power) (GBP/h)",
#        label="Qcost (fixed)"
#    )

#    q_cost_proportional = Float(
#        desc="proportional cost (reactive power) (GBP/MVarh)",
#        label="Qcost (proportional)"
#    )

#    q_cost_quadratic = Float(
#        desc="quadratic cost (reactive power) (GBP/MVar^2h)",
#        label="Qcost (quadratic)"
#    )

    # Optimisation.

    # Is the unit committed?
    u = Bool(False, desc="binary unit commitment variable indicating "
        "if the unit is despatched")

#    cost_tie = Float(desc="tie breaking cost (GBP/MWh)")

#    zeta = Float(desc="loss participation factor")

#    cost_congestion_up = Float(desc="congestion up cost (GBP/h)")

#    cost_congestion_down = Float(desc="congestion down cost (GBP/h)")

#    p_lower = Float(desc="lower real power output of PQ capability curve (MW)")

#    p_upper = Float(desc="upper real power output of PQ capability curve (MW)")

#    q_lower_min = Float(desc="minimum reactive power output at Pc1 (MVAr)")

#    q_lower_max = Float(desc="maximum reactive power output at Pc1 (MVAr)")

#    q_upper_min = Float(desc="minimum reactive power output at Pc2 (MVAr)")

#    q_upper_max = Float(desc="maximum reactive power output at Pc2 (MVAr)")

#    ramp_rate = Float(desc="ramp rate for load following/AGC (MW/min)")

#    ramp_rate_10 = Float(desc="ramp rate for 10 minute reserves (MW)")

#    ramp_rate_30 = Float(desc="ramp rate for 30 minute reserves (MW)")

#    ramp_rate_q = Float(desc="ramp rate for reactive power (2 sec timescale) (MVAr/min)")

#    area_participation_factor = Float

#    p_direction = Bool(desc="only used in continuation power flow analysis (p.u.)")

    # Reserve -----------------------------------------------------------------

#    p_max_reserve = Float(desc="maximum active power reserve (p.u.)")

#    p_min_reserve = Float(desc="minimum active power reserve (p.u.)")

#    cost_reserve = Float(desc="reserve offer price (GBP/MWh)")

    # Ramping -----------------------------------------------------------------

    rate_up = Float(desc="ramp up rate (p.u./h)")

    rate_down = Float(desc="ramp down rate (p.u./h)")

    min_up = Int(desc="minimum running time (h)")

    min_down = Int(desc="minimum shut down time (h)")

    initial_up = Int(desc="initial number of periods up")

    initial_down = Int(desc="initial number of periods down")

#    # Synchoronous machine ----------------------------------------------------

#    # TODO: Implement Range
#    v_objective = Float(desc="Target bus voltage in per-unit")

#    p_generated = Float

#    q_generated = Float

#    resistance_ps = Float(desc="Positive sequence or armature resistance")

#    reactance_ps = Float(desc="Positive sequence or d-axis reactance")

#    resistance_zs = Float(desc="Zero sequence resistance")

#    reactance_zs = Float(desc="Zero sequence reactance")

#    resistance_d_axis_transient = Float

#    time_constant_d_axis_transient = Float(desc="D-axis transient open-circuit time constant")

#    resistance_d_axis_subtransient = Float

#    time_constant_d_axis_subtransient = Float(desc="D-axis subtransient open-circuit time constant")

#    resistance_q_axis_transient = Float

#    time_constant_q_axis_transient = Float(desc="Q-axis transient open-circuit time constant")

#    resistance_q_axis_subtransient = Float

#    time_constant_q_axis_subtransient = Float(desc="Q-axis subtransient open-circuit time constant")

#    inertia = Float(desc="Inertia constant")

#    damping_factor = Float

#    reactance_potier = Float(desc="Requisite if saturation factor used")

#    saturation_factor = Float(desc="Field current required to generate 1.2pu voltage on open-circuit")

#    p_max_mech = Float

#    q_max_mech = Float

#    s_max_mech = Property

    # DoublyFedInductionMachine -----------------------------------------------

#    slip = Range(0, 100, value=10, desc="The difference between the supply "
#        "frequency and the machine rotation frequency")

#    # TODO: Confirm description accuracy
#    reactance_magnetising = Float(desc="The reactance placed in parallel with "
#        "the terminals that is used to represent the current required to induce "
#        "a flux in the stator winding")

#    resistance_stator = Float("The stator resistance")

#    reactance_stator = Float("The stator reactance")

#    # TODO: Find model types
#    motor_model = Enum("DFIG", desc="The model used for the motor")

#    resistance_rotor = Float(desc="The rotor resistance")

#    reactance_rotor = Float(desc="The rotor reactance")

#    resistance_start = Float(desc="Startup rotor resistance")

#    reactance_start = Float(desc="Startup rotor reactance")

#    b = Float(desc="Torque-speed coefficient")

#    c = Float(desc="Torque-speed coefficient")

#    inertia = Float(desc="Inertia constant in Ws/VA")

#    trip_voltage = Float(desc="Voltage below which the machine will be "
#        "disconnected")

#    trip_time = Float(desc="The time required for disconnection")

#    lockout_time = Float(desc="The time after trip beyond which reconnection "
#        "will not be attempted")

#    underspeed = Float(desc="Lower rotational speed limit")

#    overspeed = Float(desc="Upper rotational speed limit")

#    reconnect_time = Float(desc="The time required for reconnection")

#    reconnect_volt = Float(desc="The threshold voltage for reconnection")

#    n_reconnect_max = Int(desc="The maximum number of automatic reconnect "
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

#    feed_busbar = Instance("pylon.bus.Bus")

#    df_power_factor = Float

#    is_q_exported = Bool(desc="If false then reactive power is imported")

#    rotor_reference_frame = Enum("Direct-quadrature", "Real-imaginary")

    #--------------------------------------------------------------------------
    #  Property getters:
    #--------------------------------------------------------------------------

#    def _get_s_max_mech(self):
#        return
#
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

if __name__ == "__main__":
    generator = Generator(p_min=1.0, p_max=6.0, p_min_bid=0.0, p_max_bid=7.0)
    print "Min/max bid:", generator.p_min_bid, generator.p_max_bid
#    generator.configure_traits()

# EOF -------------------------------------------------------------------------
