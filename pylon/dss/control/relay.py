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

""" Defines a relay """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, List, Int, Float, Bool, Enum, Str

from pylon.dss.common.circuit_element import CircuitElement

from pylon.dss.general.api import TimeCurrentCurve

from control_element import ControlElement

#------------------------------------------------------------------------------
#  "Relay" class:
#------------------------------------------------------------------------------

class Relay(ControlElement):
    """ A Relay is a control element that is connected to a terminal of a
    circuit element and controls the switches in the same or another terminal.

    The control is usually placed in the terminal of a line or transformer, but
    it could be any element.

    Voltage relay is a definite time relay that operates after the voltage
    stays out of bounds for a fixed time interval.  It will then reclose a set
    time after the voltage comes back in the normal range.

    """

    # Full object name of the circuit element, typically a line, transformer,
    # load, or generator, to which the relay's PT and/or CT are connected. This
    # is the "monitored" element. There is no default; must be specified.
    monitored_obj = Instance(CircuitElement)

    # Number of the terminal of the circuit element to which the Relay is
    # connected. 1 or 2, typically.
    monitored_term = Int(1)

    # Name of circuit element switch that the Relay controls. Specify the full
    # object name. Defaults to the same as the Monitored element. This is the
    # "controlled" element.
    switched_obj = Instance(CircuitElement)

    # Number of the terminal of the controlled element in which the switch is
    # controlled by the Relay. 1 or 2, typically.
    switched_term = Int(1)

    # One of a legal relay type:
    #    Current Voltage Reversepower 46 (neg seq current)
    #    47 (neg seq voltage)
    #    Generic (generic over/under relay) Default is overcurrent relay
    #    (Current) Specify the curve and pickup settings appropriate for each
    #    type. Generic relays monitor PC Element Control variables and trip on
    #    out of over/under range in definite time.
    type = Enum("Current", "47", "Generic")

    # Name of the TCC Curve object that determines the phase trip.  Must have
    # been previously defined as a TCC_Curve object. Default is none (ignored).
    # For overcurrent relay, multiplying the current values in the curve by the
    # "phasetrip" value gives the actual current.
    phase_curve = Instance(TimeCurrentCurve)

    # Name of the TCC Curve object that determines the ground trip. Must have
    # been previously defined as a TCC_Curve object. For overcurrent relay,
    # multiplying the current values in the curve by the "groundtrip" value
    # gives the actual current.
    ground_curve = Instance(TimeCurrentCurve)

    # Multiplier or actual phase amps for the phase TCC curve.
    phase_trip = Float(
        1.0, desc="Multiplier or actual phase amps for the phase TCC curve"
    )

    # Multiplier or actual ground amps (3I0) for the ground TCC curve.
    ground_trip = Float(
        1.0, desc="Multiplier or actual ground amps for the ground TCC curve"
    )

    # Time dial for Phase trip curve. Multiplier on time axis of specified
    # curve.
    td_phase = Float

    # Time dial for Ground trip curve. Multiplier on time axis of specified
    # curve.
    td_ground = Float

    # Actual amps (Current relay) or kW (reverse power relay) for
    # instantaneous phase trip which is assumed to happen in 0.01 sec + Delay
    # Time. Default is 0.0, which signifies no inst trip. Use this value for
    # specifying the Reverse Power threshold (kW) for reverse power relays.
    phase_inst = Float(0.0)

    # Actual  amps for instantaneous ground trip which is assumed to happen in
    # 0.01 sec + Delay Time.Default is 0.0, which signifies no inst trip.
    ground_inst = Float

    # Reset time in sec for relay.
    reset = Float(15.0)

    # Number of shots to lockout. This is one more than the number of reclose
    # intervals.
    shots = Int(4, desc="Number of shots to lockout")

    # Array of reclose intervals. If none, specify "NONE". Default for
    # overcurrent relay is (0.5, 2.0, 2.0) seconds. Default for a voltage relay
    # is (5.0). In a voltage relay, this is  seconds after restoration of
    # voltage that the reclose occurs. Reverse power relay is one shot to
    # lockout, so this is ignored.  A locked out relay must be closed manually
    # (set action=close).
    reclose_intervals = List(Float, [0.5, 2.0, 2.0])

    # Trip time delay (sec) for definite time relays. Default is 0.0 for
    # current and voltage relays.  If >0 then this value is used instead of
    # curves.  Used exclusively by RevPower, 46 and 47 relays at this release.
    # Defaults to 0.1 s for these relays.
    delay = Float(0.0)

    # TCC Curve object to use for overvoltage relay.  Curve is assumed to be
    # defined with per unit voltage values. Voltage base should be defined for
    # the relay.
    overvolt_curve = Instance(TimeCurrentCurve)

    # TCC Curve object to use for undervoltage relay.  Curve is assumed to be
    # defined with per unit voltage values. Voltage base should be defined for
    # the relay.
    undervolt_curve = Instance(TimeCurrentCurve)

    # Voltage base (kV) for the relay. Specify line-line for 3 phase devices);
    # line-neutral for 1-phase devices.  Relay assumes the number of phases of
    # the monitored element.  Default is 0.0, which results in assuming the
    # voltage values in the "TCC" curve are specified in actual line-to-neutral
    # volts.
    kv_base = Float(0.0)

    # Percent voltage pickup for 47 relay (Neg seq voltage). Specify also base
    # voltage (kvbase) and delay time value.
    pct_pickup_47 = Float(2.0, desc="Percent voltage pickup for 47 relay")

    # Base current, Amps, for 46 relay (neg seq current). Used for establishing
    # pickup and per unit I-squared-t.
    base_amps_46 = Float(desc="Base current for 46 relay")

    # Percent pickup current for 46 relay (neg seq current). When current
    # exceeds this value * BaseAmps, I-squared-t calc starts.
    pct_pickup_46 = Float(20.0, desc="Percent pickup current for 46 relay")

    # Negative Sequence I-squared-t trip value for 46 relay (neg seq current).
    # Default is 1 (trips in 1 sec for 1 per unit neg seq current).
    # Should be 1 to 99.
    isqt_46 = Float(
        1.0, desc="Negative Sequence I-squared-t trip value for 46 relay"
    )

    # Name of variable in PC Elements being monitored.  Only applies to Generic
    # relay.
    variable = Str

    # Trip setting (high value) for Generic relay variable. Relay trips in
    # definite time if value of variable exceeds this value.
    overtrip = Float(desc="High trip setting")

    # Trip setting (low value) for Generic relay variable.  Relay trips in
    # definite time if value of variable is less than this value.
    undertrip = Float(desc="Low trip setting")

    # Fixed delay time (sec) added to relay time. Designed to represent breaker
    # time or some other delay after a trip decision is made.Use Delay_Time
    # property for setting a fixed trip time delay.Added to trip time of
    # current and voltage relays. Could use in combination with inst trip value
    # to obtain a definite time overcurrent relay.
    breaker_time = Float(0.0, desc="delay time added to relay time")

    # {Trip/Open | Close} Action that overrides the relay control. Simulates
    # manual control on breaker. "Trip" or "Open" causes the controlled element
    # to open and lock out. "Close" causes the controlled element to close and
    # the relay to reset to its first operation.
    action = Enum("Trip/Open", "Close")

# EOF -------------------------------------------------------------------------
