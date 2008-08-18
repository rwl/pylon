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
#  Date:   09/07/2008
#
#------------------------------------------------------------------------------

""" Defines a workspace tree viewer """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os import listdir

from os.path import basename, dirname, isdir, join, expanduser

from enthought.io.api import File
from enthought.traits.api import Instance, List
from enthought.pyface.api import ImageResource, ApplicationWindow, GUI
from enthought.pyface.action.api import MenuManager, Action, ToolBarManager
from enthought.envisage.ui.workbench.workbench_window import WorkbenchWindow
from enthought.plugins.workspace.editor import Editor

from enthought.pyface.viewer.api import \
    TreeContentProvider, TreeLabelProvider, ViewerFilter, \
    TreeViewer, ViewerSorter

from workspace_resource import Project, Workspace

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

EDITORS = "enthought.plugins.workspace.editors"

#------------------------------------------------------------------------------
#  "HideHiddenFiles" class:
#------------------------------------------------------------------------------

class HideHiddenFiles(ViewerFilter):
    """ A viewer filter that allows only files and folders that haves names
    that do not start with a "." """

    def select(self, viewer, parent, element):
        """ Returns True if the element is 'allowed' (ie. NOT filtered).

        'viewer'  is the viewer that we are filtering elements for.
        'parent'  is the parent element.
        'element' is the element to select.

        """

        return basename(element.absolute_path)[0] is not "."

#------------------------------------------------------------------------------
#  "FileSorter" class:
#------------------------------------------------------------------------------

class FileSorter(ViewerSorter):
    """ A sorter that arranges folders before files. """

    def category(self, viewer, parent, element):
        """ Returns the category (an integer) for an element.

        'parent'   is the parent element.
        'elements' is the element to return the category for.

        Categories are used to sort elements into bins.  The bins are
        arranged in ascending numeric order.  The elements within a bin
        are arranged as dictated by the sorter's 'compare' method.

        """

        if element.is_folder:
            category = 0
        else:
            category = 1

        return category

#------------------------------------------------------------------------------
#  "WorkspaceTreeContentProvider" class:
#------------------------------------------------------------------------------

class WorkspaceTreeContentProvider(TreeContentProvider):
    """ Defines a workspace tree content provider """

    #--------------------------------------------------------------------------
    #  "TreeContentProvider" interface.
    #--------------------------------------------------------------------------

    def get_parent(self, element):
        """ Returns the parent of an element. """

        return dirname(element.absolute_path)


    def get_children(self, element):
        """ Returns the children of an element. """

#        visible = [c for c in element.children
#                 if (basename(c.path)[0] is not ".") and (c.exists)]
#
#        return visible

        return element.children


    def has_children(self, element):
        """ Returns True iff the element has children, otherwise False. """

#        if element.is_folder:
#            visible = [c for c in element.children
#                     if (basename(c.path)[0] is not ".") and (c.exists)]
#        else:
#            visible = []
#
#        return bool(visible)

        if element.is_folder:
            return bool(len(element.children))
        else:
            return False

#------------------------------------------------------------------------------
#  "WorkspaceTreeLabelProvider" class:
#------------------------------------------------------------------------------

class WorkspaceTreeLabelProvider(TreeLabelProvider):
    """ Defines a workspace tree label provider """

    # The image used to represent folders that are NOT expanded.
    CLOSED_FOLDER = ImageResource('closed_folder')

    # The image used to represent folders that ARE expanded.
    OPEN_FOLDER = ImageResource('open_folder')

    # The image used to represent documents (ie. NON-'folder') elements.
    DOCUMENT = ImageResource('document')

    #--------------------------------------------------------------------------
    #  "WorkspaceTreeLabelProvider" interface
    #--------------------------------------------------------------------------

    # A window reference to allow retrieval of editor icons
    window = Instance(WorkbenchWindow)

    # Editor extensions
    editors = List(Instance(Editor))

    #--------------------------------------------------------------------------
    #  "TreeLabelProvider" interface
    #--------------------------------------------------------------------------

    def get_image(self, viewer, element):
        """ Returns the filename of the label image for an element. """

        selected = viewer.is_selected(element)
        expanded = viewer.is_expanded(element)

        if element.is_folder:
            if expanded:
                image = self.OPEN_FOLDER
            else:
                image = self.CLOSED_FOLDER
        else:
            for editor in self.editors:
                # FIXME: Give a default editor preference
                if element.ext in editor.extensions:
                    image = editor.image
                    break
            else:
                image = self.DOCUMENT

        return image


    def get_text(self, viewer, element):
        """ Returns the label text for an element. """

        return element.name+element.ext

    #--------------------------------------------------------------------------
    #  "WorkspaceTreeLabelProvider" interface
    #--------------------------------------------------------------------------

    def _editors_default(self):
        """ Trait initialiser """

        if self.window is not None:
            editors = self.window.application.get_extensions(EDITORS)
            return [factory() for factory in editors]
        else:
            return []

