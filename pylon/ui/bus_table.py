#------------------------------------------------------------------------------
# Copyright (C) 2007 Richard W. Lincoln
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

"""
Table editor for Bus lists

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os import path

from enthought.traits.ui.api import TableEditor
from enthought.traits.ui.table_column import ObjectColumn

from enthought.traits.ui.table_filter import \
    EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate, RuleTableFilter

from pylon.bus import Bus

from bus_view import bus_view
from common import ContextMenuColumn, FloatColumn, make_unique_name

#------------------------------------------------------------------------------
#  Bus factory function:
#------------------------------------------------------------------------------

def bus_factory(**row_factory_kw):
    """ Specify network for bus on instantiation from table editor """

    if "__table_editor__" in row_factory_kw:
        network = row_factory_kw["__table_editor__"].object
        del row_factory_kw["__table_editor__"]
        bus_names = [v.name for v in network.buses]
        return Bus(name=make_unique_name("bus", bus_names))

#------------------------------------------------------------------------------
#  Buses "TableEditor" instance:
#------------------------------------------------------------------------------

buses_table_editor = TableEditor(
    columns = [
        ContextMenuColumn(name="name"),
        ContextMenuColumn(name="mode", editable=False),
        FloatColumn( name     = "p_supply",
                     label    = "Ps",
                     editable = False ),
        FloatColumn( name     = "q_supply",
                     label    = "Qs",
                     editable = False ),
        FloatColumn( name     = "p_demand",
                     label    = "Pd",
                     editable = False ),
        FloatColumn( name     = "q_demand",
                     label    = "Qd",
                     editable = False ),
        ObjectColumn(name="slack", label="slack"),
#        ObjectColumn(name="v_amplitude", label="Vnom"),
        FloatColumn(name="v_amplitude_guess", label="Vm0"),
        FloatColumn(name="v_phase_guess", label="Va0"),
        FloatColumn(name="g_shunt", label="Gshunt"),
        FloatColumn(name="b_shunt", label="Bshunt"),
        FloatColumn(name="v_amplitude", editable=False, label="Va"),
        FloatColumn(name="p_lambda", editable=False, label="Lambda ($/MWh)")
    ],
    show_toolbar=True,
    deletable=True,
    orientation="horizontal",
#    edit_view=bus_view,
#    filters=[EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate],
    search=RuleTableFilter(),
    row_factory=bus_factory,
    row_factory_kw={"__table_editor__": ""}
)

# EOF -------------------------------------------------------------------------
