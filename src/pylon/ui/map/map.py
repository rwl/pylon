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

""" An WMS map viewer for Pylon """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from math import pow

from enthought.traits.api import \
    HasTraits, String, Int, Float, List, Instance, Bool, Range, Enum, \
    Callable, Dict, on_trait_change

from enthought.traits.ui.api import \
    View, Item, Group, HGroup, VGroup, InstanceEditor

from enthought.enable.api import Component, Pointer, Canvas, Viewport
from enthought.enable.tools.api import ViewportPanTool
from enthought.enable.component_editor import ComponentEditor

from pylon.ui.map.layer.i_layer import ILayer

#------------------------------------------------------------------------------
#  "Map" class:
#------------------------------------------------------------------------------

class Map(HasTraits):
    """ Viewer of map layers """

    #--------------------------------------------------------------------------
    #  Trait definitions:
    #--------------------------------------------------------------------------

    # Number of zoom levels
    n_zoom_level = Int(19)

    # Range of zoom levels FIXME: Dynamic 'high' trait
    zoom_level = Range(low=0, high=19, value=0, auto_set=False)

    # Available map layers
    layer_types = List(Callable)

    # Base layer type selected from the list of available types
    base_layer_type = Callable

    #--------------------------------------------------------------------------
    #  Enable traits:
    #--------------------------------------------------------------------------

    # Base map layer to which overlays are applied
    base_layer = Instance(ILayer)

    # Base layers mapped according to zoom level
    levels = Dict(Int, Instance(ILayer))

    # A view into a sub-region of the base layer
    viewport = Instance(Viewport)

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    # Default view
    traits_view=View(
        VGroup(
#            Item(
#                name="base_layer_type",
#                editor=InstanceEditor(name="layer_types", editable=False)
#            ),
            Group(
                Item(
                    name="viewport", show_label=False,
                    editor=ComponentEditor(), id=".map_viewport"
                ),
                Group(Item(name="zoom_level"))
            )
        ),
        id="pylon.ui.map.map", title="Map",
        resizable=True, width=.6, height=.5
    )

    #--------------------------------------------------------------------------
    #  Trait initialisers:
    #--------------------------------------------------------------------------

    def _base_layer_type_default(self):
        """ Trait initialiser """

        if self.layer_types:
            return self.layer_types[0]
        else:
            return None


    def _base_layer_default(self):
        """ Trait initialiser """

        if self.levels:
            return self.levels[self.zoom_level]
        else:
            return None


    def _levels_default(self):
        """ Trait initialiser """

        levels = {}
        for i in range(self.n_zoom_level):
            levels[i] = self.base_layer_type()

        return levels


    def _viewport_default(self):
        """ Trait initialiser """

        pos = [0,0]
        vp = Viewport(
            component=self.base_layer, enable_zoom=False,
            view_position=pos
        )
        vp.tools.append(ViewportPanTool(vp))

        return vp

    #--------------------------------------------------------------------------
    #  Dynamic event handlers:
    #--------------------------------------------------------------------------

    def _base_layer_type_changed(self, new):
        """ Handles selection of a new base layer type """

        for i in range(self.n_zoom_level):
            levels[i] = new()


    def _n_zoom_level_changed(self, new):
        """ Handles the number of zoom levels changing """

        levels = {}
        for i in range(new):
            levels[i] = self.base_layer_type()

        self.levels = levels


    def _levels_changed(self, new):
        """ Handles the dictionary of stored levels changing """

        self.base_layer = new[self.zoom_level]


    def _zoom_level_changed(self, new):
        """ Handles the map zoom level """

        self.base_layer = self.levels[new]

#        map_size = pow(2, new) * self.base_layer.resolution
#        x, y = self.viewport.view_position
#        zoomed_x = x + (map_size/2)
#        zoomed_y = y + (map_size/2)
#        print "MOVING FROM (%f, %f) TO (%f, %F)" % (x, y, zoomed_x, zoomed_y)
#        self.viewport.view_position = [zoomed_x, zoomed_y]


    def _base_layer_changed(self, new):
        """ Handles the currently viewed canvas """

        self.viewport.component = new
        self.viewport.request_redraw()


    @on_trait_change("viewport.view_position")
    def on_view_position_change(self):

        vp = self.viewport

        pos = vp.view_position
        width = vp.width
        height = vp.height

        map.base_layer.zoom_level=self.zoom_level
        self.base_layer.add_tiles(pos, width, height)

        vp.request_redraw()

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    from pylon.ui.map.layer.osm import OSM

    map = Map(layer_types=[OSM])
    map.configure_traits()

# EOF -------------------------------------------------------------------------
