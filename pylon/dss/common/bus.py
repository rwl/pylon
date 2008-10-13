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

""" Defines a bus """

#------------------------------------------------------------------------------
#  "Bus" class:
#------------------------------------------------------------------------------

class Bus:
    """ A bus is a circuit element having [1..N] nodes. Buses are the
    connection point for all other circuit elements. The main electrical
    property of a Bus is voltage.  Each node has a voltage with respect to the
    zero voltage reference (remote ground).  There is a nodal admittance
    equation written for every node (i.e., the current is summed at each node).

    A bus may have any number of nodes (places to connect device terminal
    conductors).  The nodes may be arbitrarily numbered, except that the first
    N are reserved for the N phases.  Thus, if a bus has 3-phase devices
    connected to it, connections would be expected to nodes 1, 2, and 3.  So
    the DSS would use these voltages to compute the sequence voltages, for
    example.   Phase 1 would nominally represent the same phase throughout the
    circuit, although that would not be mandatory.  It is up to the user to
    maintain a consistent definition.  If only the default connections are
    used, the consistency is maintained automatically. Any other nodes would
    simply be points of connection with no special meaning.

    Each Bus object keeps track of the allocation and designation of its nodes.

    Node 0 of a bus is always the voltage reference (a.k.a, ground, or earth).
    That is, it always has a voltage of exactly zero volts.

    """

    _nodes = []

    _n_nodes = 0

    _allocation = 0

    _ref_no = []


    v_bus = 115

    bus_current = []

    z_sc

    y_sc

    # X coordinate
    x

    # Y coordinate
    y

    # Base kV for each node to ground
    kv_base = 0

    # Are the coordinates defines?
    coords_defined = False

    bus_checked = False

    keep = True

    # Flag for general use in bus searches
    is_radial_bus = False

# EOF -------------------------------------------------------------------------
