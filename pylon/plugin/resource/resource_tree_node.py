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

""" Defines a tree node for file objects """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import basename

from enthought.io.api import File

from enthought.traits.api import HasTraits, Str, List, Instance, Float

from enthought.traits.ui.api import \
    TreeEditor, TreeNode, View, Item, VSplit, HGroup, Handler, Group

#------------------------------------------------------------------------------
#  "FileTreeNode" class:
#------------------------------------------------------------------------------

class FileTreeNode(TreeNode):
    """ A tree node for a file object """

    #--------------------------------------------------------------------------
    # "TreeNode" interface:
    #--------------------------------------------------------------------------

    def allows_children(self, obj):
        """ Return True if this object allows children """

        if obj.is_folder:
            return True
        else:
            return False


    def has_children(self, obj):
        """ Returns True if this object has children """

        return bool(obj.children)


    def get_children(self, obj):
        """ Get the object's children """

        folders = [file for file in obj.children if file.is_folder]
        files = [file for file in obj.children if file.is_file]

        shown = [
            file for file in folders+files if
            basename(file.absolute_path)[0] is not "."
        ]

        return shown


    def get_label(self, obj):
        """ Get the object's label """

        return obj.name+obj.ext


    def is_node_for(self, obj):
        """ Return whether this is the node for a specified object """

        return isinstance(obj, File)


    def get_view(self, object):
        """ Gets the view to use when editing an object """

        view = View(
            Item(name="absolute_path", style="readonly"),
            Item(name="mime_type", style="readonly"),
            Item(name="url", style="readonly"),
        )

        return view


#    def get_icon ( self, object, is_expanded ):
#        """ Returns the icon for a specified object """
#
#        if not self.allows_children( object ):
#            return self.icon_item
#
#        if is_expanded:
#            return self.icon_open
#
#        return self.icon_group
#
#
#    def get_icon_path ( self, object ):
#        """ Returns the path used to locate an object's icon """
#
#        return self.icon_path

# EOF -------------------------------------------------------------------------
