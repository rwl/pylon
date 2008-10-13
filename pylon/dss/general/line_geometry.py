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

""" Defines the LineGeometry object """

#------------------------------------------------------------------------------
#  "LineGeometry" class:
#------------------------------------------------------------------------------

class LineGeometry:
    """ The LineGeometry object is a general DSS object used by all circuits
    as a reference for obtaining line impedances.

    Defines the positions of the conductors.

    """

    # Number of conductors in this geometry.
    n_conds = 3

    # Number of phases.  All other conductors are considered neutrals and might
    # be reduced out.
    n_phases = 3

    # Set this = number of the conductor you wish to define.
    cond = 1

    # Code from WireData. MUST BE PREVIOUSLY DEFINED. no default.
    wire = ""

    # x coordinate.
    x = 0

    # Height of conductor.
    h = 32

    # Units for x and h: {mi|kft|km|m|Ft|in|cm } Initial default is "ft", but
    # defaults to last unit defined
    units = "ft"

    # Normal ampacity, amperes for the line. Defaults to first conductor if not
    # specified.
    norm_amps = 0

    # Emergency ampacity, amperes. Defaults to first conductor if not
    # specified.
    emerg_amps = 0

    # {Yes | No} Default = no. Reduce to n_phases (Kron Reduction). Reduce out
    # neutrals.
    reduce = "No"

# EOF -------------------------------------------------------------------------
