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

""" Defines a WireData object """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import HasTraits, List, Int, Float, Enum

#------------------------------------------------------------------------------
#  "WireData" class:
#------------------------------------------------------------------------------

class WireData(HasTraits):
    """ The WireData object is a general DSS object used by all circuits
    as a reference for obtaining line impedances.

    This class of data defines the raw conductor data that is used to compute
    the impedance for a line geometry.

    Note that you can use whatever units you want for any of the dimensional
    data - be sure to declare the units. Otherwise, the units are all assumed
    to match, which would be very rare for conductor data.  Conductor data is
    usually supplied in a hodge-podge of units. Everything is converted to
    meters internally to the DSS.

    """

    # DC resistance, ohms per unit length (see r_units). Defaults to r_ac if
    # not specified.
    r_dc = Float(-1.0, desc="DC resistance, ohms per unit length")

    # Resistance at 60 Hz per unit length. Defaults to r_dc if not specified.
    r_ac = Float(-1, desc="Resistance at 60 Hz per unit length")

    # Length units for resistance: ohms per {mi|kft|km|m|Ft|in|cm}
    r_units = Enum("mi", "kft", "km", "m", "ft", "in", "cm")

    # GMR at 60 Hz. Defaults to .7788*radius if not specified.
    gmr_ac = Float(-1, desc="GMR at 60 Hz")

    # Units for GMR: {mi|kft|km|m|Ft|in|cm}
    gmr_units = Enum("mi", "kft", "km", "m", "ft", "in", "cm")

    # Outside radius of conductor. Defaults to GMR/0.7788 if not specified.
    radius = Float(-1.0, desc="Outside radius of conductor")

    # Units for outside radius: {mi|kft|km|m|Ft|in|cm}
    rad_units = Enum("mi", "kft", "km", "m", "ft", "in", "cm")

    # Normal ampacity, amperes. Defaults to Emergency amps/1.5 if not
    # specified.
    norm_amps = Float(-1.0, desc="Normal ampacity")

    # Emergency ampacity, amperes. Defaults to 1.5 * Normal Amps if not
    # specified.
    emer_gamps = Float(-1.0, desc="Emergency ampacity")

    # Diameter; Alternative method for entering radius.
    diam = Float(-1.0)

# EOF -------------------------------------------------------------------------
