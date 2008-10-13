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

""" Defines a feeder """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import HasTraits, Instance, List, Str, Float, Bool

#------------------------------------------------------------------------------
#  "Feeder" class:
#------------------------------------------------------------------------------

class Feeder(HasTraits):
    """ User cannot instantiate this object.  Feeders are created on the fly
    when a radial system is specified.  Feeders are created from Energymeters
    and are given the same name.

    Feeders get created from energy meters if Radial is set to yes and meter
    zones are already computed.  If Radial=Yes and the meterzones are reset,
    then the feeders are redefined.  If Radial is subsequently set to NO or a
    solution mode is used that doesn't utilize feeders, the get currents
    routines will not do anything.

    Feeders cannot be re-enabled unless the energymeter object allows them to
    be.

    Feeders are not saved.  This is implicit with the Energymeter saving.

    """

    # Name of harmonic spectrum for this device.
    spectrum = Str

    # Base Frequency for ratings.
    base_freq = Float(60.0)

    # Indicates whether this element is enabled.
    enabled = Bool(True)

# EOF -------------------------------------------------------------------------
