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

""" Defines a recloser """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, List, Int, Float, Bool, Enum, Str

from pylon.dss.common.circuit_element import CircuitElement

from pylon.dss.general.api import TimeCurrentCurve

from control_element import ControlElement

#------------------------------------------------------------------------------
#  "Recloser" class:
#------------------------------------------------------------------------------

class Recloser(ControlElement):
    """ A Recloser is a control element that is connected to a terminal of a
    circuit element and controls the switches in the same or another terminal.

    The control is usually placed in the terminal of a line or transformer, but
    it could be any element

    CktElement to be controlled must already exist.

    """

    # Full object name of the circuit element, typically a line, transformer,
    # load, or generator, to which the Recloser's PT and/or CT are connected.
    # This is the "monitored" element. There is no default; must be specified.
    monitored_obj = Instance(CircuitElement, allow_none=False)

    # Number of the terminal of the circuit element to which the Recloser is
    # connected. 1 or 2, typically.
    monitored_term = Int(1, desc="Connected terminal of the monitored element")

    # Name of circuit element switch that the Recloser controls. Specify the
    # full object name.Defaults to the same as the Monitored element. This is
    # the "controlled" element.
    switched_obj = Instance(CircuitElement, desc="Controlled element")

    # Number of the terminal of the controlled element in which the switch is
    # controlled by the Recloser. 1 or 2, typically.
    switched_term = Int(1, desc="Connected terminal of the controlled element")

    # Number of Fast (fuse saving) operations. (See "Shots")
    n_fast = Int(1, desc="No. of fuse saving operations")

    # Name of the TCC Curve object that determines the Phase Fast trip. Must
    # have been previously defined as a TCC_Curve object. Default is "A".
    # Multiplying the current values in the curve by the "phasetrip" value
    # gives the actual current.
    phase_fast = Str(
        "A", desc="Name of the TCC Curve object that determines the Phase "
        "Fast trip"
    )

    # Name of the TCC Curve object that determines the Phase Delayed trip. Must
    # have been previously defined as a TCC_Curve object. Default is "D".
    # Multiplying the current values in the curve by the "phasetrip" value
    # gives the actual current.
    phase_delayed = Str(
        "D", desc="Name of the TCC Curve object that determines the Phase "
        "Delayed trip"
    )

    # Name of the TCC Curve object that determines the Ground Fast trip.  Must
    # have been previously defined as a TCC_Curve object. Multiplying the
    # current values in the curve by the "groundtrip" value gives the actual
    # current.
    ground_fast = Instance(TimeCurrentCurve)

    # Name of the TCC Curve object that determines the Ground Delayed trip.
    # Must have been previously defined as a TCC_Curve object. Multiplying the
    # current values in the curve by the "groundtrip" value gives the actual
    # current.
    ground_delayed = Instance(TimeCurrentCurve)

    phase_trip = Float(1.0)

    # Multiplier or actual ground amps (3I0) for the ground TCC curve.
    ground_trip = Float(1.0)

    # Multiplier or actual phase amps for the phase TCC curve.
    phase_inst = Float(1.0)

    # Actual amps for instantaneous ground trip which is assumed to happen in
    # 0.01 sec + Delay Time. Default is 0.0, which signifies no inst trip.
    ground_inst = Float(0.0)

    # Reset time in sec for Recloser.
    reset = Float(15.0, desc="Reset time in sec")

    # Total Number of fast and delayed shots to lockout. This is one more than
    # the number of reclose intervals.
    shots = Int(4, desc="Total Number of fast and delayed shots to lockout")

    # Array of reclose intervals.  Default for Recloser is (0.5, 2.0, 2.0)
    # seconds. A locked out Recloser must be closed manually (action=close).
    reclose_intervals = List(Float, [0.5, 2.0, 2.0])

    # Fixed delay time (sec) added to Recloser trip time. Used to represent
    # breaker time or any other delay.
    delay = Float(0.0, desc="Fixed delay time (sec) added to the trip time")

    # {Trip/Open | Close}  Action that overrides the Recloser control.
    # Simulates manual control on recloser "Trip" or "Open" causes the
    # controlled element to open and lock out. "Close" causes the controlled
    # element to close and the Recloser to reset to its first operation.
    action = Enum(
        "Trip/Open", "Close", desc="Action that overrides the Recloser control"
    )

    # Time dial for Phase Fast trip curve. Multiplier on time axis of specified
    # curve.
    td_ph_fast = Float(1.0)

    # Time dial for Ground Fast trip curve. Multiplier on time axis of
    # specified curve.
    td_gr_fast = Float(1.0)

    # Time dial for Phase Delayed trip curve. Multiplier on time axis of
    # specified curve.
    td_ph_delayed = Float(1.0)

    # Time dial for Ground Delayed trip curve. Multiplier on time axis of
    # specified curve.
    td_gr_delayed = Float(1.0)

# EOF -------------------------------------------------------------------------
