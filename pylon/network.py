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
    # Human-readable identifier.
    name = "network"

    # Base apparent power (MVA).
    base_mva = 100.0

    # Nodes of the network graph.
    buses = []

    @property
    def connected_buses(self):
        """ Property getter. Returns a list of buses that are connected
            to one or more branches.
        """
        source_buses = [e.source_bus for e in self.branches]
        target_buses = [e.target_bus for e in self.branches]

        return [v for v in self.buses if v in source_buses + target_buses]

    @property
    def slack_model(self):
        """ Slack/swing/reference bus model.
        """
        slackers = [v for v in self.buses if v.slack]
        if slackers:
            return "Single"
        else:
            return "Distributed"

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

    # Arcs of the network graph.
    branches = []

    @property
    def online_branches(self):
        """ Property getter for in-service branches.
        """
        return [branch for branch in self.branches if branch.online]


    def __init__(self, base_mva=100.0, buses=[], branches=[]):
        """ Initialises a new Network instance.
        """
        self.base_mva = base_mva
        self.buses = buses
        self.branches = branches


class Bus(object):
    """ Defines a power system bus node.
    """
    # Human readable identifier.
    name = "bus"

    # Generators defined by their active power and voltage.
    generators = []

    # Loads that specify real and reactive power demand.
    loads = []

    # Is the bus a reference/slack/swing bus?
    slack = False

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

    # Base voltage
    v_base = 100.0

    # Voltage amplitude initial guess.
    v_magnitude_guess = 1.0

    # Voltage angle initial guess.
    v_angle_guess = 1.0

    # Maximum voltage amplitude (pu).
    v_max = 1.1

    # Minimum voltage amplitude (pu).
    v_min = 0.9

    # Shunt conductance.
    g_shunt = 0.0

    # Shunt susceptance.
    b_shunt = 0.0

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

    def __init__(self, name="bus", generators=[], loads=[], slack=False,
                                                         v_base=100.0,
                                                         v_magnitude_guess=1.0,
                                                         v_angle_guess=1.0,
                                                         v_max=1.1,
                                                         v_min=0.9,
                                                         g_shunt=0.0,
                                                         b_shunt=0.0):
        """ Initialises a new Bus instance.
        """
        self.name = name
        self.generators = generators
        self.loads = loads
        self.slack = slack
        self.v_base = v_base
        self.v_magnitude_guess = v_magnitude_guess
        self.v_angle_guess = v_angle_guess
        self.v_max = v_max
        self.v_min = v_min
        self.g_shunt = g_shunt
        self.b_shunt = b_shunt


class Branch(object):
    """ Defines a network edge that links two Bus objects.
    """
    # Human readable identifier
    name = "branch"

    # Is the branch in service?
    online = True

    # Source/from/start bus.
    source_bus = None

#    @property
#    def source_bus_idx(self):
#        """ Index of the source bus in the list of all buses.
#        """
#        return self.buses.index(self.source_bus)

    # Target/to/end bus.
    target_bus = None

#    @property
#    def target_bus_idx(self):
#        """ Index of the target bus in the list of all buses.
#        """
#        return self.buses.index(self.source_bus)

    @property
    def mode(self):
        """ Branch mode may be 'line' or 'transformer'.
        """
        if self.source_bus.v_magnitude == self.target_bus.v_magnitude:
            return "line"
        else:
            return "transformer"

    # Positive sequence resistance (pu).
    r = 0.001

    # Positive sequence reactance (pu).
    x = 0.001

    # Total positive sequence line charging susceptance (pu).
    b = 0.001

    # General purpose maximum MVA rating (pu).
    s_max = 2.0

    # Transformer off nominal turns ratio.
    ratio = 1.0

    # Phase shift angle (degrees).
    phase_shift = 0.0

    # Power flow results ------------------------------------------------------

    # Active power injected at the source bus.
    p_source = 0.0

    # Active power injected at the target bus.
    p_target = 0.0

    # Reactive power injected at the source bus.
    q_source = 0.0

    # Reactive power injected at the target bus.
    q_target = 0.0

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

    # |S_source| mu
    mu_s_source = 0.0

    # |S_target| mu
    mu_s_target = 0.0

    def __init__(self, source_bus, target_bus, name="branch",
                                               online=True,
                                               r=0.001,
                                               x=0.001,
                                               b=0.001,
                                               s_max=2.0,
                                               ratio=1.0,
                                               phase_shift=0.0):
        """ Initialises a new Branch instance.
        """
        assert isinstance(source_bus, Bus)
        assert isinstance(target_bus, Bus)

        self.source_bus = source_bus
        self.target_bus = target_bus
        self.name = name
        self.online = online
        self.r = r
        self.x = x
        self.b = b
        self.s_max = s_max
        self.ratio = ratio
        self.phase_shift = phase_shift

#------------------------------------------------------------------------------
#  "Generator" class:
#------------------------------------------------------------------------------

