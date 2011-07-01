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

from traits.api import Instance, File, Bool, HasTraits, String, Enum

from traitsui.api import \
    View, Handler, UIInfo, Group, Item, TableEditor, InstanceEditor, \
    Label, Tabbed, HGroup, VGroup, ModelView, FileEditor, StatusItem, \
    spring

from traitsui.menu import NoButtons, OKCancelButtons, Separator

from pyface.image_resource import ImageResource

from pypower import loadcase, savecase, ppver, runpf, runopf, rundcopf

from pypower import \
    case4gs, case6ww, case9, case9Q, case14, case24_ieee_rts, case30, \
    case30pwl, case30Q, case39, case57, case118, case300

import pylon
from pylon.case import Case, Preferences
from pylon.view import prefs_view
from pylon.menu import menubar, toolbar
from pylon.tree import case_tree_editor

ICON_LOCATION = join(dirname(pylon.__file__), "images")

FRAME_ICON = ImageResource("frame.ico", search_path=[ICON_LOCATION])


class CaseView(HasTraits):
    case = Instance(Case, Case())

    prefs = Instance(Preferences, Preferences())

    file = File(
        value=expanduser("~"),
        desc="case data location"
    )

    status = Enum('Ready', 'Solving', 'Converged')

    ppver = String
    pycim_ver = String

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
        statusbar=[
            StatusItem(name="status", width=0.5),
#            StatusItem(name="info.ui.title", width=85),
            StatusItem(name='ppver', width=70),
            StatusItem(name="pycim_ver", width=100)
        ],
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

    def _ppver_default(self):
        v = ppver('all')
        return v['Version']


    def on_new(self):
#        if not info.initialized:
#            return

        self.case = Case()


    def on_case4gs(self):
        self.case = Case.from_ppc(case4gs())

    def on_case6ww(self):
        self.case = Case.from_ppc(case6ww())

    def on_case9(self):
        self.case = Case.from_ppc(case9())

    def on_case9Q(self):
        self.case = Case.from_ppc(case9Q())

    def on_case14(self):
        self.case = Case.from_ppc(case14())

    def on_case24_ieee_rts(self):
        self.case = Case.from_ppc(case24_ieee_rts())

    def on_case30(self):
        self.case = Case.from_ppc(case30())

    def on_case30pwl(self):
        self.case = Case.from_ppc(case30pwl())

    def on_case30Q(self):
        self.case = Case.from_ppc(case30Q())

    def on_case39(self):
        self.case = Case.from_ppc(case39())

    def on_case57(self):
        self.case = Case.from_ppc(case57())

    def on_case118(self):
        self.case = Case.from_ppc(case118())

    def on_case300(self):
        self.case = Case.from_ppc(case300())


    def on_open(self, info):
        if not info.initialized:
            return
        retval = self.edit_traits(
            parent=info.ui.control,
            view="file_view"
        )
        if retval.result:
            self.case = Case.from_ppc( loadcase(self.file) )


    def save(self, info):
        if not info.initialized:
            return

        retval = self.edit_traits(
            parent=info.ui.control,
            view="file_view"
        )

        if retval.result:
            savecase(self.file, ppc=self.case.to_ppc())


    def on_preferences(self):
        self.prefs.edit_traits(view=prefs_view)#parent=info.ui.control)


    def on_runpf(self):
        runpf(self.case.to_ppc(), self.prefs.to_ppopt())


    def on_runopf(self):
        runopf(self.case.to_ppc(), self.prefs.to_ppopt())


    def on_rundcopf(self):
        rundcopf(self.case.to_ppc(), self.prefs.to_ppopt())


def main():
    model_view = CaseView()
    model_view.configure_traits()


if __name__ == '__main__':
    main()
