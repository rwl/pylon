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

""" Power system bus component """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import uuid

from enthought.traits.api import \
    HasTraits, String, Int, Float, List, Trait, Instance, Delegate, Event, \
    Array, Bool, Range, Default, Property, Enum, Complex, cached_property

from pylon.ui.bus_view import bus_view

from generator import Generator

from load import Load

#------------------------------------------------------------------------------
#  "Bus" class:
#------------------------------------------------------------------------------

class Bus(HasTraits):
    """ Power system bus component """

    #--------------------------------------------------------------------------
    #  Object views:
    #--------------------------------------------------------------------------

    traits_view = bus_view

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    id = String(desc="unique bus identifier")

    name = String("v", desc="bus name")

#    source_branches = List(
#        Instance("pylon.branch.Branch"),
#        desc="branches sourced from this bus"
#    )
#
#    target_branches = List(
#        Instance("pylon.branch.Branch"),
#        desc="branches targeting this bus"
#    )

    generators = List(
        Generator,
        desc="generators of PV type connected to the bus"
    )

    n_generators = Property(
        Int,
        desc="total number of generators at this bus",
        depends_on=["generators"]
    )

#    has_generation = Property(
#        Bool,
#        desc="true if there is one or more Generator connected to the "
#            "Bus and in-turn allows the Bus to become the slack bus",
#        depends_on=["generators"]
#    )

    loads = List(Load, desc="loads connected to the bus")

    n_loads = Property(
        Int,
        desc="total number of loads at this bus",
        depends_on=["loads"]
    )

    type = Property(
        Enum("PV", "PQ", "Slack", "Isolated"),
        desc="bus type as determined by the connected plant",
        depends_on=["slack", "generators", "loads"]
    )

    q_limited = Bool(
        False,
        desc="true if any connected generators are "
        "at their limits of reactive power"
    )

#    slack = Property(
#        Bool(
#            False,
#            desc="true if the bus is a slack bus",
#            label="Slack bus"
#        )
#    )

    slack = Bool(
        False,
        desc="true if the bus is a slack bus",
        label="Slack bus"
    )

#    v_nominal = Float(
#        400.0,
#        desc="nominal bus voltage (kV)",
#        label="Vnom"
#    )

    # Base voltage (kV)
    v_base = Float(
        400.0,
        desc="base voltage (kV)",
        label="Vbase"
    )

    v_amplitude_guess = Range(
        low=0.5, high=1.5, value=1.0,
        desc="voltage amplitude initial guess (p.u.)",
        label="Vm0"
    )

    # TODO: Implement dynamic phase range (See @BUclass/setup.m)
    # aref = min(abs(a.con(:,4)));
    # alow  = find(a.con(:,4)-aref < -1.5708);
    # ahigh = find(a.con(:,4)-aref >  1.5708);
    v_phase_guess = Float(
        1.0,
        desc="voltage phase initial guess (p.u.)",
        label="Va0"
    )

    v_max = Float(
        1.0,
        desc="maximum voltage amplitude (PQ) (p.u.)",
        label="Vmax"
    )

    v_min = Float(
        1.0,
        desc="minimum voltage amplitude (PQ) (p.u.)",
        label="Vmin"
    )

    v_amplitude = Float(
        style="readonly",
        desc="bus voltage magnitude",
        label="Vm")

    v_phase = Float(
        style="readonly",
        desc="bus voltage angle",
        label="Va"
    )

    g_shunt = Float(
        desc="shunt conductance (p.u. (MW demanded) at V = 1.0 p.u.)",
        label="Gsh"
    )

    b_shunt = Float(
        desc="shunt susceptance (p.u. (MVAr injected) at V = 1.0 p.u.)",
        label="Bsh"
    )

    zone = Int(1, desc="loss zone")

