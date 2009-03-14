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

""" This module is responsible for modeling the energy consumers and the system
    load as curves and associated curve data. Special circumstances that may
    affect the load, such as seasons and daytypes, are also included here.

    This information is used by Load Forecasting and Load Management.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    HasTraits, String, Int, Float, List, Trait, Instance, Bool, Range, \
    Property, Enum, Any, Delegate, Tuple, Array, Disallow, cached_property

from CIM13.Core import Curve, ConductingEquipment

SynchronousMachineOperatingMode = Enum("generator", "condenser")

SynchronousMachineType = Enum("generatorcondenser", "condenser", "generator")

#------------------------------------------------------------------------------
#  "EnergyConsumer" class:
#------------------------------------------------------------------------------

class EnergyConsumer(ConductingEquipment):
    """ Generic user of energy - a point of consumption on the power system
        model.
    """

    # Number of individual customers represented by this Demand.
    customerCount = Int(desc="number of individual customers represented "
        "by this demand")

#------------------------------------------------------------------------------
#  "RegulatingCondEq" class:
#------------------------------------------------------------------------------

class RegulatingCondEq(ConductingEquipment):
    """ RegulatingCondEq is a type of ConductingEquipment that can regulate
        Measurements and have a RegulationSchedule.
    """

#    RegulatingControl = Instance("RegulatingControl")

    # The association gives the control output that is used to actually govern
    # a regulating device, e.g. the magnetization of a synchronous machine or
    # capacitor bank breaker actuators.
#    Controls = List(Instance("Control"))

#------------------------------------------------------------------------------
#  "SynchronousMachine" class:
#------------------------------------------------------------------------------

class SynchronousMachine(RegulatingCondEq):
    """ An electromechanical device that operates synchronously with the
        network. It is a single machine operating either as a generator or
        synchronous condenser or pump.
    """

    # A synchronous machine may operate as a generator and as such becomes a
    # member of a generating unit
    MemberOf_GeneratingUnit = Instance("GeneratingUnit")

    ReactiveCapabilityCurves = List(Instance("ReactiveCapabilityCurve"))

    # Defines the default MVArCapabilityCurve for use by a SynchronousMachine.
    InitialReactiveCapabilityCurve = Instance("ReactiveCapabilityCurve")

#    DrivenBy_PrimeMover = Instance("PrimeMover")

    # Maximum reactive power limit. This is the maximum (nameplate) limit for
    # the unit.
    maxQ = Float

    # Current mode of operation.
#    operatingMode = SynchronousMachineOperatingMode

    # Minimum reactive power limit for the unit.
    minQ = Float

    # Zero sequence reactance of the synchronous machine.
    x0 = Float

    # Maximum voltage limit for the unit.
    maxU = Float

    # Negative sequence resistance.
    r2 = Float

    # Positive sequence reactance of the synchronous machine.
    x = Float

    # Minimum voltage  limit for the unit.
    minU = Float

    # The energy stored in the rotor when operating at rated speed. This value
    # is used in the accelerating power reference frame for  operator training
    # simulator solutions.
    inertia = Float

    # Positive sequence resistance of the synchronous machine.
    r = Float

    # Nameplate apparent power rating for the unit
    ratedS = Float

    # Active power consumed when in condenser mode operation.
    condenserP = Float

    # Default base reactive power value. This value represents the initial
    # reactive power that can be used by any application function.
    baseQ = Float

    # Zero sequence resistance of the synchronous machine.
    r0 = Float

    # Priority of unit for reference bus selection. 0 = don t care (default)
    # 1 = highest priority. 2 is less than 1 and so on.
    referencePriority = Int(desc="priority of unit for reference bus "
        "selection")

    # Negative sequence reactance.
    x2 = Float

    # Modes that this synchronous machine can operate in.
    type = SynchronousMachineType

#------------------------------------------------------------------------------
#  "ReactiveCapabilityCurve" class:
#------------------------------------------------------------------------------

class ReactiveCapabilityCurve(Curve):
    """ Reactive power rating envelope versus the synchronous machine's active
        power, in both the generating and motoring modes. For each active power
        value there is a corresponding high and low reactive power limit
        value. Typically there will be a separate curve for each coolant
        condition, such as hydrogen pressure.  The Y1 axis values represent
        reactive minimum and the Y2 axis values represent reactive maximum.
    """

    SynchronousMachines = List(Instance(SynchronousMachine))

    # Defines the default MVArCapabilityCurve for use by a SynchronousMachine.
    InitiallyUsedBySynchronousMachine = List(Instance(SynchronousMachine))

#------------------------------------------------------------------------------
#  "Conductor" class:
#------------------------------------------------------------------------------

class Conductor(ConductingEquipment):
    """ Combination of conducting material with consistent electrical
        characteristics, building a single electrical system, used to carry
        current between points in the power system.
    """

    # Positive sequence series resistance of the entire line section.
    r = Float

    # Positive sequence series reactance of the entire line section.
    x = Float

    # Positive sequence shunt (charging) susceptance, uniformly distributed,
    # of the entire line section.
    bch = Float

    # Positive sequence shunt (charging) conductance, uniformly distributed,
    # of the entire line section.
    gch = Float

    # Zero sequence series resistance of the entire line section.
    r0 = Float

    # Zero sequence series reactance of the entire line section.
    x0 = Float

    # Zero sequence shunt (charging) susceptance, uniformly distributed, of
    # the entire line section.
    b0ch = Float

    # Zero sequence shunt (charging) conductance, uniformly distributed, of
    # the entire line section.
    g0ch = Float

    # Segment length for calculating line section capabilities.
    length = Float

#------------------------------------------------------------------------------
#  "ACLineSegment" class:
#------------------------------------------------------------------------------

class ACLineSegment(Conductor):
    """ A wire or combination of wires, with consistent electrical
        characteristics, building a single electrical system, used to carry
        alternating current between points in the power system.
    """

    pass

#------------------------------------------------------------------------------
#  "Connector" class:
#------------------------------------------------------------------------------

class Connector(ConductingEquipment):
    """ A conductor, or group of conductors, with negligible impedance, that
        serve to connect other conducting equipment within a single substation
        and are modelled with a single logical terminal.
    """

#------------------------------------------------------------------------------
#  "BusbarSection" class:
#------------------------------------------------------------------------------

class BusbarSection(Connector):
    """ A conductor, or group of conductors, with negligible impedance, that
        serve to connect other conducting equipment within a single substation.

        Voltage measurements are typically obtained from VoltageTransformers
        that are connected to busbar sections. A bus bar section may have many
        physical terminals but for analysis is modelled with exactly one
        logical terminal.
    """

    pass

# EOF -------------------------------------------------------------------------
