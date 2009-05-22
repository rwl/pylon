#------------------------------------------------------------------------------
# Copyright (C) 2009 Richard W. Lincoln
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

""" Defines a table editor for Pylon resources.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance
from enthought.traits.ui.api import View, Group, Item, HGroup, VGroup, Tabbed

from puddle.resource.resource_editor import ResourceEditor
from puddle.resource.resource_adapter import PickleFileIResourceAdapter

from pylon.ui.bus_table import buses_table_editor
from pylon.ui.branch_table import branches_table_editor
from pylon.ui.generator_table import all_generators_table_editor
from pylon.ui.load_table import all_loads_table_editor

from pylon.api import Network

#------------------------------------------------------------------------------
#  "PylonTableEditor" class:
#------------------------------------------------------------------------------

class PylonTableEditor(ResourceEditor):
    """ Defines a workbench editor for editing network resources with
        tabular views.
    """

    #--------------------------------------------------------------------------
    #  "TraitsUIEditor" interface
    #--------------------------------------------------------------------------

#    def create_ui(self, parent):
#        """ Creates the traits UI that represents the editor.
#        """
#        resource = PickleFileIResourceAdapter(self.obj)
#        self.document = document = resource.load()
#
#        ui = self.edit_traits(view=self._create_view(), parent=parent,
#            kind="subpanel")
#
#        # Dynamic notification of document object modification
#        document.on_trait_change(self.on_document_modified)
#
#        return ui

    #--------------------------------------------------------------------------
    #  "ResourceEditor" interface
    #--------------------------------------------------------------------------

    def _create_view(self):
        """ Create a view with a tree editor.
        """
        buses_table_editor.on_select = self._on_select

        branches_table_editor.on_select = self._on_select

        all_generators_table_editor.on_select = self._on_select
        all_generators_table_editor.editable = False

        all_loads_table_editor.on_select = self._on_select
        all_loads_table_editor.editable = False

        view = View(
            VGroup(
                HGroup(
                    Item(name="name", style="simple"),
                    Item(name="base_mva", label="Base MVA", style="simple")
                ),
                Tabbed(
                    Group(
                        Item(
                            name="buses", show_label=False,
                            editor=buses_table_editor,
                            id=".network_buses_table"
                        ),
                        label="Buses",
                    ),
                    Group(
                        Item(
                            name="branches", show_label=False,
                            editor=branches_table_editor,
                            id=".network_branches_table"
                        ),
                        label="Branches",
                    ),
                    Group(
                        Item(
                            name="all_generators", show_label=False,
                            editor=all_generators_table_editor,
                            id=".network_generators_table"
                        ),
                        label="All Generators"
                    ),
                    Group(
                        Item(
                            name="all_loads", show_label=False,
                            editor=all_loads_table_editor,
                            id=".network_loads_table"
                        ),
                        label="All Loads"
                    ),
                    dock="tab", scrollable=True, springy=True
                ),
            ),
            id="pylon.plugin.pylon_table_editor.network_view",
            resizable=True, style="custom"
        )

        return view


#    def _view_default(self):
#        """ Trait initialiser.
#        """
#        return View(Item(name="name"))


    def _on_select(self, object):
        """ Handle tree node selection.
        """
        # No properties view for the whole network.
        if isinstance(object, Network):
            self.selected = None
        else:
            self.selected = object

# EOF -------------------------------------------------------------------------
