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

""" Defines a pure Python implementation of the Pylon object model.
"""

from itertools import cycle


class Network:
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
        """ Bus mode may be PV, PQ or Slack.
        """
        if self.slack:
            return "Slack"
        elif self.generators:
            for g in self.generators:
                if g.q_limited:
                    return "PQ"
            return "PV"
        else:
            return "PQ"

    # Base voltage
    v_base = 100.0

    # Voltage amplitude initial guess.
    v_amplitude_guess = 1.0

    # Voltage phase angle initial guess.
    v_phase_guess = 1.0

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


class Branch:
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
        """ Branch mode may be 'Line' or 'Transformer'.
        """
        if self.source_bus.v_amplitude == self.target_bus.v_amplitude:
            return "Line"
        else:
            return "Transformer"

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

    def __init__(self, source_bus, target_bus):
        assert isinstance(source_bus, Bus)
        assert isinstance(target_bus, Bus)

        self.source_bus = source_bus
        self.target_bus = target_bus

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
    v_amplitude = 1.0

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
    cost_model = 'Polynomial'

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

# EOF -------------------------------------------------------------------------
