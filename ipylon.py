# Copyright (C) 2010 Richard Lincoln
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Pyjamas frontend for Pylon. """

import pyjd # dummy in pyjs
from pyjamas.ui.RootPanel import RootPanel
from pyjamas.ui.Label import Label
from pyjamas.ui.Button import Button
from pyjamas.ui.HTML import HTML
from pyjamas.ui.ListBox import ListBox
from pyjamas.ui.Tree import Tree
from pyjamas.ui.TreeItem import TreeItem
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.FormPanel import FormPanel
from pyjamas.ui.FileUpload import FileUpload
from pyjamas.ui.TabPanel import TabPanel
from pyjamas.ui.decoratorpanel import DecoratedTabPanel, DecoratorPanel
from pyjamas.ui.decoratorpanel import DecoratorTitledPanel
from pyjamas import Window


class IPylon:
    def __init__(self, case=None):
        self.case = self.get_default_case() if case is None else case
        self.base_panel = HorizontalPanel()
        self.tab_panel = TabPanel()
        self.tab_panel.add(self.get_case_panel(), "Case")
        self.tab_panel.add(self.get_buses_panel(), "Buses")
        self.tab_panel.selectTab(0)
        self.base_panel.add(self.tab_panel)
        RootPanel().add(self.base_panel)


    def get_default_case(self):
        return None#Case()


    def get_case_panel(self):
        panel = VerticalPanel()
        title = HTML("""Case""")
        panel.add(title)
        tree = self.get_case_tree()
        panel.add(tree)
        return panel


    def get_case_tree(self):
        tree = Tree()
        case_item = TreeItem("Case_1")
        tree.addItem(case_item)
        buses = TreeItem("Buses")
        case_item.addItem(buses)
#        for bus in self.case.buses:
        for n in ["Bus_1", "Bus_2"]:
#            proto = Proto(bus.name)
            proto = Proto(n)
            self.create_item(proto)
            buses.addItem(proto.item)
        return tree


    def create_item(self, proto):
        proto.item = TreeItem(proto.text)
        proto.item.setUserObject(proto)
        if len(proto.children) > 0:
            proto.item.addItem(PendingItem())



    def get_buses_panel(self):
        panel = VerticalPanel()
        title = HTML("""Buses""")
        panel.add(title)
        return panel


class Proto:
    def __init__(self, text, children=None):
        self.children = []
        self.item = None
        self.text = text

        if children is not None:
            self.children = children


class PendingItem(TreeItem):
    def __init__(self):
        TreeItem.__init__(self, "Please wait...")

    def isPendingItem(self):
        return True


if __name__ == "__main__":
    pyjd.setup("public/ipylon.html")
    app = IPylon()
    pyjd.run() # dummy in pyjs

# EOF -------------------------------------------------------------------------