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

from traits.ui.api import TreeEditor, TreeNode, View, Item

from pylon.case import Case, Bus, Generator, Branch, Cost

no_view = View()

network_tree_editor = TreeEditor(
    nodes=[
        TreeNode(
            node_for=[Case],
            auto_open=True, children="", label="name",
            view=minimal_view,
        ),
        TreeNode(
            node_for=[Case], auto_open=True,
            children="buses", label="=Buses",
            view=buses_view, add=[Bus]
        ),
        TreeNode(
            node_for=[Case], auto_open=True,
            children="branches", label="=Branches",
            view=branches_view,
        ),
        TreeNode(
            node_for=[Case], auto_open=False,
            children="generators", label="=_generators",
            view=all_generators_view,
        ),
        TreeNode(
            node_for=[Case], auto_open=False,
            children="loads", label="=_loads",
            view=all_loads_view
        ),
        TreeNode(
            node_for=[Bus], label="name", view=bus_view
        ),
        TreeNode(
            node_for=[Bus], children="generators", label="=Generators",
            view=generators_view, add=[Generator]
        ),
        TreeNode(
            node_for=[Bus], children="loads", label="=Loads",
            view=loads_view, add=[Load]
        ),
        TreeNode(
            node_for=[Branch], auto_open=True, label="name",
            view=branch_view
        ),
        TreeNode(
            node_for=[Generator], label="name", view=generator_view
        ),
        TreeNode(
            node_for=[Load], label="name", view=load_view
        ),
    ],
    orientation="horizontal"
)