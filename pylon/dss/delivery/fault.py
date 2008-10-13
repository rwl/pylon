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

""" Defines a fault """

#------------------------------------------------------------------------------
#  "Fault" class:
#------------------------------------------------------------------------------

class Fault:
    """ One or more faults can be placed across any two buses in the circuit.
    Like the capacitor, the second bus defaults to the ground node of the
    same bus that bus1 is connected to.

    The fault is basically an uncoupled, multiphase resistance branch. however,
    you may also specify it as NODAL CONDUCTANCE (G) matrix, which will give
    you complete control of a complex fault situation.

    To eliminate a fault from the system after it has been defined, disable it.

    In Monte Carlo Fault mode, the fault resistance is varied by the % std dev
    specified If %Stddev is specified as zero (default), the resistance is
    varied uniformly.

    Fault may have its "ON" time specified (defaults to 0). When Time (t)
    exceeds this value, the fault will be enabled.  Else it is disabled.

    Fault may be designated as Temporary.  That is, after it is enabled, it
    will disable itself if the fault current drops below the MinAmps value.

    """

    # Name of first bus.
    bus_1 = None

    # Name of 2nd bus.
    bus_2 = None

    # Number of phases.
    phases = 1

    # Resistance, each phase, ohms. Default is 0.0001. Assumed to be Mean value
    # if gaussian random mode.Max value if uniform mode.  A Fault is actually a
    # series resistance that defaults to a wye connection to ground on the
    # second terminal.  You may reconnect the 2nd terminal to achieve whatever
    # connection.  Use the Gmatrix property to specify an arbitrary conductance
    # matrix.
    r = 0.0001

    # Percent standard deviation in resistance to assume for Monte Carlo fault
    # (MF) solution mode for GAUSSIAN distribution. Default is 0 (no variation
    # from mean).
    pct_std_dev = 0

    # Use this to specify a nodal conductance (G) matrix to represent some
    # arbitrary resistance network. Specify in lower triangle form as usual for
    # DSS matrices.
    g_matrix

    # Time (sec) at which the fault is established for time varying
    # simulations. Default is 0.0 (on at the beginning of the simulation)
    on_time = 0.0

    # Designate whether the fault is temporary.  For Time-varying simulations,
    # the fault will be removed if the current through the fault drops below
    # the MINAMPS criteria.
    temporary = False

    # Minimum amps that can sustain a temporary fault.
    min_amps = 5

# EOF -------------------------------------------------------------------------
