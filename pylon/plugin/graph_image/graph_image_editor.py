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

""" Graph image editor """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from os.path import join, dirname

from enthought.pyface.image_resource import ImageResource
from enthought.plugins.workspace.resource_editor import ResourceEditor
from enthought.preferences.api import bind_preference

from pylon.ui.graph.graph_image import GraphImage

import pylon.ui.api

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

IMAGE_LOCATION = dirname(pylon.ui.api.__file__)

#------------------------------------------------------------------------------
#  "GraphImageEditor" class:
#------------------------------------------------------------------------------

class GraphImageEditor(ResourceEditor):
    """ A graph editor for network resources """

    image = ImageResource("graph", search_path=[IMAGE_LOCATION])

    #--------------------------------------------------------------------------
    #  "TraitsUIEditor" interface.
    #--------------------------------------------------------------------------

    def create_ui(self, parent):
        """ Creates the traits UI that represents the editor """

        self.document = document = self.provider.create_document(self.obj)

        g = GraphImage(network=document)

        self._bind_preferences(g)

        ui = g.edit_traits(parent=parent, kind="subpanel")

        # Dynamic notification of document object modification
        document.on_trait_change(self.on_document_modified)

        return ui

    def _bind_preferences(self, graph_image):
        """ Binds the graph traits to the preferences """

        bind_preference(
            obj=graph_image, trait_name="program",
            preference_path="pylon.graph_image.program"
        )

# EOF -------------------------------------------------------------------------
