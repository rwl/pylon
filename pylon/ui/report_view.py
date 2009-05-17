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

""" Defines views for readonly traits """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import \
    HasTraits, Int, Float, Range, Tuple, List, Instance, Str

from enthought.traits.ui.api import \
    View, Item, Group, HGroup, VGroup, TableEditor, Spring, Label, Tabbed

from enthought.traits.ui.table_column import ObjectColumn

#------------------------------------------------------------------------------
#  Power flow report:
#------------------------------------------------------------------------------

bus_pf_data_columns  = [
    ObjectColumn(name="name"),
    ObjectColumn(name="v_amplitude", label="Mag(pu)"),
    ObjectColumn(name="v_phase", label="Ang(deg)"),
    ObjectColumn(name="p_supply"),
    ObjectColumn(name="q_supply"),
    ObjectColumn(name="p_demand"),
    ObjectColumn(name="q_demand")
]
bus_pf_data_table = TableEditor(columns=bus_pf_data_columns, editable=False)

branch_data_table = TableEditor(
    columns=[
        ObjectColumn(name="name"),
        ObjectColumn(name="source_bus", label="Source",
            format_func=lambda obj: obj.name),
        ObjectColumn(name="target_bus", label="Target",
            format_func=lambda obj: obj.name),
        ObjectColumn(name="p_source"),
        ObjectColumn(name="q_source"),
        ObjectColumn(name="p_target"),
        ObjectColumn(name="q_target"),
        ObjectColumn(name="p_losses"),
        ObjectColumn(name="q_losses")
    ],
    editable=False
)

gen_pf_data_columns = [
    ObjectColumn(name="name"),
    ObjectColumn(name="online"),
    ObjectColumn(name="name"),
    ObjectColumn(name="p"),
    ObjectColumn(name="q"),
]
gen_pf_data_table = TableEditor(columns=gen_pf_data_columns, editable=False)

how_many_group = VGroup(
    ["n_buses", "n_generators", "n_committed_generators", "n_loads",
    "n_fixed", "n_despatchable", "n_shunts", "n_branches", "n_transformers",
    "n_inter_ties", "n_areas"],
    label="How many?", show_border=True
)

#how_much_group = VGroup(
#    ["pq_label", "total_gen_capacity", "online_capacity", "generation_actual",
#     "load", "fixed", "despatchable", "shunt",
#     "total_inter_tie_flow"],
#     label="How much?", show_border=True
#)

how_much_group = VGroup(
#    HGroup(
#        Item("total_p_gen_capacity", label="Total Gen Capacity"),
#        Item("total_q_gen_capacity", show_label=False), springy=True
#    ),
    ["total_gen_capacity", "online_capacity", "generation_actual",
     "load", "fixed_load", "despatchable_load", "shunt_injection",
     "losses", "branch_charging", "total_inter_tie_flow"],
     label="How much?", show_border=True, springy=True
)

minmax_group = Group(
    Item("min_voltage_amplitude"), Item("max_voltage_amplitude"),
    Item("min_voltage_phase"), Item("max_voltage_phase"), springy=True
)

pf_report_view = View(
    Tabbed(
        HGroup(
            how_many_group, how_much_group, minmax_group,
            label="System Summary"
        ),
        Group(
            Item("buses", editor=bus_pf_data_table, show_label=False),
            label="Bus Data"
        ),
        Group(
            Item(name="branches", editor=branch_data_table, show_label=False),
            label="Branch Data"
        ),
        Group(
            Item(name="all_generators", editor=gen_pf_data_table,
                show_label=False),
            label="Generator Data"
        ),
        dock="tab"
    ),
    style="readonly", title="Power Flow Report",
    buttons=["OK", "Help"], resizable=True,
    id="pylon.ui.pf_report_view"
)

#------------------------------------------------------------------------------
#  Optimal power flow report:
#------------------------------------------------------------------------------

bus_opf_data_columns = bus_pf_data_columns + [
    ObjectColumn(name="p_lambda"),
    ObjectColumn(name="q_lambda")
]

bus_opf_data_table = TableEditor(
    columns=bus_opf_data_columns,
    editable=False
)

opf_report_view = View(
    VGroup(
        HGroup(how_many_group, how_much_group),
        VGroup(
            Item(name="buses", editor=bus_opf_data_table, show_label=False),
            Item(name="branches", editor=branch_data_table, show_label=False)
        )
    ),
    style="readonly", title="Optimal Power Flow",
    buttons=["OK", "Help"], resizable=True,
    id="pylon.ui.opf_report_view"
)

if __name__ == "__main__":
    from pylon.api import Network
    Network().configure_traits(view=pf_report_view)

# EOF -------------------------------------------------------------------------
