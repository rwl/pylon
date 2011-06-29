# Copyright (C) 2011 Richard Lincoln
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from traitsui.api import TableEditor, InstanceEditor

from traitsui.table_column import ObjectColumn, ExpressionColumn
from traitsui.extras.checkbox_column import CheckboxColumn

from traitsui.table_filter import \
    EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate, RuleTableFilter

from pylon.case import Bus, Generator, Branch, Area, Cost


def bus_factory(**row_factory_kw):
    if "__table_editor__" in row_factory_kw:
        case = row_factory_kw["__table_editor__"].object
        del row_factory_kw["__table_editor__"]
        bus = Bus()
        bus.bus_i = len(case.buses)
        return bus


def gen_factory(**row_factory_kw):
    if "__table_editor__" in row_factory_kw:
        case = row_factory_kw["__table_editor__"].object
        del row_factory_kw["__table_editor__"]
        gen = Generator()
        gen.gen_bus = len(case.buses)
        return gen


def branch_factory(**row_factory_kw):
    if "__table_editor__" in row_factory_kw:
        case = row_factory_kw["__table_editor__"].object
        branch = Branch()
        branch.f_bus = case.buses[0].bus_i
        branch.t_bus = case.buses[1].bus_i
        del row_factory_kw["__table_editor__"]
        return branch


class GenColumn(ObjectColumn):
    width = 0.08
    horizontal_alignment = "center"

    def get_text_color ( self, object ):
        return ["light grey", "black"][object.gen_status]


class BranchColumn(ObjectColumn):
    width = 0.08
    horizontal_alignment = "center"

    def get_text_color ( self, object ):
        return ["light grey", "black"][object.br_status]


bus_table_editor = TableEditor(
    columns = [
        ObjectColumn(name="bus_i"),
        ObjectColumn(name="bus_type"),
        ObjectColumn(name="Pd"),
        ObjectColumn(name="Qd"),
        ObjectColumn(name="Gs"),
        ObjectColumn(name="Bs"),
        ObjectColumn(name="Vm"),
        ObjectColumn(name="Va"),
        ObjectColumn(name="Vmax"),
        ObjectColumn(name="Vmin"),
        ObjectColumn(name="bus_area"),
        ObjectColumn(name="zone"),
        ObjectColumn(name="base_kV"),
        ObjectColumn(name="lam_P", editable=False),
        ObjectColumn(name="lam_Q", editable=False),
        ObjectColumn(name="mu_Vmax", editable=False),
        ObjectColumn(name="mu_Vmin", editable=False)
    ],
    deletable=True,
    orientation="horizontal",
    show_toolbar=True,
#    edit_view=bus_view,
#    filters=[EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate],
    search=RuleTableFilter(),
    row_factory=bus_factory,
    row_factory_kw={"__table_editor__": ""}
)


gen_table_editor = TableEditor(
    columns = [
        GenColumn(name="gen_bus"),
        GenColumn(name="Pg"),
        GenColumn(name="Qg"),
        GenColumn(name="Qmax"),
        GenColumn(name="Qmin"),
        GenColumn(name="Pmax"),
        GenColumn(name="Pmin"),
        GenColumn(name="Vg"),
        GenColumn(name="mBase"),
        CheckboxColumn(name="gen_status", width=0.12),
        GenColumn(name="Pmax"),
        GenColumn(name="Pmin"),
        GenColumn(name="Pc1"),
        GenColumn(name="Pc2"),
        GenColumn(name="Qc1min"),
        GenColumn(name="Qc1max"),
        GenColumn(name="Qc2min"),
        GenColumn(name="Qc2max"),
        GenColumn(name="mu_Pmax", editable=False),
        GenColumn(name="mu_Pmin", editable=False),
        GenColumn(name="mu_Qmax", editable=False),
        GenColumn(name="mu_Qmin", editable=False)
    ],
    deletable=True,
    orientation="vertical",
#    edit_view=generator_view,
#    filters=[EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate],
    search=RuleTableFilter(),
    row_factory=gen_factory,
    row_factory_kw={"__table_editor__": ""}
)


branch_table_editor = TableEditor(
    columns = [
        BranchColumn(name="f_bus", label="From"),
        BranchColumn(name="t_bus", label="To"),
        BranchColumn(name="br_r", label="R"),
        BranchColumn(name="br_x", label="X"),
        BranchColumn(name="br_b", label="Bc"),
        BranchColumn(name="rate_a", label="Rate"),
        BranchColumn(name="tap", label="Tap Ratio"),
        BranchColumn(name="shift", label="Phase Shift"),
        CheckboxColumn(name="br_status", label="Status"),
        BranchColumn(name="angmin", label="Min Angle"),
        BranchColumn(name="angmax", label="Max Angle"),
        BranchColumn(name="Pf", editable=False),
        BranchColumn(name="Qf", editable=False),
        BranchColumn(name="Pt", editable=False),
        BranchColumn(name="Qt", editable=False),
        BranchColumn(name="mu_Sf", label="mu Sf", editable=False),
        BranchColumn(name="mu_St", label="mu St", editable=False),
        BranchColumn(name="mu_angmin", label="mu Max Angle", editable=False),
        BranchColumn(name="mu_angmax", label="mu Min Angle", editable=False)
    ],
    deletable=True,
    orientation="horizontal",
#    edit_view=branch_view,
#    filters=[EvalFilterTemplate, MenuFilterTemplate, RuleFilterTemplate],
    search=RuleTableFilter(),
    row_factory=branch_factory,
    row_factory_kw={"__table_editor__": ""}
)


area_table_editor = TableEditor(
    columns = [
        ObjectColumn(name="area_i"),
        ObjectColumn(name="price_ref_bus")
    ],
    deletable=True
)


cost_table_editor = TableEditor(
    columns = [
        ObjectColumn(name="mode"),
        ObjectColumn(name="startup"),
        ObjectColumn(name="shutdown"),
        ObjectColumn(name="ncost"),
        ObjectColumn(name="cost")
    ],
    deletable=True
)
