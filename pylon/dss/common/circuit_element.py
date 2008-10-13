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

""" Defines a base class for all elements of a circuit """

#------------------------------------------------------------------------------
#  "CircuitElement" class:
#------------------------------------------------------------------------------

class CircuitElement:
    """ Base class for all elements of a circuit """

    # Indicates whether this element is enabled.
    enabled = True

    # Base Frequency for ratings.
    base_freq = 60

    # Need fast access to this
    node_ref = []

    y_order = 0

    # Flag used in tree searches
    last_terminal_checked = 0

    # Flag used in tree searches etc
    checked = False

    has_meter = False

    is_isolated = False

    has_control = False

    is_part_of_feeder = True

    # Pointer to control for this device
    control_element = None

    terminals = []

    active_terminal = None

    # Private interface -------------------------------------------------------

    _bus_names = []

    _enabled = True

    _active_terminal = 1

    _y_prim_invalid = False

    # Protected interface -----------------------------------------------------

    _n_terms = 0

    # No. conductors per terminal
    _n_conds = 0

    # No. of phases
    _n_phases = 0

    _bus_idx = 1

    _y_prim_series = None

    _y_prim_shunt = None

    # Order will be NTerms * Ncond
    _y_prim = []

    # Frequency at which YPrim has been computed
    _y_prim_freq = 0.0

# EOF -------------------------------------------------------------------------