#------------------------------------------------------------------------------
#  "WorkspaceTreeViewer" class:
#------------------------------------------------------------------------------

class WorkspaceTreeViewer(TreeViewer):
    """ A tree viewer for local file systems. """

    #--------------------------------------------------------------------------
    #  "TreeViewer" interface
    #--------------------------------------------------------------------------

    # The content provider provides the actual tree data.
    content_provider = Instance(WorkspaceTreeContentProvider, ())

    # The label provider provides, err, the labels for the items in the tree
    # (a label can have text and/or an image).
    label_provider = Instance(WorkspaceTreeLabelProvider, ())

    # Selection mode (must be either of 'single' or 'extended').
    selection_mode = "single"

    # Should the root of the tree be shown?
#    show_root = False


    def refresh(self, element):#=None):
        """ Refresh the tree starting from the specified element.

        Call this when the STRUCTURE of the content has changed.

        """

        # Refresh from the root if no element specified
#        if element is None:
#            pid = self.control.GetRootItem()
#            data = self.control.GetPyData(pid)
#            if data is not None:
#                populated, element = data

        # Has the element actually appeared in the tree yet?
        pid = self._element_to_id_map.get(self._get_key(element), None)
        if pid is not None:
            # The item data is a tuple.  The first element indicates whether or
            # not we have already populated the item with its children.  The
            # second element is the actual item data.
            populated, element = self.control.GetPyData(pid)#

            # If an element is expanded and is not collapsed before we continue
            # then the pizza slice points down, but no children are displayed.
            # The node then has to be manually collapsed and then expanded.
            self.control.Collapse(pid)

            # fixme: We should find a cleaner way other than deleting all of
            # the element's children and re-adding them!
            self._delete_children(pid)
            self.control.SetPyData(pid, (False, element))

            # Does the element have any children?
            has_children = self.content_provider.has_children(element)
            self.control.SetItemHasChildren(pid, has_children)

            # Expand it.
            self.control.Expand(pid)

        else:
            print '**** pid is None!!! ****'

        return


    def _delete_children(self, pid):
        """ Recursively deletes the children of the specified element. """

        cookie = 0

#        (cid, cookie) = self.control.GetFirstChild(pid, cookie) # Obsolete
        (cid, cookie) = self.control.GetFirstChild(pid)
        while cid.IsOk():
            # Recursively delete the child's children.
            self._delete_children(cid)

            # Remove the reference to the item's data.
            populated, element = self.control.GetPyData(cid)
            del self._element_to_id_map[self._get_key(element)]
            self.control.SetPyData(cid, None)

            # Next!
            (cid, cookie) = self.control.GetNextChild(pid, cookie)

        self.control.DeleteChildren(pid)

        return

    #--------------------------------------------------------------------------
    #  "WorkspaceTreeViewer" interface
    #--------------------------------------------------------------------------

    def _element_right_clicked_changed(self, event):
        """ Forces selection of the item under the cursor on right click """

        element, point = event

        wx_item, flags = self.control.HitTest(point)
        self.control.SelectItem(wx_item)

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":

    class WorkspaceTreeViewerWindow(ApplicationWindow):

        def __init__(self, **traits):
            # Base class constructor.
            super(WorkspaceTreeViewerWindow, self).__init__(**traits)

            # Add a tool bar.
            self.tool_bar_manager = ToolBarManager(
                Action(name="Refresh", on_perform=self.refresh_tree),
                Action(name="Update", on_perform=self.update_tree)
            )

            return

        def _create_contents(self, parent):
            """ Creates the window contents. """

            self.tree_viewer = tree_viewer = WorkspaceTreeViewer(
                parent, input=File(expanduser("~")),
                sorter=FileSorter()
            )

            return tree_viewer.control

        def refresh_tree(self):
            """ Refreshes the tree viewer """

            if self.tree_viewer.selection:
                selected = self.tree_viewer.selection[0]
                self.tree_viewer.refresh(selected)

        def update_tree(self):
            """ Updates the tree viewer """

            if self.tree_viewer.selection:
                selected = self.tree_viewer.selection[0]
                self.tree_viewer.update(selected)

    # Create the GUI (this does NOT start the GUI event loop).
    gui = GUI()

    # Create and open the main window.
    window = WorkspaceTreeViewerWindow(size=(300, 600), position=(200,200))
    window.open()

    # Start the GUI event loop!
    gui.start_event_loop()

# EOF -------------------------------------------------------------------------
