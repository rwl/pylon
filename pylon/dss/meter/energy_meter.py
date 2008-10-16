#------------------------------------------------------------------------------
# Copyright (C) 2008 Richard W. Lincoln
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

""" Defines energy meter objects """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, List, Int, Float, Enum, Set, Bool

from pylon.dss.common.circuit_element import CircuitElement

from meter_element import MeterElement

#------------------------------------------------------------------------------
#  "EnergyMeter" class:
#------------------------------------------------------------------------------

class EnergyMeter(MeterElement):
    """ This class of device accumulates the energy of the voltage and current
    in the terminal of the device to which it is connected.

    It is an intelligent energy meter capable of measuring losses of all
    devices within its "zone".

    The Zone is determined automatically after a circuit change.  The Zone
    starts on the opposite side of the branch on which the meter is located and
    continues in the same direction through the network until
        a) an open point is encountered
        b) an open terminal or switch is encountered
        c) another energy meter is encountered
        d) a branch that is already included in a zone is encountered

    It keeps track of kwh, kvarh, UE,  EEN, Losses, etc., having registers FOR
    each of these quantities.

    In EEN/UE calculations, line overload takes precedence.

    If the Max Zone kW limits are specified, then these replace the line
    overload UE/EEN numbers. These limits were added so that the user can
    override line limits in cases such as networks where it is difficult to
    judge the UE from the individual line limits.

    Only the maximum |kVA| overload is accumulated, not all.  Loads downline
    from an overload are marked WITH a factor representing the degree of
    overload.  This is used to compute EEN/UE FOR loads.

    FOR low voltages, the full kW FOR loads below the emergency min voltage are
    counted. The EEN is proportioned based on how low the voltage is.

    Emergency min voltage must be less than normal min voltage.


    An EnergyMeter object is an intelligent meter connected to a terminal of a
    circuit element.  It simulates the behavior of an actual energy meter.
    However, it has more capability because it can access values at other
    places in the circuit rather than simply at the location at which it is
    installed.  It measures not only power and energy values at its location,
    but losses and overload values within a defined region of the circuit.
    The operation of the object is simple.  It has several registers that
    accumulate certain values.  At the beginning of a study, the registers are
    cleared (reset) to zero.  At the end of each subsequent solution, the meter
    is instructed to take a sample.  Energy values are then integrated using
    the interval of time that has passed since the previous solution.

    Registers

    There are two types of registers:
        1.Energy Accumulators (for energy values)
        2.Maximum power values ("drag hand" registers).

    The energy registers use trapezoidal integration, which allows to use
    somewhat arbitrary time step sizes between solutions with less integration
    error. This is important for using load duration curves approximated with
    straight lines, for example.

    The present definitions of the registers are:
        1.KWh at the meter location.
        2.Kvarh at the meter location.
        3.Maximum kW at the meter location.
        4.Maximum kVA at the meter location.
        5.KWh in the meter zone.
        6.Kvarh in the meter zone.
        7.Maximum kW in the meter zone.
        8.Maximum kVA in the meter zone.
        9.Overload kWh in the meter zone, normal ratings.
        10.Overload kWh in the meter zone, emergency ratings.
        11.Energy Exceeding Normal (EEN) in the loads in the meter zone.
        12.Unserved Energy (UE) in the loads in the meter zone.
        13.Losses (kWh) in power delivery elements in the meter zone.
        14.Reactive losses (kvarh) in power delivery elements in the meter
        zone.
        15.Maximum losses (kW) in  power delivery elements in the meter zone.
        16.Maximum reactive losses (kvar) in power delivery elements in the
        meter zone.

    Zones

    The EnergyMeter object uses the concept of a zone.  This is an area of the
    circuit for which the meter is responsible.  It can compute energies,
    losses, etc for any power delivery object and Load object in its zone
    (Generator objects have their own intrinsic meters).


    A zone is a collection of circuit elements "downline" from the meter.  This
    concept is nominally applicable to radial circuits, but also has some
    applicability to meshed circuits.  The zones are automatically determined
    according to the following rules:
        1.Start with the circuit element in which the meter is located.  Ignore
        the terminal on which the meter is connected.  This terminal is the
        start of the zone. Begin tracing with the other terminal(s).
        2.Trace out the circuit, finding all other circuit elements (loads and
        power delivery elements) connected to the zone.  Continue tracing out
        every branch of the circuit. Stop tracing a branch when:
        The end of the circuit branch is reached
    A circuit element containing another EnergyMeter object is encountered
    A OPEN terminal is encountered.  (all phases in the terminal are open.)
    A disabled device is encountered.
    A circuit element already included in another zone is encountered.
    There are no more circuit elements to consider.
    Zones are automatically updated after a change in the circuit unless
    the ZONELOCK option (Set command) is set to true (Yes).  Then zones
    remain fixed after initial determination.

    """

    # Name (Full Object name) of element to which the monitor is connected.
    element = Instance(CircuitElement)

    # Number of the terminal of the circuit element to which the monitor is
    # connected.  1 or 2, typically.
    terminal = Int(1)

    # {Clear (reset) | Save | Take | Zonedump | Allocate | Reduce}
    # (A)llocate = Allocate loads on the meter zone to match PeakCurrent.
    # (C)lear = reset all registers to zero
    # (R)educe = reduces zone by merging lines (see Set Keeplist &
    # ReduceOption)
    # (S)ave = saves the current register values to a file. File name is
    # "MTR_metername.CSV". (T)ake = Takes a sample at present solution
    # (Z)onedump = Dump names of elements in meter zone to a file
    # File name is "Zone_metername.CSV".
    action = Enum(
        "Clear (reset)", "Save", "Take", "Zonedump", "Allocate", "Reduce"
    )

    # Enter a string ARRAY of any combination of the following. Options
    # processed left-to-right:
    #     (E)xcess : (default) UE/EEN is estimate of energy over capacity
    #     (T)otal : UE/EEN is total energy after capacity exceeded
    #     (R)adial : (default) Treats zone as a radial circuit
    #     (M)esh : Treats zone as meshed network (not radial).
    #     (C)ombined : (default) Load UE/EEN computed from combination of
    #     overload and undervoltage.
    #     (V)oltage : Load UE/EEN computed based on voltage only.
    # Example: option=(E, R)
    option = Set(
        Enum("Excess", "Total", "Radial", "Mesh", "Combined", "Voltage")
    )

    # Upper limit on kVA load in the zone, Normal configuration. Default is 0.0
    # (ignored).  Overrides limits on individual lines for overload EEN. With
    # "LocalOnly=Yes" option, uses only load in metered branch.
    kva_norm = Float(desc="Normal kVA upper limit")

    # Upper limit on kVA load in the zone, Emergency configuration. Default is
    # 0.0 (ignored). Overrides limits on individual lines for overload UE.
    # With "LocalOnly=Yes" option, uses only load in metered branch.
    kva_emerg = Float(desc="Emergency kVA upper limit")

    # ARRAY of current magnitudes representing the peak currents measured at
    # this location for the load allocation function.  Default is (400, 400,
    # 400). Enter one current for each phase
    peak_current = List(Float, [400, 400, 400])

    # ARRAY of full element names for this meter''s zone.  Default is for meter
    # to find it''s own zone. If specified, DSS uses this list instead.  Can
    # access the names in a single-column text file.  Examples:
    # zonelist=[line.L1, transformer.T1, Line.L3]
    # zonelist=(file=branchlist.txt)
    zone_list = List(Instance(CircuitElement))

    # If Yes, meter considers only the monitored element for EEN and UE calcs.
    # Uses whole zone for losses.
    local_only = Bool(False)

    # Mask for adding registers whenever all meters are totalized.  Array of
    # floating point numbers representing the multiplier to be used for summing
    # each register from this meter.  Default = (1, 1, 1, 1, ... ).  You only
    # have to enter as many as are changed (positional). Useful when two meters
    # monitor same energy, etc.
    mask = List(Float)

    # Compute Zone losses. If NO, then no losses at all are computed.
    losses = Bool(True, desc="Compute Zone losses")

    # Compute Line losses. If NO, then none of the losses are computed.
    line_losses = Bool(True, desc="Compute Line losses")

    # Compute Transformer losses. If NO, transformers are ignored in loss
    # calculations.
    xfmr_losses = Bool(True, desc="Compute Transformer losses")

    # Compute Sequence losses in lines and segregate by line mode losses and
    # zero mode losses.
    seq_losses = Bool(
        True, desc="Compute Sequence losses in lines and segregate by line "
        "mode losses and zero mode losses"
    )

    # Compute losses and segregate by voltage base. If NO, then voltage-based
    # tabulation is not reported.
    v_base_losses = Bool(
        True, desc="Compute losses and segregate by voltage base"
    )

    # When true, write Overload exception report when Demand Intervals are
    # written.
    overload_report = Bool(True)

# EOF -------------------------------------------------------------------------
