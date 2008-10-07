#------------------------------------------------------------------------------
#
#  Copyright (c) 2008, Richard W. Lincoln
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Author: Richard W. Lincoln
#  Date:   12/08/2008
#
#------------------------------------------------------------------------------

""" Defines a tree view of the workspace for the workbench """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from enthought.io.api import File
from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import View, Item, TreeEditor
from enthought.pyface.action.api import MenuManager, Group
from enthought.envisage.ui.workbench.api import WorkbenchWindow

from enthought.envisage.ui.workbench.workbench_action_manager_builder import \
    WorkbenchActionManagerBuilder

from workspace_tree_node import FileTreeNode

#------------------------------------------------------------------------------
#  "WorkspaceBrowser" class:
#------------------------------------------------------------------------------

class WorkspaceBrowser(HasTraits):
    """ Defines a class for browsing a file on the file system.

    Actually, this class exists just because to use a trait editor we have
    to have a trait to edit!

    """

    # The browser's workbench window
    window = Instance(WorkbenchWindow)

    # The file deemed the current workspace
    workspace = Instance(File)

    # A context menu for the files in the workspace
    context_menu = Instance(MenuManager)

    # A default view
    traits_view = View(
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

    def _workspace_default(self):
        """ Trait initialiser """

        # Note that we always offer the service via its name, but look it up
        # via the actual protocol.
        from i_workspace import IWorkspace
        workspace = self.window.application.get_service(IWorkspace)

        return workspace


#    def _action_manager_builder_default(self):
#        """ Trait initialiser """
#
#        extensions = self.window.application.get_extensions(ACTION_SETS)
#        action_sets = [factory(window=self.window) for factory in extensions]
#
#        action_manager_builder = WorkbenchActionManagerBuilder(
#            window=self.window, action_sets=action_sets
#        )
#
#        return action_manager_builder


    def _context_menu_default(self):
        """ Trait initialiser """

        if self.window is not None:
            extensions = self.window.application.get_extensions(ACTION_SETS)
            action_sets = [ext(window=self.window) for ext in extensions]

            action_manager_builder = WorkbenchActionManagerBuilder(
                window=self.window, action_sets=action_sets
            )

            context_menu_manager = MenuManager(
                name="Workspace", id="enthought.plugins.workspace.context_menu"
            )

            action_manager_builder.initialize_action_manager(
                context_menu_manager, "Workspace"
            )
        else:
            context_menu_manager = None

        return context_menu_manager


    def _on_dclick(self, object):
        """ Handle tree nodes being double clicked """

        if self.window is not None:
            self.window.edit(object)


    def _on_select(self, object):
        """ Handle tree node selection """

        pass

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

#if __name__ == "__main__":
#
#    browser = WorkspaceBrowser(workspace=File("/tmp"))
#    browser.configure_traits()

# EOF -------------------------------------------------------------------------
