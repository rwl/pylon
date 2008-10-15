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

""" Defines the GrowthShape object """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import HasTraits, List, Int, Float, File

#------------------------------------------------------------------------------
#  "GrowthShape" class:
#------------------------------------------------------------------------------

class GrowthShape(HasTraits):
    """ The GrowthShape object is a general DSS object used by all circuits
    as a reference for obtaining yearly growth curves.

    A GrowthShape object is similar to a Loadshape object.  However, it is
    intended to represent the growth in load year-by-year and the way the curve
    is specified is entirely different.  You must enter the growth for the
    first year.  Thereafter, only the years where there is a change must be
    entered.  Otherwise it is assumed the growth stays the same.

    Growth shapes are entered as multipliers for the previous year's load.  If
    the load grows by 2.5% in a year, the multiplier is entered as 1.025.  You
    do not need to enter subsequent years if the multiplier remains the same.
    You need only enter the years in which the growth rate is assumed to have
    changed.

    The user may place the data in CSV or binary files as well as passing
    through the command interface. The rules are the same as for LoadShapes
    except that the year is always entered.  CSV files are text separated by
    commas, one interval to a line. There are two binary formats permitted:
    1) a file of Singles; 2) a file of Doubles.

    """

    # Number of points to expect in subsequent vector.
    n_pts = Int(desc="Number of points in subsequent vector")

    # Array of year values, or a text file spec, corresponding to the
    # multipliers.  Enter only those years where the growth changes.  May be
    # any integer sequence -- just so it is consistent. See help on mult.
    # Setting the global solution variable Year=0 causes the growth factor to
    # default to 1.0, effectively neglecting growth.  This is what you would do
    # for all base year analyses.  You may also use the syntax:
    # year=(file=filename.ext) in which the array values are entered one per
    # line in the text file referenced.
    year = List(Float, desc="Array of year values")

    # Array of growth multiplier values, or a text file spec, corresponding to
    # the year values.  Enter the multiplier by which you would multiply the
    # previous year''s load to get the present year''s.  Examples:
    #    Year = "1, 2, 5"   Mult="1.05, 1.025, 1.02".
    #    Year= (File=years.txt) Mult= (file=mults.txt).
    # Text files contain one value per line.
    #
    # Normally, only a few points need be entered and the above parameters will
    # be quite sufficient.  However, provision has been made to enter the
    # (year, multiplier) points from files just like the LoadShape objects.
    # You may also use the syntax: mult=(file=filename.ext) in which the array
    # values are entered one per line in the text file referenced.
    mult = List(Float, desc="Array of growth multiplier values")

    # Switch input of growth curve data to a csv file containing (year, mult)
    # points, one per line.
    csv_file = File(desc="CSV file containing (year, mult) points")

    # Switch input of growth curve data to a binary file of singles containing
    # (year, mult) points, packed one after another.
    sng_file = File(
        desc="binary file of singles containing (year, mult) points"
    )

    # Switch input of growth curve data to a binary file of doubles containing
    # (year, mult) points, packed one after another.
    dbl_file = File(
        desc="binary file of doubles containing (year, mult) points"
    )

# EOF -------------------------------------------------------------------------
