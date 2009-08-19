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

""" Defines the Pylon network model.
"""

from itertools import cycle


class Network(object):
    """ Defines representation of an electric power system as a graph
        of Bus objects connected by Branches.
    """

    def __init__(self, name="network", base_mva=100.0, buses=None,
            branches=None):
        """ Initialises a new Network instance.
        """
        self.name = name
        # Base apparent power (MVA).
        self.base_mva = base_mva

        if buses is None:
            self.buses = []
        else:
            self.buses = buses

        if branches is None:
            self.branches = []
        else:
            self.branches = branches

    @property
    def connected_buses(self):
        """ Returns a list of buses that are connected to one or more branches
            or the first bus in a branchless system.
        """
        if self.branches:
            source_buses = [e.source_bus for e in self.branches]
            target_buses = [e.target_bus for e in self.branches]

            return [v for v in self.buses if v in source_buses + target_buses]
        else:
            return self.buses[:1]

    @property
    def slack_model(self):
        """ Slack/swing/reference bus model.
        """
        slack_buses = [v for v in self.buses if v.slack]
        if slack_buses:
            return "single"
        else:
            return "distributed"

    @property
    def all_generators(self):
        """ All system generators.
        """
        return [g for v in self.buses for g in v.generators]

    @property
    def online_generators(self):
        """ All in-service generators.
        """
        return [g for g in self.all_generators if g.online]

    @property
    def all_loads(self):
        """ All system loads.
        """
        return [l for v in self.buses for l in v.loads]

    @property
    def online_loads(self):
        """ All in-service loads.
        """
        return [l for l in self.all_loads if l.online]

    @property
    def online_branches(self):
        """ Property getter for in-service branches.
        """
        return [branch for branch in self.branches if branch.online]


class Bus(object):
    """ Defines a power system bus node.
    """

    def __init__(self, name="bus", slack=False, v_base=100.0,
            v_magnitude_guess=1.0, v_angle_guess=0.0, v_max=1.1, v_min=0.9,
            g_shunt=0.0, b_shunt=0.0, generators=None, loads=None):
        """ Initialises a new Bus instance.
        """
        self.name = name
        # Is the bus a reference/slack/swing bus?
        self.slack = slack
        # Base voltage
        self.v_base = v_base
        # Voltage magnitude initial guess (pu).
        self.v_magnitude_guess = v_magnitude_guess
        # Voltage angle initial guess (degrees).
        self.v_angle_guess = v_angle_guess
        # Maximum voltage magnitude (pu).
        self.v_max = v_max
        # Minimum voltage magnitude (pu).
        self.v_min = v_min
        # Shunt conductance (MW (demanded) at V = 1.0 p.u.).
        self.g_shunt = g_shunt
        # Shunt susceptance (MVAr (injected) at V = 1.0 p.u.).
        self.b_shunt = b_shunt

        # Generators defined by their active power and voltage.
        if generators is None:
            self.generators = []
        else:
            self.generators = generators

        # Loads that specify real and reactive power demand.
        if loads is None:
            self.loads = []
        else:
            self.loads = loads

        # Lambda (GBP/MWh).
        p_lambda = 0.0
        # Lambda (GBP/MVAr-hr).
        q_lambda = 0.0

        mu_v_min = 0.0
        mu_v_max = 0.0

    @property
    def mode(self):
        """ Bus mode may be 'pv', 'pq' or 'slack'.
        """
        if self.slack:
            return "slack"
        elif self.generators:
            for g in self.generators:
                if g.q_limited:
                    return "pq"
            return "pv"
        else:
            return "pq"

    @property
    def p_supply(self):
        """ Total active power generation capacity.
        """
        return sum([g.p for g in self.generators])

    @property
    def p_demand(self):
        """ Total active power load.
        """
        return sum([l.p for l in self.loads])

    @property
    def p_surplus(self):
        """ Supply and demand difference.
        """
        return self.p_supply - self.p_demand

    @property
    def q_supply(self):
        """ Total reactive power generation capacity.
        """
        return sum([g.q for g in self.generators])

    @property
    def q_demand(self):
        """ Total reactive power load.
        """
        return sum([l.q for l in self.loads])

    @property
    def q_surplus(self):
        """ Supply and demand difference.
        """
        return self.q_supply - self.q_demand


