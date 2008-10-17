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
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import HasTraits, Str, List, Int, Float, Bool

from enthought.traits.ui.api import View, Item, Group

from enthought.traits.ui.api import TableEditor, InstanceEditor
from enthought.traits.ui.table_column import ObjectColumn
from enthought.traits.ui.extras.checkbox_column import CheckboxColumn

from enthought.traits.ui.table_filter import \
    EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate, RuleTableFilter

#------------------------------------------------------------------------------
#  "Bus" class:
#------------------------------------------------------------------------------

class Bus(HasTraits):
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

    _nodes = List

    _n_nodes = Int

    _allocation = Int

    _ref_no = List


    # Human readable identifier
    name = Str

    v_bus = Float(115.0, label="Vbus")

    bus_current = List(Float, label="Ibus")

    z_sc = Float(label="Zsc")

    y_sc = Float(label="Ysc")

    # X coordinate
    x = Float(desc="X-coordinate", label="x")

    # Y coordinate
    y = Float(desc="Y-coordinate", label="y")

    # Base kV for each node to ground
    kv_base = Float(
        0.0, desc="Base kV for each node to ground", label="kV base"
    )

    # Are the coordinates defines?
    coords_defined = Bool(False)

    bus_checked = Bool(False)

    keep = Bool(True)

    # Flag for general use in bus searches
    is_radial_bus = Bool(False)

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        ["name", "v_bus", "bus_current", "z_sc", "y_sc", "x", "y", "kv_base"],
        id="pylon.common.bus",
        resizable=True, title="Bus",
        buttons=["OK", "Cancel", "Help"],
        close_result=False
    )

#------------------------------------------------------------------------------
#  Bus table editor:
#------------------------------------------------------------------------------

buses_table_editor = TableEditor(
    columns = [
        ObjectColumn(name="name"),
        ObjectColumn(name="v_bus"),
        ObjectColumn(name="bus_current"),
        ObjectColumn(name="z_sc"),
        ObjectColumn(name="y_sc"),
        ObjectColumn(name="x"),
        ObjectColumn(name="y"),
        ObjectColumn(name="kv_base")
    ],
    show_toolbar=True, deletable=True,
    filters=[EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate],
    search=RuleTableFilter(),
    row_factory=Bus,
#    row_factory_kw={"__table_editor__": ""}
)

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    Bus().configure_traits()

# EOF -------------------------------------------------------------------------
