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
    import Equipment

#------------------------------------------------------------------------------
#  "EnergyArea" class:
#------------------------------------------------------------------------------

class GeneratingUnit(Equipment):
    """ A single or set of synchronous machines for converting mechanical power
        into alternating-current power. For example, individual machines within
        a set may be defined for scheduling purposes while a single control
        signal is derived for the set. In this case there would be a
        GeneratingUnit for each member of the set and an additional
        GeneratingUnit corresponding to the set.
    """

    ControlAreaGeneratingUnit = Instance(HasTraits)

    # A generating unit may have a gross active power to net active power
    # curve, describing the losses and auxiliary power requirements of the unit
    GrossToNetActivePowerCurves = Instance(HasTraits)

    # A synchronous machine may operate as a generator and as such becomes a
    # member of a generating unit
    Contains_SynchronousMachines = Instance(HasTraits)

    # A generating unit may have an operating schedule, indicating the planned
    # operation of the unit
    GenUnitOpSchedule = Instance(HasTraits)

    # A generating unit may have one or more cost curves, depending upon fuel
    # mixture and fuel cost.
    GenUnitOpCostCurves = Instance(HasTraits)

    # The net rated maximum capacity determined by subtracting the auxiliary
    # power used to operate the internal plant machinery from the rated gross
    # maximum capacity
    ratedNetMaxP = Float

#    penaltyFactor
#    stepChange
#    energyMinP

    # The efficiency of the unit in converting mechanical energy, from the
    # prime mover, into electrical energy.
    efficiency = Float

    raiseRampRate = Float

#    dispReserveFlag

    # The initial startup cost incurred for each start of the GeneratingUnit.
    startupCost = Float

#    highControlLimit
#    spinReserveRamp
#    controlPulseLow
#    genControlSource
#    governorSCD

    # For dispatchable units, this value represents the economic active power basepoint, for units that are not dispatchable, this value represents the fixed generation value. The value must be between the operating low and high limits.
    baseP = Float

#    fuelPriority

    # This is the maximum operating active power limit the dispatcher can enter for this unit
    maxOperatingP = Float

#    genControlMode

    # The variable cost component of production per unit of ActivePower.
    variableCost = Float

#    lowControlLimit
#    controlPulseHigh

    # Maximum high economic active power limit, that should not exceed the
    # maximum operating active power limit
    maxEconomicP = Float

#    controlDeadband
#    governorMPL

    # Low economic active power limit that must be greater than or equal to the
    # minimum operating active power limit
    minEconomicP = Float

    # This is the minimum operating active power limit the dispatcher can enter
    # for this unit.
    minOperatingP = Float

#    controlResponseRate
#    modelDetail
#    autoCntrlMarginP

    # The unit's gross rated maximum capacity (Book Value).
    ratedGrossMaxP = Float

#    genOperatingMode
#    fastStartFlag

    # Generating unit economic participation factor.
    longPF = Float

    # Generating unit economic participation factor.
    normalPF = Float

    # Maximum allowable spinning reserve. Spinning reserve will never be
    # considered greater than this value regardless of the current operating
    # point.
    maximumAllowableSpinningReserve = Float

    # The gross rated minimum generation level which the unit can safely
    #operate at while delivering power to the transmission grid
    ratedGrossMinP = Float

    # The planned unused capacity (spinning reserve) which can be used to
    # support emergency load
    allocSpinResP = Float

    # Time it takes to get the unit on-line, from the time that the prime mover
    # mechanical power is applied
    startupTime = Float

    # Default Initial active power  which is used to store a powerflow result
    # for the initial active power for this unit in this network configuration
    initialP = Float

    # Generating unit economic participation factor
    tieLinePF = Float

    # Minimum time interval between unit shutdown and startup
    minimumOffTime = Float

    lowerRampRate = Float

    # Generating unit economic participation factor
    shortPF = Float

# EOF -------------------------------------------------------------------------
