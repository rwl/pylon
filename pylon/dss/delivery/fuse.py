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

""" Defines a fuse """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, List, Int, Float, Enum, Array, Str

from pylon.dss.control.control_element import ControlElement

from pylon.dss.common.circuit_element import CircuitElement

#------------------------------------------------------------------------------
#  "Fuse" class:
#------------------------------------------------------------------------------

class Fuse(ControlElement):
    """ A Fuse is a control element that is connected to a terminal of a
    circuit element and controls the switches in the same or another terminal.

    The control is usually placed in the terminal of a line or transformer, but
    it could be any element.

    """

    # Full object name of the circuit element, typically a line, transformer,
    # load, or generator, to which the Fuse is connected. This is the
    # "monitored" element. There is no default; must be specified.
    monitored_obj = Instance(CircuitElement)

    # Number of the terminal of the circuit element to which the Fuse is
    # connected.  1 or 2, typically.
    monitor_term = Int(1)

    # Name of circuit element switch that the Fuse controls. Specify the full
    # object name. Defaults to the same as the Monitored element. This is the
    # "controlled" element.
    switched_obj = Instance(CircuitElement)

    # Number of the terminal of the controlled element in which the switch is
    # controlled by the Fuse. 1 or 2, typically.  Assumes all phases of the
    # element have a fuse of this type.
    switched_term = Int(1)

    # Name of the TCC Curve object that determines the fuse blowing.  Must have
    # been previously defined as a TCC_Curve object. Default is "Tlink".
    # Multiplying the current values in the curve by the "RatedCurrent" value
    # gives the actual current.
    fuse_curve = Str(
        "Tlink", desc="TCC Curve object that determines the fuse blowing"
    )

    # Multiplier or actual phase amps for the phase TCC curve.
    rated_current = Float(1.0)

    # Fixed delay time (sec) added to Fuse blowing time determined from the TCC
    # curve. Used to represent fuse clearing time or any other delay.
    delay = Float(0.0)

    # {Trip/Open | Close}  Action that overrides the Fuse control. Simulates
    # manual control on Fuse "Trip" or "Open" causes the controlled element to
    # open and lock out. "Close" causes the controlled element to close and the
    # Fuse to reset.
    action = Enum("Trip/Open", "Close")

# EOF -------------------------------------------------------------------------
