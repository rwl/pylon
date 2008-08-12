#-------------------------------------------------------------------------------
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
#-------------------------------------------------------------------------------

""" An Mapnik viewer for Pylon """

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from enthought.traits.api import \
    HasTraits, String, Int, Float, List, Trait, Instance, Delegate, Event, \
    Tuple, Button, Array, Bool, Range, Default, Property, Enum, Any, File

from enthought.traits.ui.api import \
    View, Item, Group, HGroup, VGroup

from enthought.traits.ui.wx.editor import \
    Editor

from enthought.traits.ui.wx.basic_editor_factory import \
    BasicEditorFactory

from enthought.kiva import Canvas

from enthought.kiva.agg import GraphicsContextArray

#from enthought.kiva.backend_image import Image
import enthought.kiva.backend_image as kiva

from enthought.enable.api import Component, Pointer

from enthought.enable.wx_backend.api import Window

from enthought.traits.ui.menu import OKCancelButtons, NoButtons

from mapnik import \
    Map, Color, Layer, Shapefile, Rule, Filter, Stroke, Style, \
    Envelope, PolygonSymbolizer, render_to_file, Image, render, rawdata, \
    PostGIS, load_map

import wx

from os import path

import shutil

import numpy

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

ICONS_LOCATION = 'icons'
DATA_LOCATION = 'data'
MAP_IMAGE_FILE_PATH = "/tmp/sigis.png"

WIDTH = 800
HEIGHT = 600

#-------------------------------------------------------------------------------
#  'MapnikMap' class:
#-------------------------------------------------------------------------------

class MapnikMap(HasTraits):
    ''' Traits wrapper around Mapnik's Map class.
    '''

    #---------------------------------------------------------------------------
    #  Trait definitions:
    #---------------------------------------------------------------------------

    # Parent network
    network = Instance('pylon.ui.network_vm.NetworkViewModel')

    m = Instance(Map)

    layers = List(Layer)

    updated = Event

    # Default view:
    traits_view = View(
        Item(name='m',
             editor=MapnikMapEditor(),
             show_label=False),
        id='pylon.map.MapnikMap',
        title = 'Map',
        resizable = True,
        style='custom',
        buttons = NoButtons)

    #---------------------------------------------------------------------------
    #  Initialise object:
    #---------------------------------------------------------------------------

    def __init__(self, network):
        self.network = network

    #---------------------------------------------------------------------------
    #  Default map instance:
    #---------------------------------------------------------------------------

    def _m_default(self):
        m = Map(WIDTH, HEIGHT, "+proj=latlong +ellps=WGS84")
        m.background = Color("white")

        load_map(m, path.join(DATA_LOCATION, 'osm-roads.xml'))

#        m.zoom_to_box(Envelope(1405120.04127408,
#                               -247003.813399447,
#                               1706357.31328276,
#                               -25098.593149577))

#        m.zoom_to_box(Envelope(-1000000.0, 7500000.0, -500000, 8500000))

        m.zoom_to_box(Envelope(-700000.0, 7600000.0, -300000, 7800000))

        return m

    def _layers_items_changed(self, event):
        for lyr in event.added:
            self.m.layers.append(lyr)
        for lyr in event.removed:
            self.m.layers.remove(lyr)

#-------------------------------------------------------------------------------
#  'MapnikMapCanvas' class:
#-------------------------------------------------------------------------------

class MapnikMapCanvas(Canvas):
    def __init__(self, m, parent, id=-1, size=wx.DefaultSize):
        Canvas.__init__(self, parent, id, size=size)
        self.parent = parent
        self.m = m
        self.gca = GraphicsContextArray((100, 100))
        #self.img = wx.NullBitmap
        return

    def load_image(self):
        w, h = self.parent.GetSize()

        buf = Image(WIDTH, HEIGHT)
        ren = render(self.m, buf)

        #render_to_file(self.m, MAP_IMAGE_FILE_PATH, "png")
        #self.img = kiva.Image(MAP_IMAGE_FILE_PATH)

        #img = wx.ImageFromData(WIDTH, HEIGHT, rawdata(buf))
        #self.bmp = wx.BitmapFromBufferRGBA(WIDTH, HEIGHT, rawdata(buf))

        map_string = numpy.fromstring(rawdata(buf), dtype=numpy.uint8)

        map_colours = map_string.reshape((HEIGHT*WIDTH, 4))

        red = map_colours[:, 0].reshape((HEIGHT, WIDTH))
        green = map_colours[:, 1].reshape((HEIGHT, WIDTH))
        blue = map_colours[:, 2].reshape((HEIGHT, WIDTH))
        alpha = map_colours[:, 3].reshape((HEIGHT, WIDTH))

