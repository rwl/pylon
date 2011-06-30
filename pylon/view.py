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

from os import path

from traits.api import \
    HasTraits, Instance, List, File, Property, Bool, String, Any

from traitsui.api import \
    View, Group, Item, InstanceEditor, Tabbed, TreeEditor, \
    TreeNode, Label, VGroup, HGroup, spring, RangeEditor

from traitsui.menu import \
    NoButtons, OKCancelButtons, OKButton, CancelButton, HelpButton

from pyface.image_resource import ImageResource

from pylon.table import \
    bus_table_editor, branch_table_editor, gen_table_editor, \
    cost_table_editor, area_table_editor

#FRAME_ICON = ImageResource("frame.ico")

case_view = View(
    VGroup(
        Item(name="base_mva", label="Base MVA", style="simple")
    ),
    id="pylon.view.case_view",
    buttons=OKCancelButtons
)

case_table_view = View(
    VGroup(
        Item(name="base_mva", label="Base MVA", style="simple"),
        Tabbed(
            Group(
                Item(
                    name="buses", show_label=False,
                    editor=bus_table_editor,
                    id=".case_buses_table"
                ),
                label="Buses",
#                dock="tab"
            ),
            Group(
                Item(
                    name="generators", show_label=False,
                    editor=gen_table_editor,
                    id=".case_generators_table"
                ),
                label="Generators"
            ),
            Group(
                Item(
                    name="branches", show_label=False,
                    editor=branch_table_editor,
                    id=".case_branches_table"
                ),
                label="Branches",
#                dock="tab"
            ),
            Group(
                Item(
                    name="areas", show_label=False,
                    editor=area_table_editor,
                    id=".case_loads_table"
                ),
                label="Areas"
            ),
            Group(
                Item(
                    name="costs", show_label=False,
                    editor=cost_table_editor,
                    id=".case_costs_table"
                ),
                label="Costs"
            ),
            dock="tab"
        ),
    ),
    id="pylon.view.case_tab_view",
#    icon=FRAME_ICON,
    resizable=True,
    style="custom", kind="livemodal", buttons=OKCancelButtons,
#    width=.81, height=.81
)

buses_view = View(
    Item(
        name="buses", show_label=False,
        editor=bus_table_editor,
        id=".buses_table"
    ),
    id="pylon.view.buses_view",
    style="custom"
)

generators_view = View(
    Item(
        name="generators", show_label=False,
        editor=gen_table_editor,
        id=".generators_table"
    ),
    id="pylon.view.generators_view",
    style="custom"
)

branches_view = View(
    Item(
        name="branches", show_label=False,
        editor=branch_table_editor,
        id=".branches_table"
    ),
    id="pylon.view.branches_view",
    style="custom"
)

areas_view = View(
    Item(
        name="areas", show_label=False,
        editor=area_table_editor,
        id=".areas_table"
    ),
    id="pylon.view.areas_view",
    style="custom"
)

costs_view = View(
    Item(
        name="costs", show_label=False,
        editor=cost_table_editor,
        id=".costs_table"
    ),
    id="pylon.view.costs_view",
    style="custom"
)

bus_view = View(
    Item(name="bus_i"),
    Item(name="bus_type"),
    Item(name="bus_i"),
    '_',
    Item(name="Pd"),
    Item(name="Qd"),
    Item(name="Gs"),
    Item(name="Bs"),
    '_',
    Item(name="bus_area"),
    Item(name="zone"),
    '_',
    Item(name="Vm"),
    Item(name="Va"),
    Item(name="base_kV"),
    Item(name="Vmax"),
    Item(name="Vmin"),
    '_',
    Item(name="lam_P", style='readonly'),
    Item(name="lam_Q", style='readonly'),
    Item(name="mu_Vmax", style='readonly'),
    Item(name="mu_Vmin", style='readonly')
)

gen_view = View(
    Item(name="gen_bus"),
    '_',
    Item(name="Pg"),
    Item(name="Qg"),
    Item(name="Qmax"),
    Item(name="Qmin"),
    Item(name="Pmax"),
    Item(name="Pmin"),
    '_',
    Item(name="Vg"),
    Item(name="mBase"),
    Item(name="gen_status"),
    '_',
    Item(name="Pc1"),
    Item(name="Pc2"),
    Item(name="Qc1min"),
    Item(name="Qc1max"),
    Item(name="Qc2min"),
    Item(name="Qc2max"),
    '_',
    Item(name="mu_Pmax", style='readonly'),
    Item(name="mu_Pmin", style='readonly'),
    Item(name="mu_Qmax", style='readonly'),
    Item(name="mu_Qmin", style='readonly')
)

