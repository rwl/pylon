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
Table editor for Generator lists

"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os import path

from enthought.naming.unique_name import make_unique_name
from enthought.traits.ui.api import TableEditor, InstanceEditor
from enthought.traits.ui.table_column import ObjectColumn
from enthought.traits.ui.extras.checkbox_column import CheckboxColumn

from enthought.traits.ui.table_filter import \
    EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate, RuleTableFilter

from pylon.generator import Generator

from pylon.ui.generator_view import generator_view

from common import InServiceColumn, InServiceFloatColumn

#------------------------------------------------------------------------------
#  Generator factory function:
#------------------------------------------------------------------------------

def generator_factory(**row_factory_kw):
    """ Require one or more Bus for instantiation """

    if "__table_editor__" in row_factory_kw:
        bus = row_factory_kw["__table_editor__"].object

        g_names = [g.name for g in bus.generators]
        name = make_unique_name("g", g_names)

        del row_factory_kw["__table_editor__"]

        return Generator(name=name)

#------------------------------------------------------------------------------
#  Generators "TableEditor" instance:
#------------------------------------------------------------------------------

generators_table_editor = TableEditor(
    columns = [
        CheckboxColumn(name="in_service", label="In Service", width=0.12),
        InServiceColumn(name="name"),
#        InServiceColumn(
#            name="bus",
#            editor=InstanceEditor(name="buses", editable=False)
#        ),
#        InServiceColumn(name="rating_s"),
#        InServiceColumn(name="rating_v"),
        InServiceFloatColumn(name="p"),
        InServiceFloatColumn(name="q"),
        InServiceFloatColumn(name="q_max"),
        InServiceFloatColumn(name="q_min"),
        InServiceFloatColumn(name="p_cost", editable=False),
        InServiceFloatColumn(name="p_cost_marginal", editable=False),
#        InServiceColumn(name="v_max"),
#        InServiceColumn(name="v_min"),
        InServiceFloatColumn(name="p_max"),
        InServiceFloatColumn(name="p_min"),
        InServiceFloatColumn(name="p_max_bid"),
        InServiceFloatColumn(name="p_min_bid"),
        InServiceFloatColumn(name="p_despatch", editable=False),
#        InServiceColumn(name="p_bid"),
#        InServiceColumn(name="p_cost_fixed"),
#        InServiceColumn(name="p_cost_proportional"),
#        InServiceColumn(name="p_cost_quadratic"),
#        InServiceColumn(name="q_cost_fixed"),
#        InServiceColumn(name="q_cost_proportional"),
#        InServiceColumn(name="q_cost_quadratic"),
#        InServiceColumn(name="rate_up"),
#        InServiceColumn(name="rate_down"),
#        InServiceColumn(name="min_period_up"),
#        InServiceColumn(name="min_period_down"),
#        InServiceColumn(name="initial_period_up"),
#        InServiceColumn(name="initial_period_down"),
#        InServiceColumn(name="c_startup"),
    ],
    show_toolbar=True,
    deletable=True,
    orientation="vertical",
#    edit_view=generator_view,
#    filters=[EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate],
    search=RuleTableFilter(),
    row_factory=generator_factory,
    row_factory_kw={"__table_editor__": ""}
)

#------------------------------------------------------------------------------
#  All generators "TableEditor" instance:
#------------------------------------------------------------------------------

all_generators_table_editor = TableEditor(
    columns = [
        CheckboxColumn(name="in_service", label="In Service", width=0.12),
        InServiceColumn(name="name"),
        InServiceFloatColumn(name="p"),
        InServiceFloatColumn(name="q"),
        InServiceFloatColumn(name="q_max"),
        InServiceFloatColumn(name="q_min"),
        InServiceFloatColumn(name="p_cost", editable=False),
        InServiceFloatColumn(name="p_cost_marginal", editable=False),
        InServiceFloatColumn( name    = "p_max",
                              tooltip = "Maximum real power output rating" ),
        InServiceFloatColumn( name    = "p_min",
                              tooltip = "Minimum real power output rating" ),
        InServiceFloatColumn(name="p_max_bid"),
        InServiceFloatColumn(name="p_min_bid"),
        InServiceFloatColumn(name="p_despatch", editable=False),
    ],
    deletable=False, orientation="horizontal", edit_view=generator_view,
#    filters=[EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate],
    search=RuleTableFilter(),
)

# EOF -------------------------------------------------------------------------
