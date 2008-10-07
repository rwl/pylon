#------------------------------------------------------------------------------
# Copyright (C) 2007 Richard W. Lincoln
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

""" Defines a workbench tree view of resources """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.io.api import File
from enthought.traits.api import Instance
from enthought.traits.ui.api import View, Item, TreeEditor
from enthought.pyface.image_resource import ImageResource
from enthought.pyface.workbench.api import View as WorkbenchView
from enthought.pyface.action.api import MenuManager, Group

from enthought.envisage.ui.workbench.workbench_action_manager_builder import \
    WorkbenchActionManagerBuilder

from resource_tree_node import FileTreeNode

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

ACTION_SETS = "enthought.envisage.ui.workbench.action_sets"

#------------------------------------------------------------------------------
#  "ResourceTreeView" class:
#------------------------------------------------------------------------------

class ResourceTreeView(WorkbenchView):
    """ Defines a workbench tree view of resources """

    #--------------------------------------------------------------------------
    #  "ResourceTreeView" interface:
    #--------------------------------------------------------------------------

    workspace = Instance(File)

    # A builder for the tree context menu
#    action_manager_builder = Instance(WorkbenchActionManagerBuilder)

    # The tree context menu
    context_menu = Instance(MenuManager)

    #--------------------------------------------------------------------------
    #  "IView" interface:
    #--------------------------------------------------------------------------

    # The view's globally unique identifier:
    id = "pylon.plugin.resource.resource_tree_view"

    # The view's name:
    name = "Navigator"

    # The default position of the view relative to the item specified in the
    # "relative_to" trait:
    position = "left"

    # An image used to represent the view to the user (shown in the view tab
    # and in the view chooser etc).
    image = ImageResource("tree")

    # The width of the item (as a fraction of the window width):
    width = 0.2

    # The category sed to group views when they are displayed to the user:
    category = "General"

    #--------------------------------------------------------------------------
    #  "IView" interface:
    #--------------------------------------------------------------------------

    def create_control(self, parent):
        """ Create the view contents """

#        browser = WorkspaceBrowser(window=self.window)
        ui = self.edit_traits(
            parent=parent, view=self._create_view(), kind="subpanel"
        )

        return ui.control

    #--------------------------------------------------------------------------
    #  "ResourceTreeView" interface:
    #--------------------------------------------------------------------------

    def _workspace_default(self):
        """ Trait initialiser """

        # Note that we always offer the service via its name, but look it up
        # via the actual protocol.
        from i_workspace import IWorkspace
        workspace = self.window.application.get_service(IWorkspace)

        return workspace


    def _context_menu_default(self):
        """ Trait initialiser """

        extensions = self.window.application.get_extensions(ACTION_SETS)
        action_sets = [ext(window=self.window) for ext in extensions]

        action_manager_builder = WorkbenchActionManagerBuilder(
            window=self.window, action_sets=action_sets
        )

        context_menu_manager = MenuManager(
            name="Resource", id="pylon.plugin.resource.context_menu"
        )

        action_manager_builder.initialize_action_manager(
            context_menu_manager, "Resource"
        )

        return context_menu_manager


    def _create_view(self):
        """ Create a view with a tree editor """

        view = View(
            Item(
                name="workspace", show_label=False,
                editor=TreeEditor(
                    nodes=[FileTreeNode(menu=self.context_menu)],
                    editable=False, hide_root=True,
                    on_dclick=self._on_dclick,
                    on_select=self._on_select,
                )
            ),
            buttons=["OK", "Cancel"],
            resizable=True,
            width=.3, height=.3
        )

        return view


    def _on_dclick(self, object):
        """ Handle tree nodes being double clicked """

        self.window.edit(object)


    def _on_select(self, object):
        """ Handle tree node selection """

        pass

# EOF -------------------------------------------------------------------------