branch_view = View(
    Item(name="fbus"),
    Item(name="t_bus"),
    "_",
    Item(name="br_r"),
    Item(name="br_x"),
    Item(name="br_b"),
    "_",
    Item(name="rate_a"),
    Item(name="tap"),
    Item(name="shift"),
    Item(name="br_status"),
    Item(name="angmin"),
    Item(name="angmax"),
    "_",
    Item(name="Pf", style='readonly'),
    Item(name="Qf", style='readonly'),
    Item(name="Pt", style='readonly'),
    Item(name="Qt", style='readonly'),
    "_",
    Item(name="mu_Sf", style='readonly'),
    Item(name="mu_St", style='readonly'),
    Item(name="mu_angmin", style='readonly'),
    Item(name="mu_angmax", style='readonly')
)

area_view = View(
    Item(name="area_i"),
    Item(name="price_ref_bus")
)

cost_view = View(
    Item(name="mode"),
    Item(name="startup"),
    Item(name="shutdown"),
    Item(name="ncost"),
    Item(name="cost"),
)

prefs_view = View(
    Tabbed(
        Group(
            Item(name="pf_alg", label='Algorithm', enabled_when='pf_dc==False'),
            Item(name="pf_tol", label='Tolerance', enabled_when='pf_dc==False'),
            Group(
                Item(name="pf_max_it",
                    label='Newton\'s method',
                    enabled_when='pf_alg=="Newton\'s method" and pf_dc==False'),
                Item(name="pf_max_it_fd",
                    label='Fast-Decoupled',
                    enabled_when='pf_alg=="Fast-Decoupled (XB version)" or pf_alg=="Fast-Decoupled (BX version)" and pf_dc==False'),
                Item(name="pf_max_it_gs",
                    label='Gauss Seidel',
                    enabled_when='pf_alg=="Gauss Seidel" and pf_dc==False'),
                show_border=True,
                label='Maximum iterations'
            ),
            Item(name="enforce_q_lims", enabled_when='pf_dc==False'),
            Item(name="pf_dc", label='DC'),
            label="Power Flow",
        ),
        Group(
            Item(name="opf_alg", label='Algorithm'),
            Item(name="opf_poly2pwl_pts", editor=RangeEditor(low=2, high=100, mode='spinner')),
            Item(name="opf_violation"),
            Item(name="opf_flow_lim"),
            Item(name="opf_ignore_ang_lim"),
            Item(name="opf_alg_dc"),
            label="OPF",
        ),
        Group(
            Item(name="verbose"),
            Item(name="out_all"),
            Item(name="out_sys_sum"),
            Item(name="out_area_sum"),
            Item(name="out_bus"),
            Item(name="out_branch"),
            Item(name="out_gen"),
            Group(
                Item(name="out_all_lim", label='All'),
                Item(name="out_v_lim", label='Bus voltage'),
                Item(name="out_line_lim", label='Line flow'),
                Item(name="out_pg_lim", label='Pg limit'),
                Item(name="out_qg_lim", label='Qg limit'),
                show_border=True,
                label='Constraint info'
            ),
            Item(name="out_raw"),
            Item(name="return_raw_der"),
            label="Output",
        ),
        Group(
            Group(
                Item(name="pdipm_feastol", label='Fesibility (equality)'),
                Item(name="pdipm_gradtol", label='Gradient'),
                Item(name="pdipm_comptol", label='Complementary (inequality)'),
                Item(name="pdipm_costtol", label='Optimality'),
                show_border=True,
                label='Tolerances'
            ),
            Item(name="pdipm_max_it"),
            Item(name="scpdipm_red_it", editor=RangeEditor(low=1, high=100, mode='spinner')),
            label="PDIPM",
        ),
    ),
    id="pylon.view.prefs_view",
#    icon=FRAME_ICON,
    resizable=False,
    title='Preferences',
#    style="custom",
    kind="livemodal", buttons=[OKButton, CancelButton, HelpButton],
#    width=.81, height=.81
)
