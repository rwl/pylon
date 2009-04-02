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
    import View, Group, Item, VGroup, HGroup, InstanceEditor

from CIM13.Core \
    import Equipment, Curve, RegularIntervalSchedule

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
        "unit", opposite="GeneratingUnit")

#    ControlAreaGeneratingUnit = List(Instance("ControlAreaGeneratingUnit"))

    # A generating unit may have a gross active power to net active power
    # curve, describing the losses and auxiliary power requirements of the unit
    GrossToNetActivePowerCurves = List(Instance(HasTraits),
        desc="gross active power to net active power curve",
        opposite="GeneratingUnit")

    # A synchronous machine may operate as a generator and as such becomes a
    # member of a generating unit
    Contains_SynchronousMachines = List(Instance("SynchronousMachine"),
        desc="synchronous machines operating as generators",
        opposite="MemberOf_GeneratingUnit")

    # A generating unit may have one or more cost curves, depending upon fuel
    # mixture and fuel cost.
    GenUnitOpCostCurves = List(Instance("GenUnitOpCostCurve"),
        desc="one or more cost curves, depending upon fuel mixture and fuel "
        "cost", opposite="GeneratingUnit")

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
        "reserve", label="Max Allowable Reserve")

    # The planned unused capacity (spinning reserve) which can be used to
    # support emergency load
    allocSpinResP = Float(desc="spinning reserve for emergency load support")

    # Time it takes to get the unit on-line, from the time that the prime mover
    # mechanical power is applied
    startupTime = Float(desc="time it takes to get the unit on-line")

    # Minimum time interval between unit shutdown and startup
    minimumOffTime = Float(desc="minimum time interval between unit shutdown "
        "and startup")

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(VGroup(["name", Item("description", style="custom"),
                               "efficiency", "startupCost", "variableCost",
                               "startupTime", "minimumOffTime",
                        Group(["initialP", "ratedGrossMaxP", "ratedGrossMinP",
                               "maxOperatingP", "minOperatingP",
                               "maxEconomicP", "minEconomicP",
                               "ratedNetMaxP"],
                            label="Active Power", show_border=True),
                        Group(["maximumAllowableSpinningReserve",
                               "allocSpinResP"],
                              label="Reserve", show_border=True),
                        Group(["raiseRampRate", "lowerRampRate"],
                              label="Ramp rate", show_border=True),
#                       Group(Item("MemberOf_EquipmentContainer",
#                                  show_label=False)),
                       Group(Item("GenUnitOpCostCurves", show_label=False,
                                  height=80),
                             label="GenUnitOpCostCurves", show_border=True),
                       ],
                       Group(Item("GenUnitOpSchedule", style="simple",
#                            editor=InstanceEditor(name="_GenUnitOpSchedules",
#                                                  editable=True),
                            show_label=False))),
                       id="CIM13.Generation.Production.GeneratingUnit",
                       title="GeneratingUnit", resizable=True,
                       buttons=["Help", "OK", "Cancel"])

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
        "have a gross active power to net active power curve",
        opposite="GrossToNetActivePowerCurves")

#------------------------------------------------------------------------------
#  "GenUnitOpCostCurve" class:
#------------------------------------------------------------------------------

class GenUnitOpCostCurve(Curve):
    """ Relationship between unit operating cost (Y-axis) and unit output
        active power (X-axis). The operating cost curve for thermal units is
        derived from heat input and fuel costs. The operating cost curve for
        hydro units is derived from water flow rates and equivalent water
        costs.
    """

    # A generating unit may have one or more cost curves, depending upon fuel
    # mixture and fuel cost.
    GeneratingUnit = Instance(GeneratingUnit, desc="parent unit",
        opposite="GenUnitOpCostCurves")

    # Flag is set to true when output is expressed in net active power.
    isNetGrossP = Bool

#------------------------------------------------------------------------------
#  "GenUnitOpSchedule" class:
#------------------------------------------------------------------------------

class GenUnitOpSchedule(RegularIntervalSchedule):
    """ The generating unit's Operator-approved current operating schedule
        (or plan), typically produced with the aid of unit commitment type
        analyses. The X-axis represents absolute time. The Y1-axis represents
        the status (0=off-line and unavailable: 1=available: 2=must run: 3=must
        run at fixed power value: etc.). The Y2-axis represents the must run
        fixed power value where required.
    """

    # A generating unit may have an operating schedule, indicating the planned
    # operation of the unit.
    GeneratingUnit = Instance(GeneratingUnit, desc="parent unit",
        opposite="GenUnitOpSchedule")

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(VGroup(["name", Item("description", style="custom"),
                               "startTime",
                               "value1Multiplier", "value1Unit",
                               "value2Multiplier", "value2Unit",
                               "timeStep", "endTime"],
                       Group(Item("TimePoints", show_label=False,
                                  height=100),
                             label="Time Points", show_border=True),
                       Item("GeneratingUnit", show_label=False)),
                       id="CIM13.Generation.Production.GenUnitOpSchedule",
                       title="Generating Unit Operating Schedule",
                       resizable=True,
                       buttons=["Help", "OK", "Cancel"])

# EOF -------------------------------------------------------------------------
