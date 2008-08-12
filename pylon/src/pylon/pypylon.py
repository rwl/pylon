#------------------------------------------------------------------------------
#  Copyright (c) 2008, Richard W. Lincoln
#
#  This file is part of Pylon.
#
#  Pylon is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 2 of the License, or
#  (at your option) any later version.
#
#  Pylon is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Pylon.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------

""" A Pylon implementation without Enthought dependencies """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import logging
from uuid import uuid4

#------------------------------------------------------------------------------
#  "Network" class:
#------------------------------------------------------------------------------

class Network:
    """ Electric power system network model """

    # Human-readable identifier
    name = "network"
    # Base apparent power (MVA)
    base_mva = 0.0
    # Nodes of the network graph
    buses = []
    # Arcs of the network graph
    branches = []

    def _get_n_buses(self):
        """ Property getter """
        return len(self.buses)

    # Total number of buses
    n_buses = property(_get_n_buses)

    def _get_bus_names(self):
        """ Property getter """

        return [bus.name for bus in self.buses]

    # The names of all buses
    bus_names = property(_get_bus_names)

    def _get_n_branches(self):
        """ Property getter """
        return len(self.branches)

    # Total number of branches
    n_branches = property(_get_n_branches)

    def _get_branch_names(self):
        """ Property getter """

        return [e.name for e in self.branches]

    branch_names = property(_get_branch_names)

    def add_branch(self, branch):
        """ Adds a Branch object """

        if len(self.buses) < 2:
            logger.error("For Branch addition two or more buses are requisite")
        elif branch.source_bus not in self.buses:
            raise ValueError, "source bus not present in model"
        elif branch.target_bus not in self.buses:
            raise ValueError, "destination bus not found in model"
        else:
            self.branches.append(branch)

#------------------------------------------------------------------------------
#  "Bus" class:
#------------------------------------------------------------------------------

class Bus(object):
    """ Power system node """

    # Human-readable identifier
    name = "bus"
    # Unique identifier
    id = ""
    # Active electricity production
    generators = []
    # Passive electricity consumption
    loads = []
    # Is the bus the reference/slack/swing bus?
    slack = False
    # Base voltage
    v_base = 400.0
    # Voltage amplitude initial guess
    v_amplitude_guess = 1.0
    # Voltage phase initial guess
    v_phase_guess = 1.0
    # Maximum voltage amplitude (pu)
    v_max = 1.1
    # Minimum voltage amplitude (pu)
    v_min = 0.9
    # Shunt conductance
    g_shunt = 0.0
    # Shunt susceptance
    b_shunt = 0.0

    def __init__(self, *args, **kw):
        """ Returns a new Bus object """

        self.id = uuid4().hex[:6]

        super(Bus, self).__init__(*args, **kw)

#------------------------------------------------------------------------------
#  "Branch" class:
#------------------------------------------------------------------------------

class Branch(object):
    """ Power system line/cable/transformer """

    # Human-readable identifier
    name = "branch"
    # Unique identifier
    id = ""
    # Source bus
    source_bus = None
    # Target bus
    target_bus = None
    # Connection status
    in_service = True
    # Positive sequence resistance (pu)
    r = 0.0
    # Positive sequence reactance (pu)
    x = 0.0
    # Total positive sequence line charging susceptance (pu)
    b = 0.0
    # Standard MVA rating (pu)
    s_max = 2.0

    # Transformer off nominal turns ratio
    ratio = 1.0
    # Phase shift angle (degrees)
    phase_shift = 0.0

    def __init__(self, source_bus=None, target_bus=None, *args, **kw):
        """ Returns a new Branch object.

        NB: 'source_bus' and 'target_bus' should really be non-keyword
        arguments, but are not for the sake of the traitsy model.

        """

        if (source_bus is None) or (target_bus is None):
            raise AttributeError, "source and target bus must be specified"

        self.source_bus = source_bus
        self.target_bus = target_bus
        self.id = uuid4().hex[:6]

        super(Branch, self).__init__(*args, **kw)

#------------------------------------------------------------------------------
#  "Generator" class:
#------------------------------------------------------------------------------

class Generator(object):
    """ Fixes voltage magnitude and active power injected at parent bus
    or when at its reactive power limit fixes active and reactive power
    injected at parent bus.

    """

    # Human-readable identifier
    name = "generator"
    # Unique identifier
    id = ""
    # Connection status
    in_service = True
    # Machine MVA base
    base_mva = 100.0
    # Active power output (pu)
    p = 1.0
    # Maximum active power output (pu)
    p_max = 2.0
    # Minimum active power output (pu)
    p_min = 0.0
    # Voltage amplitude setpoint (pu)
    v_amplitude = 1.0
    # Maximum reactive power (pu)
    q_max = 3.0
    # Minimum reactive power (pu)
    q_min = -3.0
    # Is the machine at the limit of reactive power?
    q_limited = False

    # Start up cost (GBP)
    cost_startup = 0.0
    # Shut down cost (GBP)
    cost_shutdown = 0.0
    # Polynomial cost curve coefficients
    cost_coeffs = (1.0, 0.1, 0.01)
    # Piecewise linear cost segment points
    pwl_points = [(0.0, 0.0), (1.0, 1.0)]

    def __init__(self, *args, **kw):
        """ Return a new Generator obejct """

        self.id = uuid4().hex[:6]

        super(Generator, self).__init__(*args, **kw)

#------------------------------------------------------------------------------
#  "Load" class:
#------------------------------------------------------------------------------

class Load(object):
    """ PQ """

    # Human-readable identifier
    name = "load"
    # Unique identifier
    id = ""
    # Connection status
    in_service = True
    # Active power demand (pu)
    p = 1.0
    # Reactive power demand (pu)
    q = 0.1

    def __init__(self, *args, **kw):
        """ Returns a new Load object """

        self.id = uuid4().hex[:6]

        super(Load, self).__init__(*args, **kw)


# EOF -------------------------------------------------------------------------
