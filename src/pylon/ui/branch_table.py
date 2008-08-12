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
Table editor for Branch lists

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os import path

from enthought.traits.ui.api import TableEditor, InstanceEditor

from enthought.traits.ui.table_column import ObjectColumn, ExpressionColumn

from enthought.traits.ui.table_filter import \
    EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate, RuleTableFilter

from enthought.naming.unique_name import make_unique_name

from pylon.branch import Branch

from pylon.ui.branch_view import branch_view

#------------------------------------------------------------------------------
#  Branch factory function:
#------------------------------------------------------------------------------

def branch_factory(**row_factory_kw):
    """
    Require two or more buses for Branch instantiation

    """

    if "__table_editor__" in row_factory_kw:
        network = row_factory_kw["__table_editor__"].object
        if len(network.buses) < 2:
            print "For Branch addition two or more Buses are requisite"
            return None
        else:
            branch = Branch(
                name=make_unique_name("e", network.branch_names),
                network=network,
                source_bus=network.buses[0],
                target_bus=network.buses[1]
            )
            del row_factory_kw["__table_editor__"]
            print branch.source_bus, branch.target_bus
            return branch

#------------------------------------------------------------------------------
#  Branches "TableEditor" instance:
#------------------------------------------------------------------------------

branches_table_editor = TableEditor(
    columns = [
        ObjectColumn(name="name"),
        ObjectColumn(name="in_service", label="On"),
        ObjectColumn(
            name="source_bus",
            editor=InstanceEditor(name="buses", editable=False),
            label="Source", format_func=lambda obj: obj.name
        ),
        ObjectColumn(
            name="target_bus",
            editor=InstanceEditor(name="buses", editable=False),
            label="Target", format_func=lambda obj: obj.name
        ),
        ObjectColumn(name="r", label="R"),
        ObjectColumn(name="x", label="X"),
        ObjectColumn(name="b", label="B"),
#        ObjectColumn(name="r_zero", label="R0"),
#        ObjectColumn(name="x_zero", label="X0"),
        ObjectColumn(name="ratio", label="Tap"),
        ObjectColumn(name="phase_shift", label="Shift"),
#        ObjectColumn(name="rating_s", label="S"),
#        ObjectColumn(name="rating_v", label="V"),
#        ObjectColumn(name="rating_f", label="f"),
#        ObjectColumn(name="s_max", label="Smax"),
#        ObjectColumn(name="i_max", label="Imax"),
#        ObjectColumn(name="p_max", label="Pmax"),

#        ObjectColumn(
#            name="p_source",
#            label="Psrc",
#            editable=False
#        ),
#        ObjectColumn(
#            name="p_target",
#            label="Pdst",
#            editable=False
#        ),
#        ObjectColumn(
#            name="q_source",
#            label="Qsrc",
#            editable=False
#        ),
#        ObjectColumn(
#            name="q_target",
#            label="Qtar",
#            editable=False
#        )
    ],
    deletable=True,
    orientation="horizontal",
#    edit_view=branch_view,
#    filters=[EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate],
    search=RuleTableFilter(),
    row_factory=branch_factory,
    row_factory_kw={"__table_editor__": ""}
)

# EOF -------------------------------------------------------------------------
