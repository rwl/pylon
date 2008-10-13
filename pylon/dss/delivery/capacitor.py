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

""" Defines a capacitor """

#------------------------------------------------------------------------------
#  "Capacitor" class:
#------------------------------------------------------------------------------

class Capacitor:
    """ Basic  capacitor

    Implemented as a two-terminal constant impedance (Power Delivery Element)

    Bus2 connection defaults to 0 node of Bus1 (if Bus2 has the default bus
    connection at the time Bus1 is defined.  Therefore, if only Bus1 is
    specified, a shunt capacitor results.
    If delta connected, Bus2 is set to node zero of Bus1 and nothing is
    returned in the lower half of YPrim - all zeroes.

    If an ungrounded wye is desired, explicitly set Bus2= and set all nodes the
    same, e.g. Bus1.4.4.4   (uses 4th node of Bus1 as neutral point)
    or BusNew.1.1.1  (makes a new bus for the neutral point)
    You must specify the nodes or you will get a series capacitor!

    A series capacitor is specified simply by setting bus2 and declaring the
    connection to be Wye.  If the connection is specified as delta, nothing
    will be connected to Bus2. In fact the number of terminals is set to 1.

    Capacitance may be specified as:

     1.  kvar and kv ratings at base frequency.  impedance.  Specify kvar as total for
         all phases (all cans assumed equal). For 1-phase, kV = capacitor can kV rating.
         For 2 or 3-phase, kV is line-line three phase. For more than 3 phases, specify
         kV as actual can voltage.
     2.  Capacitance in uF to be used in each phase.  If specified in this manner,
         the given value is always used whether wye or delta.
     3.  A nodal C matrix (like a nodal admittance matrix).
         If conn=wye then 2-terminal through device
         If conn=delta then 1-terminal.
         Microfarads.

    """

    # Name of first bus. Examples:
    #     bus1=busname bus1=busname.1.2.3
    bus_1 = None

    # Name of 2nd bus. Defaults to all phases connected to first bus, node 0.
    # (Shunt Wye Connection) Not necessary to specify for delta (LL) connection
    bus_2 = None

    # Number of phases.
    phases = 3

    # Total kvar, if one step, or ARRAY of kvar ratings for each step.  Evenly
    # divided among phases. See rules for NUMSTEPS.
    kvar = 1200

    # For 2, 3-phase, kV phase-phase. Otherwise specify actual can rating.
    kv = 12.47

    # {wye | delta |LN |LL}  Default is wye, which is equivalent to LN
    conn = "wye"

    # Nodal cap. matrix, lower triangle, microfarads, of the following form:
    #     cmatrix="c11 | -c21 c22 | -c31 -c32 c33"
    # All steps are assumed the same if this property is used.
    cmatrix = ""

    # ARRAY of Capacitance, each phase, for each step, microfarads.
    # See Rules for NumSteps.
    cuf = ""

    # ARRAY of series resistance in each phase (line), ohms.
    r = 0

    # ARRAY of series inductive reactance(s) in each phase (line) for filter,
    # ohms at base frequency. Use this OR "h" property to define filter.
    xl = 0

    # ARRAY of harmonics to which each step is tuned. Zero is interpreted as
    # meaning zero reactance (no filter).
    harm = 0

    # Number of steps in this capacitor bank. Default = 1. Forces reallocation
    # of the capacitance, reactor, and states array.  Rules:
    # If this property was previously =1, the value in the kvar property is
    # divided equally among the steps. The kvar property does not need to be
    # reset if that is accurate.  If the Cuf or Cmatrix property was used
    # previously, all steps are set to the value of the first step.
    # The states property is set to all steps on. All filter steps are set to
    # the same harmonic.
    # If this property was previously >1, the arrays are reallocated, but no
    # values are altered. You must SUBSEQUENTLY assign all array properties.
    n_steps = 1

    # ARRAY of integers {1|0} states representing the state of each step
    # (on|off). Defaults to 1 when reallocated (on).
    # Capcontrol will modify this array as it turns steps on or off.
    states = 1

# EOF -------------------------------------------------------------------------