class Branch(object):
    """ Defines a network edge that links two Bus objects.
    """

    def __init__(self, source_bus, target_bus, name="branch", online=True,
            r=0.001, x=0.001, b=0.001, s_max=2.0, ratio=1.0, phase_shift=0.0):
        """ Initialises a new Branch instance.
        """
        # Source/from/start bus.
        self.source_bus = source_bus
#        self.source_bus_idx = 0
        # Target/to/end bus.
        self.target_bus = target_bus
#        self.target_bus_idx = 0

        self.name = name
        # Is the branch in service?
        self.online = online
        # Positive sequence resistance (pu).
        self.r = r
        # Positive sequence reactance (pu).
        self.x = x
        # Total positive sequence line charging susceptance (pu).
        self.b = b
        # General purpose maximum MVA rating (MVA).
        self.s_max = s_max
        # Transformer off nominal turns ratio.
        self.ratio = ratio
        # Phase shift angle (degrees).
        self.phase_shift = phase_shift

        # Power flow results --------------------------------------------------

        # Active power injected at the source bus (MW).
        self.p_source = 0.0
        # Active power injected at the target bus (MW).
        self.p_target = 0.0
        # Reactive power injected at the source bus (MVAr).
        self.q_source = 0.0
        # Reactive power injected at the target bus (MVAr).
        self.q_target = 0.0

        # |S_source| mu.
        self.mu_s_source = 0.0
        # |S_target| mu.
        self.mu_s_target = 0.0

    @property
    def mode(self):
        """ Branch mode may be 'line' or 'transformer'.
        """
        if self.source_bus.v_magnitude == self.target_bus.v_magnitude:
            return "line"
        else:
            return "transformer"

    @property
    def p_losses(self):
        """ Active power losses.
        """
        return self.p_source - self.p_target

    @property
    def q_losses(self):
        """ Reactive power losses.
        """
        return self.q_source - self.q_target

#------------------------------------------------------------------------------
#  "Generator" class:
#------------------------------------------------------------------------------

class Generator(object):
    """ Defines a power system generator component. Fixes voltage magnitude
        and active power injected at parent bus. Or when at it's reactive
        power limit fixes active and reactive power injected at parent bus.
    """

    def __init__(self, name="generator", online=True, base_mva=100.0, p=100.0,
            p_max=200.0, p_min=0.0, v_magnitude=1.0, q=0.0, q_max=30.0,
            q_min=-30.0, p_max_bid=None, p_min_bid=None, c_startup=0.0,
            c_shutdown=0.0, cost_model="polynomial", pwl_points=None,
            cost_coeffs=None, rate_up=1.0, rate_down=1.0, min_up=0,
            min_down=0, initial_up=1, initial_down=0):
        """ Initialises a new Generator instance.
        """
        self.name = name
        # Is the generator in service?
        self.online = online
        # Machine MVA base.
        self.base_mva = base_mva
        # Active power output (MW).
        self.p = p
        # Maximum active power output (MW).
        self.p_max = p_max
        # Minimum active power output (MW).
        self.p_min = p_min
        # Voltage magnitude setpoint (pu).
        self.v_magnitude = v_magnitude
        # Reactive power output (MVAr).
        self.q = q
        # Maximum reactive power (MVAr).
        self.q_max = q_max
        # Minimum reactive power (MVAr).
        self.q_min = q_min

        # Maximum active power output bid. Used in OPF routines. Should be less
        # than or equal to p_max.
        if p_max_bid is None:
            self.p_max_bid = p_max
        else:
            self.p_max_bid = 0.0
        # Minimum active power bid. Used in OPF routines. Should be greater
        # than or equal to p_min.
        if p_min_bid is None:
            self.p_min_bid = p_min
        else:
            self.p_min_bid = 0.0
        # Start up cost.
        self.c_startup = c_startup
        # Shut down cost.
        self.c_shutdown = c_shutdown
        # Valid values are 'polynomial' and 'piecewise linear'.
        self.cost_model = cost_model
        # Polynomial cost curve coefficients.
        # (a, b, c) relates to: cost = c*p**3 + b*p**2 + a*p.
        if cost_coeffs is None:
            self.cost_coeffs = (0.01, 0.1, 10.0)
        else:
            self.cost_coeffs = cost_coeffs
        # Piecewise linear cost segment points.
        if pwl_points == None:
            self.pwl_points = [(0.0, 0.0), (1.0, 10.0)]
        else:
            self.pwl_points = pwl_points
        # Ramp up rate (p.u./h).
        self.rate_up = rate_up
        # Ramp down rate (p.u./h).
        self.rate_down = rate_down
        # Minimum running time (h).
        self.min_up = min_up
        # Minimum shut down time (h).
        self.min_down = min_down
        # Initial number of periods up.
        self.initial_up = initial_up
        # Initial number of periods down.
        self.initial_down = initial_down

        # The output power that the Generator is despatched to generate
        # as a result of solving the OPF problem.