#        ARGB4 = numpy.array([A, R, G, B])
#        ARGB = numpy.ndarray(shape=(HEIGHT, WIDTH, 4), dtype=numpy.uint8)
#        ARGB[:,:,0] = ARGB4[0,:,:]
#        ARGB[:,:,1] = ARGB4[1,:,:]
#        ARGB[:,:,2] = ARGB4[2,:,:]
#        ARGB[:,:,3] = ARGB4[3,:,:]

        argb = numpy.dstack((alpha, red, green, blue)).copy()

        self.gca = GraphicsContextArray(argb, pix_format="argb32")
        self.dirty = 1
        self.Refresh()

    def do_draw(self, gc):

        w = gc.width()
        h = gc.height()
        img_w = self.gca.width()
        img_h = self.gca.height()
        gc.draw_image(self.gca, ((w/2)-(img_w/2), (h/2)-(img_h/2), img_w, img_h))

#-------------------------------------------------------------------------------
#  'MapnikMapComponent' class:
#-------------------------------------------------------------------------------

class MapnikMapComponent(Component):
    m = Instance(MapnikMap)

    normal_pointer = Pointer("arrow")
    moving_pointer = Pointer("hand")

    def __init__(self, bounds, position, padding, m):
        Component.__init__(self,
                           bounds=bounds,
                           position=position,
                           padding=padding)
        self.m = m

        # A blank GraphicsContextArray
        self.gca = GraphicsContextArray((100, 100))

        self.bgcolor = 'transparent'

#    def update(self, m):
#        self.m = m
#
#        #w, h = self.parent.GetSize()
#        w = self.gc.width()
#        h = self.gc.height()
#
#        buf = Image(WIDTH, HEIGHT)
#        ren = render(self.m, buf)
#
#        map_string = numpy.fromstring(rawdata(buf), dtype=numpy.uint8)
#
#        map_colours = map_string.reshape((HEIGHT*WIDTH, 4))
#
#        red = map_colours[:, 0].reshape((HEIGHT, WIDTH))
#        green = map_colours[:, 1].reshape((HEIGHT, WIDTH))
#        blue = map_colours[:, 2].reshape((HEIGHT, WIDTH))
#        alpha = map_colours[:, 3].reshape((HEIGHT, WIDTH))
#
#        argb = numpy.dstack((alpha, red, green, blue)).copy()
#
#        self.gca = GraphicsContextArray(argb, pix_format="argb32")
#        self.dirty = 1
#        self.request_redraw()

    def _draw_mainlayer(self, gc, view_bounds=None, mode="normal"):

        gc.save_state()

        x, y = self.position

        w = gc.width()
        h = gc.height()

        buf = Image(w, h)
        ren = render(self.m.m, buf)

        map_string = numpy.fromstring(rawdata(buf), dtype=numpy.uint8)

        map_colours = map_string.reshape((h*w, 4))

        red = map_colours[:, 0].reshape((h, w))
        green = map_colours[:, 1].reshape((h, w))
        blue = map_colours[:, 2].reshape((h, w))
        alpha = map_colours[:, 3].reshape((h, w))

        argb = numpy.dstack((alpha, red, green, blue)).copy()

        self.gca = GraphicsContextArray(argb, pix_format="argb32")

        img_w = self.gca.width()
        img_h = self.gca.height()

        gc.draw_image(self.gca)#, (x+(w/2-img_w/2), y+(h/2-img_h/2), img_w, img_h))

        gc.restore_state()

        self.m.m.updated = True
        return

    def normal_left_down(self, event):
        self.event_state = "moving"
        event.window.set_pointer(self.moving_pointer)
        self.offset_x = event.x - self.x
        self.offset_y = event.y - self.y
        return

    def normal_right_down(self, event):
        self.m.m.zoom(0.5)
        self.request_redraw()
        return

    def moving_mouse_move(self, event):
        self.position = [event.x-self.offset_x, event.y-self.offset_y]
        #self.request_redraw()
        return

    def moving_left_up(self, event):
        self.event_state = "normal"
        event.window.set_pointer(self.normal_pointer)
        self.request_redraw()
        return

    def moving_mouse_leave(self, event):
        self.moving_left_up(event)
        return

