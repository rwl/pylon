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

""" Defines a Thevinen equivalent short circuit """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, List, Int, Float, Enum

from pylon.dss.common.bus import Bus

from power_conversion_element import PowerConversionElement

#------------------------------------------------------------------------------
#  "Equivalent" class:
#------------------------------------------------------------------------------

class Equivalent(PowerConversionElement):
    """ Multi terminal, multi-phase Short Circuit (Thevinen) Equivalent

    Enter positive and zero short circuit impedance matrices and Voltage behind
    the equivalent

    """

    # Number of terminals. Set this BEFORE defining matrices.
    terminals = Int(1)

    # Array of Bus Names to which equivalent source is connected.
    buses = List(Instance(Bus))

    # Base Source kV, usually L-L unless you are making a positive-sequence
    # model in which case, it will be L-N.
    base_kv = Float(115.0)

    # Per unit of the base voltage that the source is actually operating at.
    pu = Float(1.0, desc="Per unit of the base voltage")

    # Phase angle in degrees of first phase.
    angle = Float(0.0, desc="Phase angle in degrees of first phase")

    # Source frequency.
    frequency = Float(60.0)

    # Number of phases.
    phases = Int(3)

    # Positive-sequence resistance matrix, lower triangle.
    r1 = Float(1.65)

    # Positive-sequence reactance matrix, lower triangle.
    x1 = Float(6.6)

    # Zero-sequence resistance matrix, lower triangle.
    r0 = Float(1.9)

    # Zero-sequence reactance matrix, lower triangle.
    x0 = Float(5.7)

# EOF -------------------------------------------------------------------------
