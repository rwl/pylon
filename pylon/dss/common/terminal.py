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

""" Defines an element terminal """

#------------------------------------------------------------------------------
#  "Terminal" class:
#------------------------------------------------------------------------------

class Terminal:
    """ Each electrical element in the power system has one or more terminals.
    Each terminal has one or more conductors.  Each conductor contains a
    disconnect switch and a TCC (fuse) curve[Fuse has been disabled and is
    being redesigned; a Relay object can be used if needed to control the
    switches].  The conductors are numbered [1,2,3,...].

    If the terminal is connected to an N-phase device, the first N conductors
    are assumed to correspond to the phases, in order.  The remaining
    conductors may be neutrals or whatever.

    """

    bus_ref = 0

    # Need to get to this fast
    term_node_ref = []

    conductors = []

    checked = False

    # Private interface -------------------------------------------------------

    _n_cond = 0

    _active_conductor = 1

# EOF -------------------------------------------------------------------------