#-------------------------------------------------------------------------------
#  '_MapnikMapEditor' class:
#-------------------------------------------------------------------------------

class _MapnikMapEditor(Editor):
    scrollable = True

    map_component = Instance(MapnikMapComponent)

    def init(self, parent):
        self.control = wx.Panel(parent, -1, style=wx.CLIP_CHILDREN)
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.control.SetSizer(self._sizer)

        #self._figure = MapnikMapCanvas(self.value, self.control)
        #self._sizer.Add(self._figure, 1, wx.EXPAND)

        self.map_component = MapnikMapComponent(bounds=[100,100],
                                          position=[100,200],
                                          padding=5,
                                          m=self.value)
        self._figure = Window(self.control, -1, component=self.map_component)

        self._sizer.Add(self._figure.control, 1, wx.EXPAND)

        self.set_tooltip()

        #
        # Listen for the 'updated' trait of the Graph to change
        #
        self.value.on_trait_change(self.update_editor, 'updated')

    def update_editor(self):

        #self.map_component.update(self.value)

        self.control.Layout()

        #self._figure.component.request_redraw()

#-------------------------------------------------------------------------------
#  'MapnikMapTraitsEditor' class:
#-------------------------------------------------------------------------------

class MapnikMapEditor(BasicEditorFactory):
    klass = _MapnikMapEditor

#---------------------------------------------------------------------------
#  Standalone call:
#---------------------------------------------------------------------------

if __name__ == "__main__":
    mm = mm()

    # Canadian Provinces (Polygons)

#    provpoly_lyr = Layer('Provinces')
#    provpoly_lyr.datasource = Shapefile(file=path.join(DATA_LOCATION,
#                                                       'boundaries'),
#                                        encoding='latin1')
#
#    provpoly_style = Style()
#
#    provpoly_rule_on = Rule()
#
#    provpoly_rule_on.filter = Filter("[NAME_EN] = 'Ontario'")
#
#    provpoly_rule_on.symbols.append(PolygonSymbolizer(Color(250, 190, 183)))
#    provpoly_style.rules.append(provpoly_rule_on)
#
#    provpoly_rule_qc = Rule()
#    provpoly_rule_qc.filter = Filter("[NAME_EN] = 'Quebec'")
#    provpoly_rule_qc.symbols.append(PolygonSymbolizer(Color(217, 235, 203)))
#    provpoly_style.rules.append(provpoly_rule_qc)
#
#    mm.m.append_style("provinces", provpoly_style)
#
#    provpoly_lyr.styles.append("provinces")
#
#    #mm.layers.append(provpoly_lyr)
#
#    # OSM roads
#
#    roads = Layer("Roads")
#
#    roads.datasource = PostGIS(type="postgis",
#                               host="/var/run/postgresql",
#                               #port="5433",
#                               user="rwl",
#                               dbname="gis",
#                               #password="blapp",
#                               table="SELECT * from planet_osm_roads order by z_order")
#
#    roads_style = Style()
#
#    roads_motorway_level_4_5_rule = Rule()
#    roads_motorway_level_4_5_rule.filter = Filter("[highway] = 'motorway' or [highway] = 'motorway_link'")
#
#    mm.layers.append(roads)

    load_map(mm.m, path.join(DATA_LOCATION, 'osm-roads.xml'))

    mm.m.zoom_to_box(Envelope(-1000000.0, 7500000.0, -500000, 8500000))
    #mm.m.zoom_to_box(Envelope(-200000.0, 7500000.0, -400000, 7800000))

    mm.configure_traits(view=mm_view)
