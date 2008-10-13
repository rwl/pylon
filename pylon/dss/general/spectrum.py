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

""" """

#------------------------------------------------------------------------------
#  "Spectrum" class:
#------------------------------------------------------------------------------

class Spectrum:
    """ Spectrum specified as Harmonic, pct magnitude and angle

    Spectrum is shifted by the fundamental angle and stored in MultArray
    so that the fundamental is at zero degrees phase shift.

    """

    # Number of frequencies in this spectrum. (See CSVFile)
    n_harm = 0

    # Array of harmonic values.
    harmonic = []

    # Array of magnitude values, assumed to be in PERCENT.
    pct_mag = []

    # Array of phase angle values, degrees.
    angle = []

    # File of spectrum points with (harmonic, magnitude-percent, angle-degrees)
    # values, one set of 3 per line, in CSV format. If fewer than NUMHARM
    # frequencies found in the file, NUMHARM is set to the smaller value.
    csv_file = ""

# EOF -------------------------------------------------------------------------
