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

""" Defines a time-current curve """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import HasTraits, List, Int, Float, File

#------------------------------------------------------------------------------
#  "TimeCurrentCurve" class:
#------------------------------------------------------------------------------

class TimeCurrentCurve(HasTraits):
    """ Nominally, a time-current curve, but also used for volt-time curves.

    Collections of time points.  Return values can be interpolated either
    Log-Log as traditional TCC or as over- or under-voltage definite time.

    A TCC_Curve object is defined similarly to Loadshape and Growthshape
    objects in that they all are defined by curves consisting of arrays of
    points.  Intended to model time-current characteristics for overcurrent
    relays, TCC_Curve objects are also used for other relay types requiring
    time curves.  Both the time array and the C array must be entered.

    """

    # Number of points to expect in time-current arrays.
    n_pts = Int(0)

    # Array of current (or voltage) values corresponding to time values.
    c_array = List(Float, desc="Current (or voltage) values")

    # Array of time values in sec. Typical array syntax:
    #     t_array = (1, 2, 3, 4, ...)
    # Can also substitute a file designation:
    #     t_array =  (file=filename)
    # The specified file has one value per line.
    t_array = List(Float, desc="Array of time values in sec")

# EOF -------------------------------------------------------------------------