#    q_max = Property(
#        Float,
#        desc="maximum reactive power limit (PV) (p.u.)",
#        depends_on=["generators_items", "generators.q"],
#        label="Qmax"
#    )
#
#    q_min = Property(
#        Float,
#        desc="minimum reactive power limit (PV) (p.u.)",
#        depends_on=["generators_items, generators.q"],
#        label="Qmin"
#    )

    p_supply = Property(
        Float,
        desc="total real power supply (MW)",
        depends_on=["generators.p", "loads.p"],
        label="P (supply)"
    )

    p_demand = Property(
        Float,
        desc="total real power demand (MW)",
        depends_on=["loads", "loads_items"],
        label="P (demand)"
    )

    p_surplus = Property(
        Float,
        desc="local real power supply and demand difference",
        depends_on=["p_supply", "p_demand"],
        label="P (surplus)"
    )

    q_supply = Property(
        Float,
        desc="total reactive power supply (MVAr)",
        depends_on=["generators.q", "loads.q"],
        label="Q (supply)"
    )

    q_demand = Property(
        Float,
        desc="total reactive power demand (MVAr)",
        depends_on=["loads", "loads_items"],
        label="Q (demand)"
    )

    q_surplus = Property(
        Float,
        desc="local reactive power supply and demand difference",
        depends_on=["q_supply", "q_demand"],
        label="Q (surplus)"
    )

    #--------------------------------------------------------------------------
    #  Text representation of the Bus:
    #--------------------------------------------------------------------------

#    def __str__(self):
#        """ Text representation of the Bus """
#
#        return self.name

    #--------------------------------------------------------------------------
    #  Generate unique identifier:
    #--------------------------------------------------------------------------

    def _id_default(self):
        """ Unique identifier initialiser """

        return self.name + "-#" + uuid.uuid4().hex[:6]

    #--------------------------------------------------------------------------
    #  Suppress any attempt to make the Bus slack if there is no generation
    #  attached
    #--------------------------------------------------------------------------

#    def _set_slack(self, value):
#        if value is True:
#            if self.n_generators == 0:
#                print "Bus can not be made slack - no generation"
#                return False
#            else:
#                return True
#        else:
#            return False
#
#
#    @cached_property
#    def _get_slack(self):
#        return self.slack


#    def _slack_changed(self, new):
#        if new is True:
#            if self.n_generators == 0:
#                print "Bus can not be made slack - no generation"
#                self.slack = False


    def _get_n_generators(self):
        """ Property getter """

        return len(self.generators)


    def _get_n_loads(self):
        """ Property getter """

        return len(self.loads)

    #--------------------------------------------------------------------------
    #  Maintain an indication of any connected generators being at the reactive
    #  power limit:
    #--------------------------------------------------------------------------

    def _q_limited_changed_for_generators(self, obj, name, old, new):
        print "Q-limited changed", obj, name, old, new
        limited_generators = [g for g in self.generators if g.q_limited]
        if len(limited_generators) > 0: self.q_limited = True
        else: self.q_limited = False

    #--------------------------------------------------------------------------
    #  Maintain an indicator of the mode in which the bus is:
    #--------------------------------------------------------------------------

    def _get_type(self):
        if self.slack:
            return "Slack"
        elif len(self.generators) > 0 and not self.q_limited:
            return "PV"
        else:
            return "PQ"


    def _get_p_supply(self):
        p_supply = 0

        for g in self.generators:
            p_supply += g.p

        return p_supply


    def _get_p_demand(self):
        p_demand = 0

        for l in self.loads:
            p_demand += l.p

        return p_demand


    def _get_p_surplus(self):
        return self.p_supply - self.p_demand


    def _get_q_supply(self):
        q_supply = 0

        for g in self.generators:
            q_supply += g.q

        return q_supply


    def _get_q_demand(self):
        q_demand = 0

        for l in self.loads:
            q_demand += l.q

        return q_demand


    def _get_q_surplus(self):
        return self.q_supply - self.q_demand

    #--------------------------------------------------------------------------
    #  Public interface:
    #--------------------------------------------------------------------------

    def add_generator(self, g):
        self.generators.append(g)


    def add_load(self, l):
        self.loads.append(l)

# EOF -------------------------------------------------------------------------
