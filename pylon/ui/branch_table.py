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

""" Table editor for Branch lists. """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os import path

from enthought.traits.ui.api import TableEditor, InstanceEditor

from enthought.traits.ui.table_column import ObjectColumn, ExpressionColumn

from enthought.traits.ui.extras.checkbox_column import CheckboxColumn

from enthought.traits.ui.table_filter import \
    EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate, RuleTableFilter

from enthought.naming.unique_name import make_unique_name

from pylon.branch import Branch

from pylon.ui.branch_view import branch_view

from common import OnlineColumn, OnlineFloatColumn

#------------------------------------------------------------------------------
#  Branch factory function:
#------------------------------------------------------------------------------

def branch_factory(**row_factory_kw):
    """ Require two or more buses for Branch instantiation. """

    if "__table_editor__" in row_factory_kw:
        network = row_factory_kw["__table_editor__"].object
        if len(network.buses) < 2:
            print "For Branch addition two or more Buses are requisite"
            return None
        else:
            branch_names = [e.name for e in network.branches]
            branch = Branch(
                name=make_unique_name("branch", branch_names),
                source_bus=network.buses[0],
                target_bus=network.buses[1]
            )
            del row_factory_kw["__table_editor__"]
            return branch
    else:
        return None

#------------------------------------------------------------------------------
#  Branches "TableEditor" instance:
#------------------------------------------------------------------------------

branches_table_editor = TableEditor(
    columns = [
        OnlineColumn(name="name"),
        CheckboxColumn(name="online", label="On", width=0.06),
        OnlineColumn(name="mode", editable=False),
        OnlineColumn(
            name="source_bus",
            editor=InstanceEditor(name="buses", editable=False),
            label="Source", format_func=lambda obj: obj.name
        ),
        OnlineColumn(
            name="target_bus",
            editor=InstanceEditor(name="buses", editable=False),
            label="Target", format_func=lambda obj: obj.name
        ),
        OnlineFloatColumn(name="r", label="R"),
        OnlineFloatColumn(name="x", label="X"),
        OnlineFloatColumn(name="b", label="B"),
#        OnlineFloatColumn(name="r_zero", label="R0"),
#        OnlineFloatColumn(name="x_zero", label="X0"),
        OnlineFloatColumn(name="ratio", label="Tap"),
        OnlineFloatColumn(name="phase_shift", label="Shift"),
#        OnlineFloatColumn(name="rating_s", label="S"),
#        OnlineFloatColumn(name="rating_v", label="V"),
#        OnlineFloatColumn(name="rating_f", label="f"),
#        OnlineFloatColumn(name="s_max", label="Smax"),
#        OnlineFloatColumn(name="i_max", label="Imax"),
#        OnlineFloatColumn(name="p_max", label="Pmax"),

        OnlineFloatColumn(name="p_source", label="Psrc", editable=False),
        OnlineFloatColumn(name="q_source", label="Qsrc", editable=False),
        OnlineFloatColumn(name="mu_s_source", label="|S_source| mu",
                          editable=False)
    ],
    show_toolbar=True,
    deletable=True,
    orientation="horizontal",
#    edit_view=branch_view,
#    filters=[EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate],
    search=RuleTableFilter(),
    row_factory=branch_factory,
    row_factory_kw={"__table_editor__": ""}
)

# EOF -------------------------------------------------------------------------
