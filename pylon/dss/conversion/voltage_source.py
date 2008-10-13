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

""" Defines a voltage source """

#------------------------------------------------------------------------------
#  "VoltageSource" class:
#------------------------------------------------------------------------------

class VoltageSource(PowerConversionElement):
    """ This is a special power conversion element.  It is special because
    voltage sources must be identified to initialize the solution with all
    other injection sources set to zero.

    A Vsource object is simply a multi-phase Thevenin equivalent with data
    specified as it would commonly be for a power system source equivalent:
    Line-line voltage (kV) and short circuit MVA.

    """

    # Name of bus to which the source's one terminal is connected.  Remember
    # to specify the node order if the terminals are connected in some unusual
    # manner.
    bus_1 = None

    # Base Source kV, usually L-L unless you are making a positive-sequence
    # model in which case, it will be L-N.
    base_kv = 115

    # Per unit of the base voltage that the source is actually operating at.
    # Assumed balanced for all phases.
    pu = 1

    # Phase angle in degrees of first phase.
    angle = 0

    # Source frequency.
    frequency = 60

    # Number of phases.
    phases = 3

    # MVA Short circuit, 3-phase fault.  Z1 is determined by squaring the base
    # kv and dividing by this value.  For single-phase source, this value is
    # not used.
    mva_sc3 = 2000

    # MVA Short Circuit, 1-phase fault.  The "single-phase impedance", Zs, is
    # determined by squaring the base kV and dividing by this value.  Then Z0
    # is determined by Z0 = 3Zs - 2Z1.  For 1-phase sources, Zs is used
    # directly. Use x0_r0 to define X/R ratio for 1-phase source.
    mva_sc1 = 2100

    # Positive-sequence X/R ratio.
    x1_r1 = 4

    # Zero-sequence X/R ratio.
    x0_r0 = 3

    # Alternate method of defining the source impedance. 3-phase short circuit
    # current, amps.
    i_sc3 = 10000

    # Alternate method of defining the source impedance. Single-phase short
    # circuit current, amps.
    i_sc1 = 10500

    # Alternate method of defining the source impedance. Positive-sequence
    # resistance, ohms.
    r1 = 1.65

    # Alternate method of defining the source impedance. Positive-sequence
    # reactance, ohms.
    x1 = 6.6

    # Alternate method of defining the source impedance. Zero-sequence
    # resistance, ohms.
    r0 = 1.9

    # Alternate method of defining the source impedance. Zero-sequence
    # reactance, ohms.
    x0 = 5.7

    # Base Frequency for impedance specifications.
    base_freq = 60

    # {pos*| zero | none} Maintain specified sequence for harmonic solution.
    # Default is positive sequence. Otherwise, angle between phases rotates
    # with harmonic.
    scan_type = "Pos"

# EOF -------------------------------------------------------------------------
