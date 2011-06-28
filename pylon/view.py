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

from enthought.traits.api import \
    HasTraits, Instance, List, File, Property, Bool, String, Any

from enthought.traits.ui.api import \
    View, Group, Item, InstanceEditor, Tabbed, TreeEditor, \
    TreeNode, Label, VGroup, HGroup, spring

from enthought.traits.ui.menu import NoButtons, OKCancelButtons
from enthought.pyface.image_resource import ImageResource
from enthought.naming.unique_name import make_unique_name

FRAME_ICON = ImageResource("frame.ico")

minimal_view = View(
    Group(
        Item(name="name", style="simple"),
        "_",
        Item(name="mva_base", label="Base MVA", style="simple"),
        Item(name="slack_model", style="readonly"),
        "_",
        Item(name="n_buses", label="Buses", style="readonly"),
    #    Item(name="n_branches", label="Branches", style="readonly"),
        Item(name="n_generators", label="Generators", style="readonly"),
    ),
    id="network_view.minimal_view",
    buttons=OKCancelButtons
)

case_view = View(
    VGroup(
        HGroup(
            Item(name="name", style="simple"),
            Item(name="mva_base", label="Base MVA", style="simple")
        ),
        Tabbed(
            Group(
                Item(
                    name="buses", show_label=False,
                    editor=buses_table_editor,
                    id=".network_buses_table"
                ),
                label="Buses",
#                dock="tab"
            ),
            Group(
                Item(
                    name="branches", show_label=False,
                    editor=branches_table_editor,
                    id=".network_branches_table"
                ),
                label="Branches",
#                dock="tab"
            ),
            Group(
                Item(
                    name="generators", show_label=False,
                    editor=all_generators_table_editor,
                    id=".network_generators_table"
                ),
                label="_generators"
            ),
            Group(
                Item(
                    name="loads", show_label=False,
                    editor=all_loads_table_editor,
                    id=".network_loads_table"
                ),
                label="_loads"
            ),
            dock="tab"
        ),
    ),
    id="pylon.ui.network_view.network_view",
    icon=frame_icon, resizable=True,
    style="custom", kind="livemodal", buttons=OKCancelButtons,
#    width=.81, height=.81
)
