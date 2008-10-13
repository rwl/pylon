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
#  "Recloser" class:
#------------------------------------------------------------------------------

class Recloser:
    """ A Recloser is a control element that is connected to a terminal of a
    circuit element and controls the switches in the same or another terminal.

    The control is usually placed in the terminal of a line or transformer, but
    it could be any element

    CktElement to be controlled must already exist.

    """

    # Full object name of the circuit element, typically a line, transformer,
    # load, or generator, to which the Recloser's PT and/or CT are connected.
    # This is the "monitored" element. There is no default; must be specified.
    monitored_obj = None

    # Number of the terminal of the circuit element to which the Recloser is
    # connected. 1 or 2, typically.
    monitored_term = 1

    # Name of circuit element switch that the Recloser controls. Specify the
    # full object name.Defaults to the same as the Monitored element. This is
    # the "controlled" element.
    switched_obj = None

    # Number of the terminal of the controlled element in which the switch is
    # controlled by the Recloser. 1 or 2, typically.
    switched_term = 1

    # Number of Fast (fuse saving) operations. (See "Shots")
    n_fast = 1

    # Name of the TCC Curve object that determines the Phase Fast trip. Must
    # have been previously defined as a TCC_Curve object. Default is "A".
    # Multiplying the current values in the curve by the "phasetrip" value
    # gives the actual current.
    phase_fast = "A"

    # Name of the TCC Curve object that determines the Phase Delayed trip. Must
    # have been previously defined as a TCC_Curve object. Default is "D".
    # Multiplying the current values in the curve by the "phasetrip" value
    # gives the actual current.
    phase_delayed = "D"

    # Name of the TCC Curve object that determines the Ground Fast trip.  Must
    # have been previously defined as a TCC_Curve object. Multiplying the
    # current values in the curve by the "groundtrip" value gives the actual
    # current.
    ground_fast = None

    # Name of the TCC Curve object that determines the Ground Delayed trip.
    # Must have been previously defined as a TCC_Curve object. Multiplying the
    # current values in the curve by the "groundtrip" value gives the actual
    # current.
    ground_delayed = None

    phase_trip = 1.0

    # Multiplier or actual ground amps (3I0) for the ground TCC curve.
    ground_trip = 1.0

    # Multiplier or actual phase amps for the phase TCC curve.
    phase_inst = 1.0

    # Actual amps for instantaneous ground trip which is assumed to happen in
    # 0.01 sec + Delay Time.Default is 0.0, which signifies no inst trip.
    ground_inst = 0

    # Reset time in sec for Recloser.
    reset = 15

    # Total Number of fast and delayed shots to lockout. This is one more than
    # the number of reclose intervals.
    shots = 4

    # Array of reclose intervals.  Default for Recloser is (0.5, 2.0, 2.0)
    # seconds. A locked out Recloser must be closed manually (action=close).
    reclose_intervals = (0.5, 2.0, 2.0)

    # Fixed delay time (sec) added to Recloser trip time. Used to represent
    # breaker time or any other delay.
    delay = 0.0

    # {Trip/Open | Close}  Action that overrides the Recloser control.
    # Simulates manual control on recloser "Trip" or "Open" causes the
    # controlled element to open and lock out. "Close" causes the controlled
    # element to close and the Recloser to reset to its first operation.
    action = "Trip/Open"

    # Time dial for Phase Fast trip curve. Multiplier on time axis of specified
    # curve.
    td_ph_fast = 1.0

    # Time dial for Ground Fast trip curve. Multiplier on time axis of
    # specified curve.
    td_gr_fast = 1.0

    # Time dial for Phase Delayed trip curve. Multiplier on time axis of
    # specified curve.
    td_ph_delayed = 1.0

    # Time dial for Ground Delayed trip curve. Multiplier on time axis of
    # specified curve.
    td_gr_delayed = 1.0

# EOF -------------------------------------------------------------------------
