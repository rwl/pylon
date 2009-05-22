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

""" Pylon graph editor extensions.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import dirname, join

from enthought.pyface.api import ImageResource
from puddle.resource.editor import Editor

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = join(dirname(__file__), "..", "..", "ui", "images")

#------------------------------------------------------------------------------
#  "GraphEditorExtension" class:
#------------------------------------------------------------------------------

class GraphEditorExtension(Editor):
    """ Associates a graph editor with *.pkl files.
    """

    # The object contribution's globally unique identifier.
    id = "pylon.plugins.graph.graph_editor"

    # A name that will be used in the UI for this editor
    name = "Graph Editor"

    # An icon that will be used for all resources that match the
    # specified extensions
    image = ImageResource("dot", search_path=[IMAGE_LOCATION])

    # The contributed editor class
    editor_class = "pylon.plugin.graph.graph_editor:GraphEditor"

    # The list of file types understood by the editor
    extensions = [".pkl"]

    # If true, this editor will be used as the default editor for the type
    default = False

# EOF -------------------------------------------------------------------------