#        self.p_despatch = 0.0

        self.mu_p_min = None
        self.mu_p_max = None

    @property
    def q_limited(self):
        """ Is the machine at it's limit of reactive power?
        """
        if (self.q >= self.q_max) or (self.q <= self.q_min):
            return True
        else:
            return False

    @property
    def mode(self):
        """ Does the machine represent a generator or a despatchable load.
        """
        raise DeprecationWarning, "Use is_load instead."

        if 0 <= self.p_min < self.p_max:
            return "generator"
        elif self.p_min < self.p_max <= 0.0:
            return "dispatchable load"
        else:
            return "unknown"

    @property
    def p_cost(self):
        """ Active power cost at the current output.
        """
        return self.total_cost(self.p)

    @property
    def is_load(self):
        """ Returns true if the generator if a dispatchable load. This may
            need to be revised to allow sensible specification of both elastic
            demand and pumped storage units.
        """
        return self.p_min < 0.0 and self.p_max == 0.0


    def total_cost(self, p):
        """ Computes total cost for the generator at the given output level.
        """
        if self.cost_model == "piecewise linear":
            n_segments = len(self.pwl_points) - 1
            # Iterate over the piece-wise linear segments.
            for i in range(n_segments):
                x1, y1 = self.pwl_points[i]
                x2, y2 = self.pwl_points[(i + 1)]

                m = (y2 - y1) / (x2 - x1)
                c = y1 - m * x1

                result = m*p + c

                if x1 <= p <= x2:
                    break
#            else:
##                raise ValueError, "Value [%f] outwith pwl cost curve." % p
#                # Use the last segment for values outwith the cost curve.
#                result = m*p + c

        elif self.cost_model == "polynomial":
            result = self.cost_coeffs[-1]

            for i in range(1, len(self.cost_coeffs)):
                result += self.cost_coeffs[-(i + 1)] * p**i

        else:
            raise ValueError

        return result


    def poly_to_pwl(self, n_points=10):
        """ Sets the piece-wise linear cost attribute, converting the
            polynomial cost variable by evaluating at zero and then at
            n_points evenly spaced points between p_min and p_max.
        """
        p_min = self.p_min
        p_max = self.p_max
        self.pwl_points = []
        # Ensure that the cost model is polynomial for calling total_cost.
        self.cost_model = "polynomial"

        if p_min > 0.0:
            # Make the first segment go from the origin to p_min.
            step = (p_max - p_min) / (n_points - 2)

            y0 = self.total_cost(0.0)
            self.pwl_points.append((0.0, y0))

            x = p_min
            n_points -= 1
        else:
            step = (p_max - p_min) / (n_points - 1)
            x = 0.0

        for i in range(n_points):
            y = self.total_cost(x)
            self.pwl_points.append((x, y))
            x += step

        # Change the cost model.
        self.cost_model = "piecewise linear"


    def get_offers(self):
        """ Returns a quantity and price offer created from the cost function.
        """
        from pylon.pyreto.market import Offer

        if self.cost_model == "polynomial":
            # Convert polynomials to piece-wise linear.
            self.poly_to_pwl(n_points=6)

        n_segments = len(self.pwl_points) - 1

        offers = []

        for i in range(n_segments):
            x1, y1 = self.pwl_points[i]
            x2, y2 = self.pwl_points[(i + 1)]

            quantity = x2 - x1
            price = (y2 - y1) / quantity

            offers.append(Offer(quantity, price))

        return offers


    def offers_to_pwl(self, offers, is_bid=False, limits=None):
        """ Sets the piecewise linear total cost function according to the
            given bid/offer blocks.

            @see: extras/smartmarket/off2case.m
        """
        from numpy import cumsum

        if min([off.quantity for off in offers]) < 0.0:
            logger.error("Offer/bid quantities must be non-negative.")

        # Strip zero quantities and optionally strip prices beyond limits.
        if limits is not None:
            if is_bid:
                offers = [off for off in offers if off.quantity >= limit]
                offers = [off for off in offers if off.price >= limit]
            else:
                offers = [off for off in offers if off.quantity <= limit]
                offers = [off for off in offers if off.price <= limit]

        n_points = len(offers) + 1 # Number of points to define pwl function.

        points = [(0.0, 0.0)]
        # Form piece-wise linear total cost function.
        for i, off in enumerate(offers):
            x = points[i][0] + off.quantity
            y = points[i][1] + off.price
            points.append((x, y))

        if is_bid:
            x_end = points[-1][0]
            y_end = points[-1][1]
            points = [(pnt[0] - x_end, pnt[1] - y_end) for pnt in points]

        self.pwl_points = points

        self.cost_model = "piecewise linear"


