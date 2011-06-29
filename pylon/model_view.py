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

from os.path import join, dirname, expanduser

from traits.api import Instance, File, Bool, HasTraits

from traitsui.api import \
    View, Handler, UIInfo, Group, Item, TableEditor, InstanceEditor, \
    Label, Tabbed, HGroup, VGroup, ModelView, FileEditor, StatusItem, \
    spring

from traitsui.menu import NoButtons, OKCancelButtons, Separator

from pyface.image_resource import ImageResource

import pylon
from pylon.case import Case
from pylon.menu import menubar, toolbar
from pylon.tree import case_tree_editor

ICON_LOCATION = join(dirname(pylon.__file__), "images")

FRAME_ICON = ImageResource("frame.ico", search_path=[ICON_LOCATION])


class CaseView(HasTraits):
    case = Instance(Case, Case())

    file = File(
        value=expanduser("~"),
        desc="case data location"
    )

    traits_view = View(
        Item(
            name="case",
            editor=case_tree_editor,
            show_label=False,
            id=".tree_editor",
            width=.2,
        ),
        id="case_vm.view",
        title="Pylon",
#        icon=FRAME_ICON,
        resizable=True,
        style="custom",
    #    buttons=NoButtons,
        width=.5,
        height=.5,
        kind="live",
        buttons=NoButtons,
        menubar=menubar,
        toolbar=toolbar,
#        statusbar=[
#            StatusItem(name="file", width=0.5),
#            StatusItem(name="info.ui.title", width=85)
#        ],
#        dock="vertical"
    )

    file_view = View(
        Item(
            name="file",
            id="data_file",
            label="File",
#            editor=FileEditor(entries=6)
        ),
        id="case_mv.file_view",
        title="Select a file",
#        icon=FRAME_ICON,
        resizable=True,
        style="simple",
        width=.3,
        kind="livemodal",
        buttons=OKCancelButtons
    )


def main():
    model_view = CaseView()
    model_view.configure_traits()


if __name__ == '__main__':
    main()
