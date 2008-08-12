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
Table editor for Load lists

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os import path

from enthought.traits.ui.api import TableEditor

from enthought.traits.ui.table_column import ObjectColumn

from enthought.traits.ui.table_filter import \
    EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate, RuleTableFilter

from enthought.naming.unique_name import make_unique_name

from pylon.load import Load

from pylon.ui.load_view import load_view

#------------------------------------------------------------------------------
#  load factory function:
#------------------------------------------------------------------------------

def load_factory(**row_factory_kw):
    """
    Require one or more Bus for Load instantiation

    """

    if "__table_editor__" in row_factory_kw:
        bus = row_factory_kw["__table_editor__"].object

        l_names = [l.name for l in bus.loads]
        name = make_unique_name("l", l_names)

        del row_factory_kw["__table_editor__"]

        return Load(name=name)

#------------------------------------------------------------------------------
#  Loads "TableEditor" instance:
#------------------------------------------------------------------------------

loads_table_editor = TableEditor(
    columns = [
        ObjectColumn(name="name"),
        ObjectColumn(name="in_service"),
#        ObjectColumn(
#            name="bus",
#            editor=InstanceEditor(name="buses", editable=False)
#        ),
#        ObjectColumn(name="rating_s"),
#        ObjectColumn(name="rating_v"),
        ObjectColumn(name="p"),
        ObjectColumn(name="q"),
#        ObjectColumn(name="v_max"),
#        ObjectColumn(name="v_min"),
#        ObjectColumn(name="p_max_bid"),
#        ObjectColumn(name="p_min_bid"),
#        ObjectColumn(name="p_bid"),
#        ObjectColumn(name="p_cost_fixed"),
#        ObjectColumn(name="p_cost_proportional"),
#        ObjectColumn(name="p_cost_quadratic"),
#        ObjectColumn(name="q_cost_fixed"),
#        ObjectColumn(name="q_cost_proportional"),
#        ObjectColumn(name="q_cost_quadratic"),
#        ObjectColumn(name="rate_up"),
#        ObjectColumn(name="rate_down"),
#        ObjectColumn(name="min_period_up"),
#        ObjectColumn(name="min_period_down"),
    ],
    deletable=True,
    orientation="vertical",
#    edit_view=load_view,
#    filters=[EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate],
    search=RuleTableFilter(),
    row_factory=load_factory,
    row_factory_kw={"__table_editor__": ""}
)

#------------------------------------------------------------------------------
#  All loads "TableEditor" instance:
#------------------------------------------------------------------------------

all_loads_table_editor = TableEditor(
    columns = [
        ObjectColumn(name="name"),
        ObjectColumn(name="in_service"),
        ObjectColumn(name="p"),
        ObjectColumn(name="q")
    ],
    deletable=False, orientation="horizontal",# edit_view=load_view,
#    filters=[EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate],
    search=RuleTableFilter()
)

# EOF -------------------------------------------------------------------------
