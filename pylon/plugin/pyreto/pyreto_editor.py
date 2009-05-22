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

""" Pyreto editors.
"""

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import dirname, join

from enthought.traits.api import on_trait_change
from enthought.traits.ui.api import View, Group, Item, HGroup, VGroup, Tabbed
from enthought.pyface.api import ImageResource

from puddle.resource.editor import Editor
from puddle.resource.resource_editor import ResourceEditor

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = join(dirname(__file__), "..", "..", "ui", "images")

#------------------------------------------------------------------------------
#  "PyretoPlotEditor" class:
#------------------------------------------------------------------------------

class PyretoPlotEditor(ResourceEditor):
    """ Defines a workbench editor for editing an experiment resource with
        interactive plots.
    """

    #--------------------------------------------------------------------------
    #  "TraitsUIEditor" interface:
    #--------------------------------------------------------------------------

    def create_ui(self, parent):
        """ Creates the traits UI that represents the editor.
        """
        self.document = input = self.editor_input.load()
        ui = input.edit_traits(parent=parent, kind="subpanel")

        return ui

    #--------------------------------------------------------------------------
    #  "ResourceEditor" interface
    #--------------------------------------------------------------------------

    @on_trait_change("document.+")
    def on_experiment_modified(self):
        """ Handle modification to the experiment.
        """
        self.dirty = True

#------------------------------------------------------------------------------
#  "PyretoPlotEditorExtension" class:
#------------------------------------------------------------------------------

class PyretoPlotEditorExtension(Editor):
    """ Associates a table editor with *.pkl files.
    """

    # The object contribution's globally unique identifier.
    id = "pylon.plugins.pyreto.pyreto_plot_editor"

    # A name that will be used in the UI for this editor
    name = "Pyreto Plot Editor"

    # An icon that will be used for all resources that match the
    # specified extensions
    image = ImageResource("plot", search_path=[IMAGE_LOCATION])

    # The contributed editor class
    editor_class = "pylon.plugin.pyreto.pyreto_editor:PyretoPlotEditor"

    # The list of file types understood by the editor
    extensions = [".pkl"]

    # If true, this editor will be used as the default editor for the type
    default = True

# EOF -------------------------------------------------------------------------
