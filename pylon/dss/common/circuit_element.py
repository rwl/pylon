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
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    HasTraits, Instance, List, Int, Float, Bool, Str

from enthought.traits.ui.api import View, Item, Group

from enthought.traits.ui.table_column import ObjectColumn

from terminal import Terminal

#------------------------------------------------------------------------------
#  "CircuitElement" class:
#------------------------------------------------------------------------------

class CircuitElement(HasTraits):
    """ Base class for all elements of a circuit """

    # Human readable identifer
    name = Str

    # Indicates whether this element is enabled.
    enabled = Bool(True)

    # Base Frequency for ratings.
    base_freq = Float(60.0, desc="base frequency for ratings")

    # Need fast access to this
    node_ref = List(Int)

    y_order = Int

    # Flag used in tree searches
    last_terminal_checked = Int

    # Flag used in tree searches etc
    checked = Bool(False)

    has_meter = Bool(False)

    is_isolated = Bool(False)

    has_control = Bool(False)

    is_part_of_feeder = Bool(True)

    # Pointer to control for this device
    control_element = Instance(
        "pylon.dss.control.control_element:ControlElement"
    )

    terminals = List(Instance(Terminal))

    active_terminal = Instance(Terminal)

    # Private interface -------------------------------------------------------

    _bus_names = List(Str)

    _enabled = Bool(True)

    _active_terminal = Int(1)

    _y_prim_invalid = Bool(False)

    # Protected interface -----------------------------------------------------

    _n_terms = Int

    # No. conductors per terminal
    _n_conds = Int

    # No. of phases
    _n_phases = Int

    _bus_idx = Int(1)

    _y_prim_series = None

    _y_prim_shunt = None

    # Order will be NTerms * Ncond
    _y_prim = List(Float)

    # Frequency at which YPrim has been computed
    _y_prim_freq = Float

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        Item("enabled"),
        Item("base_freq")
    )

#------------------------------------------------------------------------------
#  "CircuitElementColumn" class:
#------------------------------------------------------------------------------

class CircuitElementColumn(ObjectColumn):
    """ A specialised column to set the text color differently
    based upon whether or not the circuit element is enabled.

    """

#    width = 0.08

#    horizontal_alignment = "center"

    def get_text_color(self, object):
        return ["light grey", "black"][object.enabled]

# EOF -------------------------------------------------------------------------
