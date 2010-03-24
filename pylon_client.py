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
from pyjamas.JSONService import JSONProxy


class Pylon:
    def __init__(self):
        self.remote_case = CaseService()

        self.base_panel = VerticalPanel()
        self.tab_panel = TabPanel()
        self.base_panel.add(self.tab_panel)
        self.tab_panel.add(self.get_case_panel(), "Case")
        self.tab_panel.add(self.get_buses_panel(), "Buses")
        self.tab_panel.selectTab(0)
        self.status = Label()
        self.base_panel.add(self.status)
        RootPanel().add(self.base_panel)


    def get_case_panel(self):
        panel = VerticalPanel()
        title = HTML("""Case""")
        panel.add(title)
        tree = self.get_case_tree()
        panel.add(tree)
        return panel


    def get_case_tree(self):
        tree = self.tree = Tree()
        case_item = TreeItem("Case_1")
        tree.addItem(case_item)
        buses = self.buses = TreeItem("Buses")
        case_item.addItem(buses)
        id = self.remote_case.buses("name", self)
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

    # JSON handler interface --------------------------------------------------

    # The handler object should implement
    #     onRemoteResponse(value, requestInfo)
    # to accept the return value of the remote method, and
    #     onRemoteError(code, error_dict, requestInfo)
    #          code = http-code or 0
    #          error_dict is an jsonrpc 2.0 error dict:
    #              {
    #                'code': jsonrpc-error-code (integer) ,
    #                'message': jsonrpc-error-message (string) ,
    #                'data' : extra-error-data
    #              }
    # to handle errors.

    def onRemoteResponse(self, response, request_info):
        print "RESPONSE:", response
#        self.tree.clear()
        self.buses.removeItems()
        for bus_name in response:
            proto = Proto(str(bus_name))
            self.create_item(proto)
            self.buses.addItem(proto.item)


    def onRemoteError(self, code, errobj, request_info):
        print "ERROR:", errobj['message']

        message = errobj['message']
        if code != 0:
            self.status.setText("HTTP error %d: %s" % (code, message))
        else:
            code = errobj['code']
            self.status.setText("JSONRPC Error %s: %s" % (code, message))


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


class CaseService(JSONProxy):
    def __init__(self):
        JSONProxy.__init__(self, "/json", ["buses"])


if __name__ == "__main__":
    # For pyjd, set up a web server and load the HTML from there.
    pyjd.setup("http://0.0.0.0:8080/static/pylon.html")
#    pyjd.setup("public/pylon.html")
    app = Pylon()
    pyjd.run() # dummy in pyjs

# EOF -------------------------------------------------------------------------
