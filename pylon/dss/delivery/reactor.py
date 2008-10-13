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

""" Defines a reactor """

#------------------------------------------------------------------------------
#  "Reactor" class:
#------------------------------------------------------------------------------

class Reactor:
    """ Uses same rules as Capacitor and Fault for connections

    Implemented as a two-terminal constant impedance (Power Delivery Element)
    Defaults to a Shunt Reactor but can be connected as a two-terminal series
    reactor

    If Parallel=Yes, then the R and X components are treated as being in
    parallel.

    Bus2 connection defaults to 0 node of Bus1 (if Bus2 has the default bus
    connection at the time Bus1 is defined.  Therefore, if only Bus1 is
    specified, a shunt Reactor results. If delta connected, Bus2 is set to node
    zero of Bus1 and nothing is returned in the lower half of YPrim - all
    zeroes.

    If an ungrounded wye is desired, explicitly set Bus2= and set all nodes the
    same, e.g.
        Bus1.4.4.4   (uses 4th node of Bus1 as neutral point)
        or BusNew.1.1.1  (makes a new bus for the neutral point)
    You must specify the nodes or you will get a series Reactor!

    A series Reactor is specified simply by setting bus2 and declaring the
    connection to be Wye.  If the connection is specified as delta, nothing
    will be connected to Bus2. In fact the number of terminals is set to 1.

    Reactance may be specified as:

     1.  kvar and kv ratings at base frequency.  impedance.  Specify kvar as
         total for all phases. For 1-phase, kV = Reactor coil kV rating.
         For 2 or 3-phase, kV is line-line three phase. For more than 3 phases,
         specify kV as actual coil voltage.
     2.  Series Resistance and Reactance in ohns at base frequency to be used
         in each phase.  If specified in this manner, the given value is always
         used whether wye or delta.
     3.  A R and X  matrices. If conn=wye then 2-terminal through device
         If conn=delta then 1-terminal. Ohms at base frequency
         Note that Rmatix may be in parallel with Xmatric (set parallel = Yes)

    """

    # Name of first bus.
    bus_1 = None

    # Name of 2nd bus. Defaults to all phases connected to first bus, node 0.
    # (Shunt Wye Connection)Not necessary to specify for delta (LL)
    # connection
    bus_2 = None

    # Number of phases.
    phases = 3

    # Total kvar, all phases.  Evenly divided among phases. Only determines X.
    # Specify R separately
    k_var = 1200

    # For 2, 3-phase, kV phase-phase. Otherwise specify actual coil rating.
    kv = 12.47

    # {wye | delta |LN |LL}  Default is wye, which is equivalent to LN. If
    # Delta, then only one terminal.
    conn = "wye"

    # Resistance matrix, lower triangle, ohms at base frequency. Order of the
    # matrix is the number of phases.
    r_matrix = []

    # Reactance matrix, lower triangle, ohms at base frequency. Order of the
    # matrix is the number of phases.
    x_matrix = []

    # Signifies R and X are to be interpreted as being in parallel.
    parallel = False

    # Resistance, each phase, ohms.
    r = 0

    # Reactance, each phase, ohms at base frequency.
    x = 0

    # Resistance in parallel with R and X (the entire branch). Assumed infinite
    # if not specified.
    rp = 0

# EOF -------------------------------------------------------------------------