class Load(object):
    """ Defines a PQ load component.
    """

    def __init__(self, name="load", online=True, p=1.0, q=0.1, p_max=1.0,
            p_min=0.0, p_profile=None):
        """ Initialises a new Load instance.
        """
        self.name = name
        # Is the load in service?
        self.online = online
        # Active power demand (MW).
        self.p = p
        # Reactive power demand (MVAr).
        self.q = q
        # Maximum active power (MW).
        self.p_max = p_max
        # Minimum active power (MW).
        self.p_min = p_min

        self._p_profile = []
        # Active power profile (%).
        if p_profile is None:
            self.p_profile = [100.0]
        else:
            self.p_profile = p_profile

        self._p_cycle = cycle(self.p_profile)

    @property
    def p_profiled(self):
        """ Active power demand scaled between 'p_max' and 'p_min'
            according to the 'p_profile' percentages.
        """
        percent = self._p_cycle.next()
        return (percent / 100) * (self.p_max - self.p_min)


    def get_p_profile(self):
        """ Returns the active power profile for the load.
        """
        return self._p_profile


    def set_p_profile(self, profile):
        """ Sets the active power profile, updating the cycle iterator.
        """
        self._p_cycle = cycle(profile)
        self._p_profile = profile


    p_profile = property(get_p_profile, set_p_profile)


