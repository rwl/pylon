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

""" Defines the LoadShape object """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import HasTraits, Enum, Int, Float, List, File

#------------------------------------------------------------------------------
#  "LoadShape" class:
#------------------------------------------------------------------------------

class LoadShape(HasTraits):
    """ The LoadShape object is a general DSS object used by all circuits
    as a reference for obtaining yearly, daily, and other load shapes.

    Loadshapes default to fixed interval data.  If the Interval is specified to
    be 0.0, then both time and multiplier data are expected.  If the Interval
    is  greater than 0.0, the user specifies only the multipliers.  The Hour
    command is ignored and the files are assumed to contain only the multiplier
    data.

    The user may place the data in CSV or binary files as well as passing
    through the command interface. Obviously, for large amounts of data such as
    8760 load curves, the command interface is cumbersome.  CSV files are text
    separated by commas, one interval to a line. There are two binary formats
    permitted: 1) a file of Singles; 2) a file of Doubles.

    For fixed interval data, only the multiplier is expected.  Therefore, the
    CSV format would contain only one number per line.  The two binary formats
    are packed.

    For variable interval data, (hour, multiplier) pairs are expected in both
    formats.

    The Mean and Std Deviation are automatically computed when a new series of
    points is entered.

    The data may also be entered in unnormalized form.  The normalize=Yes
    command will force normalization.  That is, the multipliers are scaled so
    that the maximum value is 1.0.


    A LoadShape object consists of a series of multipliers, nominally ranging
    from 0.0 to 1.0 that are applied to the base kW values of the load to
    represent variation of the load over some time period.

    Load shapes are generally fixed interval, but may also be variable
    interval.  For the latter, both the time, hr, and the multiplier must be
    specified.

    All loadshapes, whether they be daily, yearly, or some arbitrary duty
    cycle, are maintained in this class.  Each load simply refers to the
    appropriate shape by name.

    The loadshape arrays may be entered directly in command line, or the load
    shapes may be stored in one of three different types of files from which
    the shapes are loaded into memory.

    """

    # Max number of points to expect in load shape vectors. This gets reset to
    # the number of multiplier values found (in files only) if less than
    # specified.
    n_pts = Int(0, desc="Number of points to expect in load shape vectors")

    # Time interval (hrs) for fixed interval data.  If set = 0 then time data
    # (in hours) is expected using either the Hour property or input files.
    interval = Int(1, desc="Time interval (hrs) for fixed interval data")

    # Array of multiplier values for active power (P).  Can also use the
    # syntax: mult = (file=filename) where the file contains one value per
    # line. In "file=" syntax, the number of points may be altered.
    mult = List(Float, desc="Multiplier values for active power")

    # Array of hour values. Only necessary to define for variable interval
    # data.  If the data are fixed interval, do not use this property.  Can
    # also use the syntax: mult = (file=filename) where the file contains one
    # value per line.
    hour = List(Float, desc="Hour values")

    # Mean of the active power multipliers.  Automatically computed when a
    # curve is defined.  However, you may set it independently.  Used for Monte
    # Carlo load simulations.
    #
    # The mean and standard deviation are always computed after an array of
    # points are entered or normalized (see below).  However, if you are doing
    # only parametric load studies using the Monte Carlo solution mode, only
    # the Mean and Std Deviation are required to define a loadshape.  These two
    # values may be defined directly rather than by supplying the curve.  Of
    # course, the multiplier points are not generated.
    mean = Float(0.0, desc="Mean of the active power multipliers")

    # Standard deviation of active power multipliers.  This is automatically
    # computed when a vector or file of multipliers is entered.  However, you
    # may set it to another value indepently.  Is overwritten if you
    # subsequently read in a curve.  Used for Monte Carlo load simulations.
    std_dev = Float(0.0, desc="Standard deviation of active power multipliers")

    # The next three parameters instruct the LoadShape object to get its data
    # from a file.  Three different formats are allowed. If Interval>0 then
    # only the multiplier is entered.  For variable interval data, set
    # Interval=0.0 and enter both the time (in hours) and multiplier, in that
    # order for each interval.

    # Switch input of active power load curve data to a csv file containing
    # (hour, mult) points, or simply (mult) values for fixed time interval
    # data, one per line.
    #
    # NOTE: This action may reset the number of points to a lower value.
    csv_file = File(desc="CSV file containing (hour, mult) points")

    # Switch input of active power load curve data to a binary file of singles
    # containing (hour, mult) points, or simply (mult) values for fixed time
    # interval data, packed one after another.
    #
    # NOTE: This action may reset the number of points to a lower value.
    sng_file = File(
        desc="binary file of singles containing (hour, mult) points"
    )

    # Switch input of active power load curve data to a binary file of doubles
    # containing (hour, mult) points, or simply (mult) values for fixed time
    # interval data, packed one after another.
    #
    # NOTE: This action may reset the number of points to a lower value.
    dbl_file = File(
        desc="binary file of doubles containing (hour, mult) points"
    )

    # NORMALIZE is only defined action. After defining load curve data, setting
    # action=normalize will modify the multipliers so that the peak is 1.0.
    # The mean and std deviation are recomputed.
    #
    # Many times the raw load shape data is in actual kW or some other unit.
    # The load shapes normally will have a maximum value of 1.0.  Specifying
    # this parameter as "Action=N" after the load shape multiplier data are
    # imported will force the normalization of the data in memory and
    # recalculation of the mean and standard deviation.
    action = Enum("normalise")

    # Array of multiplier values for reactive power (Q).  Can also use the
    # syntax: qmult = (file=filename) where the file contains one value per
    # line.
    q_mult = List(Float, desc="Multiplier values for reactive power")

# EOF -------------------------------------------------------------------------
