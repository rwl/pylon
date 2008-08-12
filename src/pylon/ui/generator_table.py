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

#------------------------------------------------------------------------------
#  Generator factory function:
#------------------------------------------------------------------------------

def generator_factory(**row_factory_kw):
    """
    Require one or more Bus for instantiation

    """

    if "__table_editor__" in row_factory_kw:
        bus = row_factory_kw["__table_editor__"].object

        g_names = [g.name for g in bus.generators]
        name = make_unique_name("g", g_names)

        del row_factory_kw["__table_editor__"]

        return Generator(name=name)

#------------------------------------------------------------------------------
#  "GeneratorColumn" class:
#------------------------------------------------------------------------------

class GeneratorColumn(ObjectColumn):
    """
    A specialised column to set the text color differently
    based upon whether or not the generator is in service

    """

    width = 0.08

    horizontal_alignment = "center"

    def get_text_color ( self, object ):
        return ["light grey", "black"][object.in_service]

#------------------------------------------------------------------------------
#  Generators "TableEditor" instance:
#------------------------------------------------------------------------------

generators_table_editor = TableEditor(
    columns = [
        CheckboxColumn(name="in_service", label="In Service", width=0.12),
        GeneratorColumn(name="name"),
#        GeneratorColumn(
#            name="bus",
#            editor=InstanceEditor(name="buses", editable=False)
#        ),
#        GeneratorColumn(name="rating_s"),
#        GeneratorColumn(name="rating_v"),
        GeneratorColumn(name="p"),
        GeneratorColumn(name="q"),
        GeneratorColumn(name="q_max"),
        GeneratorColumn(name="q_min"),
        GeneratorColumn(name="p_cost", editable=False),
#        GeneratorColumn(name="v_max"),
#        GeneratorColumn(name="v_min"),
#        GeneratorColumn(name="p_max_bid"),
#        GeneratorColumn(name="p_min_bid"),
#        GeneratorColumn(name="p_bid"),
#        GeneratorColumn(name="p_cost_fixed"),
#        GeneratorColumn(name="p_cost_proportional"),
#        GeneratorColumn(name="p_cost_quadratic"),
#        GeneratorColumn(name="q_cost_fixed"),
#        GeneratorColumn(name="q_cost_proportional"),
#        GeneratorColumn(name="q_cost_quadratic"),
#        GeneratorColumn(name="rate_up"),
#        GeneratorColumn(name="rate_down"),
#        GeneratorColumn(name="min_period_up"),
#        GeneratorColumn(name="min_period_down"),
#        GeneratorColumn(name="initial_period_up"),
#        GeneratorColumn(name="initial_period_down"),
#        GeneratorColumn(name="cost_startup"),
    ],
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
        GeneratorColumn(name="name"),
        GeneratorColumn(name="p"),
        GeneratorColumn(name="q"),
        GeneratorColumn(name="q_max"),
        GeneratorColumn(name="q_min"),
        GeneratorColumn(name="p_cost", editable=False),
    ],
    deletable=False, orientation="horizontal",# edit_view=generator_view,
#    filters=[EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate],
    search=RuleTableFilter(),
)

# EOF -------------------------------------------------------------------------
