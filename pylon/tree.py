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

from traitsui.api import TreeEditor, TreeNode, View

from pylon.case import Case, Bus, Generator, Branch, Area, Cost

from pylon.view import \
    case_view, buses_view, generators_view, branches_view, areas_view, \
    costs_view, bus_view, gen_view, branch_view, area_view, cost_view

no_view = View()

case_tree_editor = TreeEditor(
    nodes=[
        TreeNode(
            node_for=[Case],
            auto_open=True, children="", label="=Case",
            view=case_view,
        ),

        TreeNode(
            node_for=[Case], auto_open=False,
            children="buses", label="=Buses",
            view=buses_view, add=[Bus]
        ),
        TreeNode(
            node_for=[Case], auto_open=False,
            children="branches", label="=Branches",
            view=branches_view, add=[Branch],
        ),
        TreeNode(
            node_for=[Case], auto_open=False,
            children="generators", label="=Generators",
            view=generators_view, add=[Generator],
        ),
        TreeNode(
            node_for=[Case], auto_open=False,
            children="areas", label="=Areas",
            view=areas_view, add=[Area],
        ),
        TreeNode(
            node_for=[Case], auto_open=False,
            children="costs", label="=Costs",
            view=costs_view, add=[Cost],
        ),

        TreeNode(
            node_for=[Bus], label="bus_i", view=bus_view
        ),
        TreeNode(
            node_for=[Generator], label="gen_bus", view=gen_view
        ),
        TreeNode(
            node_for=[Branch], label="f_bus", view=branch_view
        ),
        TreeNode(
            node_for=[Area], label="area_i", view=area_view
        ),
        TreeNode(
            node_for=[Cost], label="", view=cost_view
        )
    ],
    orientation="horizontal"
)
