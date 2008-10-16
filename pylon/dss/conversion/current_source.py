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

""" Defines an ideal current source """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, List, Int, Float, Enum

from pylon.dss.common.bus import Bus

from power_conversion_element import PowerConversionElement

#------------------------------------------------------------------------------
#  "CurrentSource" class:
#------------------------------------------------------------------------------

class CurrentSource(PowerConversionElement):
    """ Ideal current source.

    ISource maintains a positive sequence for harmonic scans.  If you want zero
    sequence, use three single-phase ISource.

    """

    # Name of bus to which source is connected.
    bus_1 = Instance(Bus)

    # Magnitude of current source, each phase, in Amps.
    amps = Float(0.0, desc="Current source magnitude")

    # Phase angle in degrees of first phase. Phase shift between phases is
    # assumed 120 degrees when number of phases <= 3
    angle = Float(0.0, desc="Phase angle of the first phase")

    # Source frequency.  Defaults to  circuit fundamental frequency.
    frequency = Float(60.0)

    # Number of phases. For 3 or less, phase shift is 120 degrees.
    phases = Int(3)

    # {pos*| zero | none} Maintain specified sequence for harmonic solution.
    # Otherwise, angle between phases rotates with harmonic.
    scantype = Enum("Positive", "Zero", "None")

# EOF -------------------------------------------------------------------------
