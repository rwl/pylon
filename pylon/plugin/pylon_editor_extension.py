#------------------------------------------------------------------------------
# Copyright (C) 2008 Richard W. Lincoln
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

""" Pylon editor extensions """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import dirname

from enthought.pyface.api import ImageResource
from enthought.plugins.workspace.editor import Editor

import pylon.ui.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = dirname(pylon.ui.api.__file__)

#------------------------------------------------------------------------------
#  "PylonTableEditorExtension" class:
#------------------------------------------------------------------------------

class PylonTableEditorExtension(Editor):
    """ Associates a table editor with *.pyl files """

    # The object contribution's globally unique identifier.
    id = "pylon.plugins.pylon_table_editor"

    # A name that will be used in the UI for this editor
    name = "Table Editor"

    # An icon that will be used for all resources that match the
    # specified extensions
    image = ImageResource("table", search_path=[IMAGE_LOCATION])

    # The contributed editor class
    editor_class = "pylon.plugin.pylon_table_editor:PylonTableEditor"

    # The list of file types understood by the editor
    extensions = [".pyl"]

    # If true, this editor will be used as the default editor for the type
    default = False

#------------------------------------------------------------------------------
#  "PylonTreeEditorExtension" class:
#------------------------------------------------------------------------------

class PylonTreeEditorExtension(Editor):
    """ Associates a tree editor with *.pyl files """

    # The object contribution's globally unique identifier.
    id = "pylon.plugins.pylon_table_editor"

    # A name that will be used in the UI for this editor
    name = "Tree Editor"

    # An icon that will be used for all resources that match the
    # specified extensions
    image = ImageResource("tree", search_path=[IMAGE_LOCATION])

    # The contributed editor class
    editor_class = "pylon.plugin.pylon_tree_editor:PylonTreeEditor"

    # The list of file types understood by the editor
    extensions = [".pyl"]

    # If true, this editor will be used as the default editor for the type
    default = True

#------------------------------------------------------------------------------
#  "PylonPlotEditorExtension" class:
#------------------------------------------------------------------------------

class PylonPlotEditorExtension(Editor):
    """ Associates a plot editor with *.pyl files """

    # The object contribution's globally unique identifier.
    id = "pylon.plugins.pylon_plot_editor"

    # A name that will be used in the UI for this editor
    name = "Plot Editor"

    # An icon that will be used for all resources that match the
    # specified extensions
    image = ImageResource("plot", search_path=[IMAGE_LOCATION])

    # The contributed editor class
    editor_class = "pylon.plugin.pylon_plot_editor:PylonPlotEditor"

    # The list of file types understood by the editor
    extensions = [".pyl"]

    # If true, this editor will be used as the default editor for the type
    default = False

# EOF -------------------------------------------------------------------------
