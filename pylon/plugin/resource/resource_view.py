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

""" Defines a tree view of resources for the workbench """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.traits.api import Instance, Delegate
from enthought.pyface.action.api import MenuManager, Group
from enthought.pyface.image_resource import ImageResource
from enthought.pyface.workbench.api import View as WorkbenchView

from enthought.envisage.ui.workbench.workbench_action_manager_builder import \
    WorkbenchActionManagerBuilder

from resource import File
from action.open_action import OpenAction

from resource_tree_viewer import \
    ResourceTreeViewer, FileSorter, ResourceTreeLabelProvider, \
    HideHiddenFiles

#from enthought.pyface.action.api import ToolBarManager, Action

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

ACTION_SETS = "enthought.envisage.ui.workbench.action_sets"

#------------------------------------------------------------------------------
#  "ResourceView" class:
#------------------------------------------------------------------------------

class ResourceView(WorkbenchView):
    """ Defines a tree view of resources for the workbench """

    #--------------------------------------------------------------------------
    #  "WorkspaceView" interface:
    #--------------------------------------------------------------------------

    # A view of resources based on a tree control
    tree_viewer = Instance(ResourceTreeViewer)

    # That which is currently selected in the tree
    selection = Delegate("tree_viewer")

    # A builder for the tree context menu
    action_manager_builder = Instance(WorkbenchActionManagerBuilder)

    # The tree context menu
    context_menu = Instance(MenuManager)

    # A tree label provider that uses contributed editor icons
    label_provider = Instance(ResourceTreeLabelProvider)

    #--------------------------------------------------------------------------
    #  "IView" interface:
    #--------------------------------------------------------------------------

    # The view's globally unique identifier:
    id = "pylon.plugin.resource.resource_view"

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

        # Note that we always offer the service via its name, but look it up
        # via the actual protocol.
        from i_workspace import IWorkspace

        workspace = self.window.application.get_service(IWorkspace)

        # Create a tree viewer with the workspace as input
        self.tree_viewer = tree_viewer = ResourceTreeViewer(
            parent, input=workspace,
            label_provider=self.label_provider,
            sorter=FileSorter(),
            filters=[HideHiddenFiles()]
        )

        # Make the TreeViewer a selection provider
        tree_viewer.on_trait_change(self.on_selection_change, "selection")
        # Add a right-click handler for showing the context menu
        tree_viewer.on_trait_change(
            self.on_right_click, "element_right_clicked"
        )
        # Add a double-click handler for opening resources
        tree_viewer.on_trait_change(self.on_double_click, "element_activated")

        return tree_viewer.control

    #--------------------------------------------------------------------------
    #  "ResourceView" interface:
    #--------------------------------------------------------------------------

    def _label_provider_default(self):
        """ Trait initialiser """

        return ResourceTreeLabelProvider(window=self.window)


    def _action_manager_builder_default(self):
        """ Trait initialiser """

        extensions = self.window.application.get_extensions(ACTION_SETS)
        action_sets = [factory(window=self.window) for factory in extensions]

        action_manager_builder = WorkbenchActionManagerBuilder(
            window=self.window, action_sets=action_sets
        )

        return action_manager_builder


    def _context_menu_default(self):
        """ Trait initialiser """

        context_menu_manager = MenuManager(
            name="Resource", id="pylon.plugin.resource.context_menu"
        )

        self.action_manager_builder.initialize_action_manager(
            context_menu_manager, "Resource"
        )

        return context_menu_manager


    def on_selection_change(self, new):
        """ Sets the workbench window's currently selected item """

        self.window.selection = new


    def on_right_click(self, event):
        """ Handles displaying the context menu on right-click """

        element, (x, y) = event
        parent = self.tree_viewer.control
        self.context_menu.create_menu(parent).show(x, y)


    def on_double_click(self, element):
        """ Opens a file resource in the default editor """

        if element.is_file:
            OpenAction(window=self.window).perform(None)
            self.window.selection = self.tree_viewer.selection
        elif element.is_folder:
            from i_workspace import IWorkspace
            workspace = self.window.application.get_service(IWorkspace)
            workspace.path = element.absolute_path

            self.tree_viewer.refresh(workspace)
        else:
            pass

# EOF -------------------------------------------------------------------------
