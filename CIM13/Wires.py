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

""" An extension to the Core and Topology package that models information on
    the electrical characteristics of Transmission and Distribution networks.

    This package is used by network applications such as State Estimation,
    Load Flow and Optimal Power Flow.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    HasTraits, String, Int, Float, List, Trait, Instance, Bool, Range, \
    Property, Enum, Any, Delegate, Tuple, Array, Disallow, cached_property

from CIM13.Core import Curve, Equipment, ConductingEquipment, PhaseCode

#------------------------------------------------------------------------------
#  Trait definitions:
#------------------------------------------------------------------------------

SynchronousMachineOperatingMode = Enum("generator", "condenser")

SynchronousMachineType = Enum("generatorcondenser", "condenser", "generator")

ConnectionType = Enum("D", "Z", "Y")

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
    MemberOf_GeneratingUnit = Instance("GeneratingUnit",
        opposite="Contains_SynchronousMachines")

    ReactiveCapabilityCurves = List(Instance("ReactiveCapabilityCurve"),
        opposite="SynchronousMachines")

    # Defines the default MVArCapabilityCurve for use by a SynchronousMachine.
    InitialReactiveCapabilityCurve = Instance("ReactiveCapabilityCurve",
        opposite="InitiallyUsedBySynchronousMachine")

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

    SynchronousMachines = List(Instance(SynchronousMachine),
        opposite="ReactiveCapabilityCurves")

    # Defines the default MVArCapabilityCurve for use by a SynchronousMachine.
    InitiallyUsedBySynchronousMachine = List(Instance(SynchronousMachine),
        opposite="InitialReactiveCapabilityCurve")

#------------------------------------------------------------------------------
#  "Conductor" class:
#------------------------------------------------------------------------------

class Conductor(ConductingEquipment):
    """ Combination of conducting material with consistent electrical
        characteristics, building a single electrical system, used to carry
        current between points in the power system.
    """

    # Positive sequence series resistance of the entire line section.
    r = Float(desc="positive sequence series resistance")

    # Positive sequence series reactance of the entire line section.
    x = Float(desc="positive sequence series reactance")

    # Positive sequence shunt (charging) susceptance, uniformly distributed,
    # of the entire line section.
    bch = Float(desc="positive sequence shunt (charging) susceptance")

    # Positive sequence shunt (charging) conductance, uniformly distributed,
    # of the entire line section.
    gch = Float(desc="positive sequence shunt (charging) conductance")

    # Zero sequence series resistance of the entire line section.
    r0 = Float(desc="zero sequence series resistance")

    # Zero sequence series reactance of the entire line section.
    x0 = Float(desc="zero sequence series reactance")

    # Zero sequence shunt (charging) susceptance, uniformly distributed, of
    # the entire line section.
    b0ch = Float(desc="zero sequence shunt (charging) susceptance")

    # Zero sequence shunt (charging) conductance, uniformly distributed, of
    # the entire line section.
    g0ch = Float(desc="zero sequence shunt (charging) conductance")

    # Segment length for calculating line section capabilities.
    length = Float(desc="segment length")

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

#------------------------------------------------------------------------------
#  "PowerTransformer" class:
#------------------------------------------------------------------------------

class PowerTransformer(Equipment):
    """ An electrical device consisting of two or more coupled windings, with
        or without a magnetic core, for introducing mutual coupling between
        electric circuits. Transformers can be used to control voltage and
        phase shift (active power flow).
    """

    # A transformer has windings.
    Contains_TransformerWindings = List(Instance("TransformerWinding"),
        opposite="MemeberOf_PowerTransformer")

    # The reference voltage at which the magnetizing saturation measurements
    # were made.
#    magBaseU = Float

    # Describes the phases carried by a power transformer.
    phases = PhaseCode

#------------------------------------------------------------------------------
#  "PowerTransformer" class:
#------------------------------------------------------------------------------

class TransformerWinding(ConductingEquipment):
    """ A winding is associated with each defined terminal of a transformer
        (or phase shifter).
    """

    # A transformer winding may have tap changers, separately for voltage and
    # phase angle.  If a TransformerWinding does not have an associated
    # TapChanger, the winding is assumed to be fixed tap.
#    TapChangers = List(Instance(TapChanger))

    # A transformer has windings
    MemeberOf_PowerTransformer = Instance(PowerTransformer,
        opposite="Contains_TransformerWindings")

    # The rated voltage (phase-to-phase) of the winding, usually the same as
    # the neutral voltage.
    ratedU = Float(desc="rated voltage (phase-to-phase) of the winding")

    connectionType = ConnectionType

    # Positive sequence series resistance of the winding.
    r = Float(desc="positive sequence series resistance")

    # Positive sequence series reactance of the winding.
    x = Float(desc="positive sequence series reactance")

    # Magnetizing branch susceptance (B mag).
    b = Float(desc="magnetizing branch susceptance")

    # Magnetizing branch conductance (G mag).
    g = Float(desc="magnetizing branch conductance")

    # Zero sequence series resistance of the winding.
    r0 = Float(desc="zero sequence series resistance")

    # Zero sequence series reactance of the winding.
    x0 = Float(desc="zero sequence series reactance")

    # Zero sequence magnetizing branch susceptance.
    b0 = Float(desc="zero sequence magnetizing branch susceptance")

    # Zero sequence magnetizing branch conductance.
    g0 = Float(desc="zero sequence magnetizing branch conductance")

    # The normal apparent power rating for the winding.
    ratedS = Float(desc="normal apparent power rating")

    # Apparent power that the winding can carry for a short period of time.
    shortTermS = Float(desc="short term apparent power rating")

    # The apparent power that the winding can carry  under emergency
    # conditions.
    emergencyS = Float(desc="normal apparent power rating")

# EOF -------------------------------------------------------------------------
