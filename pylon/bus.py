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

""" Power system bus component.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    HasTraits, String, Int, Float, List, Instance, Delegate, Event, \
    Bool, Range, Disallow, Property, Enum, Complex, cached_property

from pylon.ui.bus_view import bus_view

from generator import Generator
from load import Load

#------------------------------------------------------------------------------
#  "Bus" class:
#------------------------------------------------------------------------------

class Bus(HasTraits):
    """ Power system bus component.
    """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # Deprecated identifier.
    id = Disallow

    # Human readable identifier.
    name = String("v", desc="bus name")

    # Generators that specify active power and voltage.
    generators = List(Instance(Generator),
        desc="generators of PV type connected to the bus")

    # Loads that specify active and reactive power demand.
    loads = List(Instance(Load), desc="loads connected to the bus")

    # Bus mode. Possible values are: PV, PQ, Slack and Isolated.
    mode = Property(Enum("PV", "PQ", "Slack", "Isolated"),
        desc="bus type as determined by the connected plant",
        depends_on=["slack", "generators", "loads"])

    # Are any generators at their reactive power limit?
    q_limited = Bool(False, desc="true if any connected generators are "
        "at their limits of reactive power")

    # Is the bus a reference bus that is despatched to make up any slack?
    slack = Bool(False, desc="is the bus slack", label="Slack bus")

    # Nominal bus voltage.
#    v_nominal = Float(400.0, desc="nominal bus voltage (kV)", label="Vnom")

    # Base voltage (kV), defaults to the system base.
    v_base = Float(100.0, desc="base voltage (kV)", label="Vbase")

    # Voltage amplitude initial guess.
    v_amplitude_guess = Range(low=0.5, high=1.5, value=1.0,
        desc="voltage amplitude initial guess (p.u.)",
        label="Vm0")

    # TODO: Implement dynamic phase range (See @BUclass/setup.m)
    # aref = min(abs(a.con(:,4)));
    # alow  = find(a.con(:,4)-aref < -1.5708);
    # ahigh = find(a.con(:,4)-aref >  1.5708);
    # Voltage phase angle initial guess.
    v_phase_guess = Float(1.0, desc="voltage phase initial guess (p.u.)",
        label="Va0")

    # Maximum voltage amplitude.
    v_max = Float(1.5, desc="maximum voltage amplitude (PQ) (p.u.)",
        label="Vmax")

    # Minimum voltage amplitude.
    v_min = Float(0.5, desc="minimum voltage amplitude (PQ) (p.u.)",
        label="Vmin")

    # Actual bus voltage amplitude.
    v_amplitude = Float(style="readonly", desc="bus voltage magnitude",
        label="Vm")

    # Actual bus voltage phase amplitude.
    v_phase = Float(style="readonly", desc="bus voltage angle", label="Va")

    # Shunt conductance (p.u. (MW demanded) at V=1.0 pu).
    g_shunt = Float(desc="shunt conductance (p.u. (MW demanded) at V=1.0 pu)",
        label="Gsh")

    # Shunt susceptance (p.u. (MVAr injected) @ V=1.0 pu).
    b_shunt = Float(desc="shunt susceptance (p.u. (MVAr injected) @ V=1.0 pu)",
        label="Bsh")

    # Loss zone.
#    zone = Int(1, desc="loss zone")

    # Total real power supply (MW).
    p_supply = Property(Float, desc="total real power supply (MW)",
        depends_on=["generators.p", "loads.p"], label="P (supply)")

    # Total real power demand (MW).
    p_demand = Property(Float, desc="total real power demand (MW)",
        depends_on=["loads", "loads_items"], label="P (demand)")

    # Local real power difference.
    p_surplus = Property(Float, desc="local real power difference",
        depends_on=["p_supply", "p_demand"], label="P (surplus)")

    # Total reactive power supply (MVAr).
    q_supply = Property(Float, desc="total reactive power supply (MVAr)",
        depends_on=["generators.q", "loads.q"], label="Q (supply)")

    # Total reactive power demand (MVAr).
    q_demand = Property(Float, desc="total reactive power demand (MVAr)",
        depends_on=["loads", "loads_items"], label="Q (demand)")

    # Local reactive power difference.
    q_surplus = Property(Float, desc="local reactive power difference",
        depends_on=["q_supply", "q_demand"], label="Q (surplus)")

    # Lambda's and mu's
    p_lambda = Float(style="readonly", desc="Lambda (GBP/MWh)")

    q_lambda = Float(style="readonly", desc="Lambda (GBP/MVAr-hr)")

    mu_v_min = Float(style="readonly")

    mu_v_max = Float(style="readonly")

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = bus_view

    #--------------------------------------------------------------------------
    #  Indicate if the bus is at its reactive power limit:
    #--------------------------------------------------------------------------

    def _q_limited_changed_for_generators(self, obj, name, old, new):
        """ Indicates if any generators are at their reactive power limit.
        """
        limited_generators = [g for g in self.generators if g.q_limited]

        if len(limited_generators) > 0:
            self.q_limited = True
        else:
            self.q_limited = False

    #--------------------------------------------------------------------------
    #  Maintain an indicator of the mode in which the bus is:
    #--------------------------------------------------------------------------

    def _get_mode(self):
        """ Property getter.

            TODO: Implement 'Isolated' mode.
        """
        if self.slack:
            return "Slack"
        elif (len(self.generators) > 0) and (not self.q_limited):
            return "PV"
        else:
            return "PQ"

    #--------------------------------------------------------------------------
    #  Power property getters:
    #--------------------------------------------------------------------------

    def _get_p_supply(self):
        """ Property getter.
        """
        return sum([g.p for g in self.generators])


    def _get_p_demand(self):
        """ Property getter.
        """
        return sum([l.p for l in self.loads])


    def _get_p_surplus(self):
        """ Property getter.
        """
        return self.p_supply - self.p_demand


    def _get_q_supply(self):
        """ Property getter.
        """
        return sum([g.q for g in self.generators])


    def _get_q_demand(self):
        """ Property getter """

        return sum([l.q for l in self.loads])


    def _get_q_surplus(self):
        """ Property getter.
        """
        return self.q_supply - self.q_demand

# EOF -------------------------------------------------------------------------
