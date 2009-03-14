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

"""
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    HasTraits, String, Int, Float, List, Instance, Bool, Range, Enum

from enthought.traits.ui.api \
    import View, Group, Item, VGroup, HGroup

from CIM13.Core \
    import Equipment, Curve

#------------------------------------------------------------------------------
#  "GeneratingUnit" class:
#------------------------------------------------------------------------------

class GeneratingUnit(Equipment):
    """ A single or set of synchronous machines for converting mechanical power
        into alternating-current power. For example, individual machines within
        a set may be defined for scheduling purposes while a single control
        signal is derived for the set. In this case there would be a
        GeneratingUnit for each member of the set and an additional
        GeneratingUnit corresponding to the set.
    """

    # A generating unit may have an operating schedule, indicating the planned
    # operation of the unit
    GenUnitOpSchedule = Instance("GenUnitOpSchedule",
        desc="operating schedule, indicating the planned operation of the "
        "unit")

#    ControlAreaGeneratingUnit = List(Instance("ControlAreaGeneratingUnit"))

    # A generating unit may have a gross active power to net active power
    # curve, describing the losses and auxiliary power requirements of the unit
    GrossToNetActivePowerCurves = List(Instance(HasTraits),
        desc="gross active power to net active power curve")

    # A synchronous machine may operate as a generator and as such becomes a
    # member of a generating unit
    Contains_SynchronousMachines = List(Instance("SynchronousMachine"),
        desc="synchronous machines operating as generators")

    # A generating unit may have one or more cost curves, depending upon fuel
    # mixture and fuel cost.
    GenUnitOpCostCurves = List(Instance("GenUnitOpCostCurve"),
        desc="one or more cost curves, depending upon fuel mixture and fuel "
        "cost")

    # Default Initial active power which is used to store a powerflow result
    # for the initial active power for this unit in this network configuration
    initialP = Float(desc="default Initial active power")

    # Defined as: 1 / ( 1 - Incremental Transmission Loss); with the
    # Incremental Transmission Loss expressed as a plus or minus value. The
    # typical range of penalty factors is (0.9 to 1.1).
#    penaltyFactor = Float(desc="Defined as: "
#        "1 / ( 1 - Incremental Transmission Loss)")

    # The efficiency of the unit in converting mechanical energy, from the
    # prime mover, into electrical energy.
    efficiency = Float(90.0, desc="efficiency of the unit in converting "
        "mechanical energy, from the prime mover, into electrical energy")

    # For dispatchable units, this value represents the economic active power
    # basepoint, for units that are not dispatchable, this value represents
    # the fixed generation value. The value must be between the operating low
    # and high limits.
#    baseP = Float(desc="economic active power basepoint or fixed generation "
#        "value")

    raiseRampRate = Float

    lowerRampRate = Float

    # The initial startup cost incurred for each start of the GeneratingUnit.
    startupCost = Float(desc="initial startup cost incurred for each start "
        "of the GeneratingUnit")

    # The variable cost component of production per unit of ActivePower.
    variableCost = Float(desc="variable cost component of production per "
        "unit of ActivePower")

    # Maximum high economic active power limit, that should not exceed the
    # maximum operating active power limit
    maxEconomicP = Float(desc="maximum high economic active power limit.")

    # Low economic active power limit that must be greater than or equal to the
    # minimum operating active power limit
    minEconomicP = Float(desc="low economic active power limit")

    # This is the maximum operating active power limit the dispatcher can enter
    # for this unit.
    maxOperatingP = Float(desc="maximum operating active power limit the "
        "dispatcher can enter for this unit")

    # This is the minimum operating active power limit the dispatcher can enter
    # for this unit.
    minOperatingP = Float(desc="minimum operating active power limit the "
        "dispatcher can enter for this unit")

    # The unit's gross rated maximum capacity (Book Value).
    ratedGrossMaxP = Float(desc="unit's book value")

    # The gross rated minimum generation level which the unit can safely
    #operate at while delivering power to the transmission grid
    ratedGrossMinP = Float(desc="gross rated minimum generation level which "
        "the unit can safely operate at")

    # The net rated maximum capacity determined by subtracting the auxiliary
    # power used to operate the internal plant machinery from the rated gross
    # maximum capacity
    ratedNetMaxP = Float(desc="net rated maximum capacity")

#    # Generating unit economic participation factor.
#    normalPF = Float(desc="normal economic participation factor")
#    # Generating unit economic participation factor
#    shortPF = Float(desc="short economic participation factor")
#    # Generating unit economic participation factor.
#    longPF = Float(desc="long economic participation factor")
#    # Generating unit economic participation factor
#    tieLinePF = Float(desc="tie-line economic participation factor")

    # Maximum allowable spinning reserve. Spinning reserve will never be
    # considered greater than this value regardless of the current operating
    # point.
    maximumAllowableSpinningReserve = Float(desc="maximum allowable spinning "
        "reserve")

    # The planned unused capacity (spinning reserve) which can be used to
    # support emergency load
    allocSpinResP = Float(desc="spinning reserve for emergency load support")

    # Time it takes to get the unit on-line, from the time that the prime mover
    # mechanical power is applied
    startupTime = Float(desc="time it takes to get the unit on-line")

    # Minimum time interval between unit shutdown and startup
    minimumOffTime = Float(desc="minimum time interval between unit shutdown "
        "and startup")

#------------------------------------------------------------------------------
#  "GrossToNetActivePowerCurve" class:
#------------------------------------------------------------------------------

class GrossToNetActivePowerCurve(Curve):
    """ Relationship between the generating unit's gross active power output
        on the X-axis (measured at the terminals of the machine(s)) and the
        generating unit's net active power output on the Y-axis (based on
        utility-defined measurements at the power station). Station service
        loads, when modeled, should be treated as non-conforming bus loads.

        There may be more than one curve, depending on the auxiliary equipment
        that is in service.
    """

    # A generating unit may have a gross active power to net active power
    # curve, describing the losses and auxiliary power requirements of the
    # unit.
    GeneratingUnit = Instance(GeneratingUnit, desc="a generating unit may "
        "have a gross active power to net active power curve")


if __name__ == "__main__":
    unit = GeneratingUnit()
    unit.configure_traits()

# EOF -------------------------------------------------------------------------