class Generator(object):
    """ Defines a power system generator component. Fixes voltage magnitude
        and active power injected at parent bus. Or when at it's reactive
        power limit fixes active and reactive power injected at parent bus.
    """
    # Human readable identifier.
    name = "generator"

    # Is the generator in service.
    online = True

    # Machine MVA base.
    base_mva = 100.0

    # Active power output (pu).
    p = 1.0

    # Maximum active power output (pu).
    p_max = 2.0

    # Minimum active power output (pu).
    p_min = 0.0

    # Voltage amplitude setpoint (pu).
    v_magnitude = 1.0

    # Reactive power output.
    q = 0.0

    # Maximum reactive power (pu).
    q_max = 3.0

    # Minimum reactive power (pu).
    q_min = -3.0

    @property
    def q_limited(self):
        """ Is the machine at it's limit of reactive power?
        """
        if (self.q >= self.q_max) or (self.q <= self.q_min):
            return True
        else:
            return False

    # The output power that the Generator is despatched to generate
    # as a result of solving the OPF problem.
    p_despatch = 0.0

    # Maximum active power output bid. Used in OPF routines. Should be less
    # than or equal to p_max.
    p_max_bid = 2.0

    # Minimum active power bid. Used in OPF routines. Should be greater than
    # or equal to p_min.
    p_min_bid = 0.0

    # Start up cost.
    c_startup = 0.0

    # Shut down cost.
    c_shutdown = 0.0

    # Valid values are 'Polynomial' and 'Piecewise Linear'.
    cost_model = 'polynomial'

    # Polynomial cost curve coefficients.
    cost_coeffs = (1.0, 0.1, 0.01)

    # Piecewise linear cost segment points
    pwl_points = [(0.0, 0.0), (1.0, 1.0)]

    @property
    def p_cost(self):
        """ Active power cost at the current output.
        """
        if self.cost_model == "Polynomial":
            x = self.p
            c0, c1, c2 = self.cost_coeffs
            return c0 + c1*x + c2*x**2
        else:
            raise NotImplementedError

    # Ramp up rate (p.u./h).
    rate_up = 1.0

    # Ramp down rate (p.u./h).
    rate_down = 1.0

    # Minimum running time (h).
    min_up = 0

    # Minimum shut down time (h).
    min_down = 0

    # Initial number of periods up.
    initial_up = 1

    # Initial number of periods down.
    initial_down = 0

    def __init__(self, name="generator", online=True,
                                         base_mva=100.0,
                                         p=1.0,
                                         p_max=2.0,
                                         p_min=0.0,
                                         v_magnitude=1.0,
                                         q=0.0,
                                         q_max=3.0,
                                         q_min=-3.0,
                                         p_max_bid=2.0,
                                         p_min_bid=0.0,
                                         c_startup=0.0,
                                         c_shutdown=0.0,
                                         cost_model="polynomial",
                                         cost_coeffs=(1.0, 0.1, 0.01),
                                         rate_up=1.0,
                                         rate_down=1.0,
                                         min_up=0,
                                         min_down=0,
                                         initial_up=1,
                                         initial_down=0):
        """ Initialises a new Generator instance.
        """
        self.name = name
        self.online = online
        self.base_mva = base_mva
        self.p = p
        self.p_max = p_max
        self.p_min = p_min
        self.v_magnitude = v_magnitude
        self.q = q
        self.q_max = q_max
        self.q_min = q_min
        self.p_max_bid = p_max_bid
        self.p_min_bid = p_min_bid
        self.c_startup = c_startup
        self.c_shutdown = c_shutdown
        self.cost_model = cost_model
        self.cost_coeffs = cost_coeffs
        self.rate_up = rate_up
        self.rate_down = rate_down
        self.min_up = min_up
        self.min_down = min_down
        self.initial_up = initial_up
        self.initial_down = initial_down


class Load(object):
    """ Defines a PQ load component.
    """
    # Human readable identifier.
    name = "load"

    # Is the load in service?
    online = True

    # Active power demand (pu).
    p = 1.0

    # Reactive power demand (pu).
    q = 0.1

    # Maximum active power (p.u.).
    p_max = 1.0

    # Minimum active power (p.u.).
    p_min = 0.0

    # Active power profile (%).
    p_profile = [100.0]

    _p_cycle = cycle

    @property
    def p_profiled(self):
        """ Active power demand scaled between 'p_max' and 'p_min'
            according to the 'p_profile' percentages.
        """
        percent = self._p_cycle.next()
        return (percent / 100) * (self.p_max - self.p_min)

    def __init__(self):
        self._p_cycle = cycle(self.p_profile)


    def set_p_profile(self, profile):
        """ Sets the active power profile, updating the cycle iterator.
        """
        self._p_cycle = cycle(profile)
        self.p_profile = profile

    def __init__(self, name="load", online=True, p=1.0,
                                                 q=0.1,
                                                 p_max=1.0,
                                                 p_min=0.0,
                                                 p_profile=[100.0]):
        """ Initialises a new Load instance.
        """
        self.name = name
        self.online = online
        self.p = p
        self.q = q
        self.p_max = p_max
        self.p_min = p_min
        self.p_profile = p_profile


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

        return complex(p * base_mva, q * base_mva)


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
        p = sum([g.p_despatch for g in self.network.all_generators])
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