class NetworkReport(object):
    """ Defines a statistical network report.
    """

    def __init__(self, network):
        """ Initialises a NetworkReport instance.
        """
        self.network = network


    @property
    def n_buses(self):
        """ Total number of buses.
        """
        return len(self.network.buses)


    @property
    def n_connected_buses(self):
        """ Total number of non-islanded buses.
        """
        return len(self.network.connected_buses)


    @property
    def n_generators(self):
        """ Total number of generators.
        """
        return len(self.network.all_generators)


    @property
    def n_online_generators(self):
        """ Total number of generators in service.
        """
        return len(self.network.online_generators)


    @property
    def committed_generators(self):
        """ Generators that have been despatched.
        """
        return [g for g in self.network.all_generators if g.p > 0.0]


    @property
    def n_committed_generators(self):
        """ Number of committed generators.
        """
        return len(self.committed_generators)


    @property
    def n_loads(self):
        """ Total number of loads.
        """
        return len(self.network.all_loads)


    @property
    def n_online_loads(self):
        """ Number of active loads.
        """
        return len(self.network.online_loads)


    @property
    def fixed(self):
        """ Fixed loads.
        """
        return self.network.all_loads


    @property
    def n_fixed(self):
        """ Total number of fixed loads.
        """
        return len(self.fixed)


    @property
    def despatchable(self):
        """ Generators with negative output.
        """
        return [g for g in self.network.all_generators if g.p < 0.0]


    @property
    def n_despatchable(self):
        """ Number of despatchable loads.
        """
        return len(self.despatchable)

    # Branch property getters -------------------------------------------------

    @property
    def n_branches(self):
        """ Total number of branches.
        """
        return len(self.network.branches)


    @property
    def n_online_branches(self):
        """ Total number of active branches.
        """
        return len(self.network.online_branches)


    @property
    def transformers(self):
        """ Branches operating as transformers.
        """
        return [e for e in self.network.branches if e.mode == "transformer"]


    @property
    def n_transformers(self):
        """ Total number of transformers.
        """
        return len(self.transformers)

    # "How much?" property getters --------------------------------------------

    @property
    def total_gen_capacity(self):
        """ Total generation capacity.
        """
        base_mva = self.network.base_mva
        p = sum([g.p for g in self.network.all_generators])
        q = sum([g.q for g in self.network.all_generators])

        return complex(p, q)


    @property
    def online_capacity(self):
        """ Total online generation capacity.
        """
        p = sum([g.p for g in self.network.online_generators])
        q = sum([g.q for g in self.network.online_generators])

        return complex(p, q)


    @property
    def generation_actual(self):
        """ Total despatched generation.
        """
        p = sum([g.p for g in self.network.all_generators])
        q = sum([g.q for g in self.network.all_generators])

        return complex(p, q)


    @property
    def load(self):
        """ Total system load.
        """
        p = sum([l.p for l in self.network.all_loads])
        q = sum([l.q for l in self.network.all_loads])

        return complex(p, q)


    @property
    def fixed_load(self):
        """ Total fixed system load.
        """
        p = sum([l.p for l in self.fixed])
        q = sum([l.q for l in self.fixed])

        return complex(p, q)


    @property
    def despatchable_load(self):
        """ Total volume of despatchable load.
        """
        p = sum([l.p for l in self.despatchable])
        q = sum([l.q for l in self.despatchable])

        return complex(p, q)


#    @property
#    def shunt_injection(self):
#        """ Total system shunt injection.
#        """
#        return 0.0 + 0.0j # FIXME: Implement shunts


    @property
    def losses(self):
        """ Total system losses.
        """
        p = sum([e.p_losses for e in self.network.branches])
        q = sum([e.q_losses for e in self.network.branches])

        return complex(p, q)


    @property
    def branch_charging(self):
        """ Total branch charging injections.
        """
        return 0.0 + 0.0j # FIXME: Calculate branch charging injections


#    @property
#    def total_inter_tie_flow(self):
#        """ Total inter-tie flow.
#        """
#        return 0.0 + 0.0j # FIXME: Implement inter-ties


    @property
    def min_voltage_amplitude(self):
        """ Minimum bus voltage amplitude.
        """
        if self.network.buses:
#            l.index(min(l))
            return min([bus.v_magnitude for bus in self.network.buses])
        else:
            return 0.0


    @property
    def max_voltage_amplitude(self):
        """ Maximum bus voltage amplitude.
        """
        if self.network.buses:
            return max([bus.v_magnitude for bus in self.network.buses])
        else:
            return 0.0


    @property
    def min_voltage_phase(self):
        """ Minimum bus voltage phase angle.
        """
        if self.network.buses:
            return min([bus.v_angle for bus in self.network.buses])
        else:
            return 0.0


    @property
    def max_voltage_phase(self):
        """ Maximum bus voltage phase angle.
        """
        if self.network.buses:
            return max([bus.v_angle for bus in self.network.buses])
        else:
            return 0.0


    @property
    def min_p_lambda(self):
        """ Minimum bus active power Lagrangian multiplier.
        """
        if self.network.buses:
            return min([v.p_lambda for v in self.network.buses])
        else:
            return 0.0


    @property
    def max_p_lambda(self):
        """ Maximum bus active power Lagrangian multiplier.
        """
        if self.network.buses:
            return max([v.p_lambda for v in self.network.buses])
        else:
            return 0.0


    @property
    def min_q_lambda(self):
        """ Minimum bus reactive power Lagrangian multiplier.
        """
        if self.network.buses:
            return min([v.q_lambda for v in self.network.buses])
        else:
            return 0.0


    @property
    def max_q_lambda(self):
        """ Maximum bus reactive power Lagrangian multiplier.
        """
        if self.network.buses:
            return max([v.q_lambda for v in self.network.buses])
        else:
            return 0.0

# EOF -------------------------------------------------------------------------
