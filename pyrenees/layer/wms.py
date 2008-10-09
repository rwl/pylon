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

""" Defines a generic Web Map Service layer """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import string

from urllib2 import HTTPError

from StringIO import StringIO

from enthought.traits.api import \
    HasTraits, String, Int, Float, List, Trait, Instance, Delegate, Event, \
    Tuple, Button, Array, Bool, Range, Default, Property, Enum, Any, Dict, \
    on_trait_change

from enthought.traits.ui.api import \
    View, Item, Group, HGroup, VGroup, InstanceEditor, TableEditor, EnumEditor

from enthought.traits.ui.table_column import ObjectColumn

from enthought.enable.api import Component, Pointer, Canvas, Viewport
from enthought.enable.tools.api import ViewportPanTool
from enthought.enable.component_editor import ComponentEditor
from enthought.kiva.backend_image import Image

from owslib.wms import WebMapService, ServiceException

#------------------------------------------------------------------------------
#  "ServerConnection" class:
#------------------------------------------------------------------------------

class ServerConnection(HasTraits):
    """ Connection to a WMS server """

    # Human readable identifier
    name = String

    # Unique resource locator
    url = String(label="URL")

    # WMS protocol version
    version = String(
        "1.1.1", desc="Currently supports only version 1.1.1 of the WMS protocol"
    )

    # Default view
    traits_view = View(
        Item(name="name"), Item(name="url"),
        Item(name="version", style="readonly"),
        title="Connection details",
        buttons=["OK", "Cancel"], width=0.3
    )

#------------------------------------------------------------------------------
#  "Layer" class:
#------------------------------------------------------------------------------

class ContentLayer(HasTraits):
    """ Defines the structure of a layer of map content """

    # Layer name
    name = String

    # Layer title
    title = String

    # Detailed description of the layer
    abstract = String

    # Bounding box (left, bottom, right, top) in srs units
    bbox = Tuple(Float, Float, Float, Float)

    # Spacial reference system identifier
    srs = String

    # Optional list of named styles
    styles = Dict(String, Dict(String, String))

    # Selected style
    style = String

#------------------------------------------------------------------------------
#  "MapService" class:
#------------------------------------------------------------------------------

class MapService(HasTraits):
    """ A Web Map Service """

    name = String("blapp")

    # Reference to OWSLib map service
    wms = Trait(WebMapService)

    #--------------------------------------------------------------------------
    #  Server connections:
    #--------------------------------------------------------------------------

    # Server connection details
    connection = Instance(ServerConnection)

    # Available connections
    connections = List(Instance(ServerConnection))

    # Connects to the service
    connect = Button("C&onnect")

    # Adds a new connection
    new = Button("&New")

    # Edits the server connection details
    edit = Button("&Edit")

    # Deletes the current connection
    delete = Button("&Delete")

    #--------------------------------------------------------------------------
    #  Capability:
    #--------------------------------------------------------------------------

    # Image encoding
    format = String

    # Available image encoding types
    formats = List(String)

    #--------------------------------------------------------------------------
    #  Layers:
    #--------------------------------------------------------------------------

    # Spatial reference system
    srs = String(desc="spatial reference system")

    # Available spatial reference systems
    systems = List(String)

    # Available map layers
    layers = List(Instance(ContentLayer))

    # Layers selected for addition
    selected_layers = List(Instance(ContentLayer))

    #--------------------------------------------------------------------------
    #  Views:
    #--------------------------------------------------------------------------

    traits_view = View(
        VGroup(
            Group(
                Item(
                    name="connection", show_label=False,
                    editor=InstanceEditor(name="connections", editable=False)
                ),
                HGroup(
                    Item(
                        name="connect", enabled_when="connection is not None",
                        show_label=False
                    ),
                    Item(name="new", show_label=False),
                    Item(
                        name="edit", enabled_when="connection is not None",
                        show_label=False
                    ),
                    Item(
                        name="delete", enabled_when="connection is not None",
                        show_label=False
                    )
                ),
                label="Server connections", show_border=True
            ),
            Group(
                Item(
                    name="format", label="Image encoding",
                    editor=EnumEditor(name="formats")
                ),
                Item(
                    name="srs", label="Reference system",
                    editor=EnumEditor(name="systems"),
                ),
            ),
            Group(
                Item(
                    name="layers", show_label=False,
                    editor=TableEditor(
                        columns=[
                            ObjectColumn(
                                name="name", editable=False, width=0.2
                            ),
                            ObjectColumn(
                                name="title", editable=False, width=0.4
                            ),
                            ObjectColumn(
                                name="abstract", editable=False, width=0.4
                            )
                        ],
                        editable=False, configurable=False, sortable=False,
                        selection_mode="rows", selected="selected_layers",
                        scroll_dy=10
                    )
                ),
                label="Layers", show_border=True
            ),
        ),
        id="pylon.ui.map.map.map_service",
        resizable=True, buttons=["OK", "Cancel"],
        title="Add Layer(s) from a Server",
        height=0.4
    )

    #--------------------------------------------------------------------------
    #  Protected interface:
    #--------------------------------------------------------------------------

    def _connection_default(self):
        """ Trait initialiser """

        if self.connections:
            return self.connections[0]
        else:
            return None


    def _connect_fired(self):
        """ Handles connection """

        connection = self.connection
        if connection is not None:
            try:
                self.wms = WebMapService(connection.url, connection.version)
            except HTTPError:
                print "Invalid URL"
                self.wms = None


    def _new_fired(self):
        """ Handles new connections """

        connection = ServerConnection()
        retval = connection.edit_traits(kind="livemodal")
        if retval.result:
            self.connections.append(connection)


    def _edit_fired(self):
        """ Handles editing server connection details """

        if self.connection is not None:
            self.connection.edit_traits(kind="livemodal")


    def _delete_fired(self):
        """ Handles deletion of connection details """

        conn = self.connection
        if (conn is not None) and (conn in self.connections):
            self.connections.remove(conn)
            conn = None


    def _systems_changed(self, new):
        """ Handles the list of SRS changing """

        if new: self.srs = new[0]


    def _formats_changed(self, new):
        """ Handles the list of image encoding types changing """

        if new: self.format = new[0]


    def _wms_changed(self, new):
        """ Handles new web map service """
        from xml.etree.ElementTree import tostring
        print tostring(new.capabilities)

        fd = open("/tmp/metacarta.xml", "wb")
        fd.write(tostring(new.capabilities))
        fd.close()

        cap = new.capabilities

        # Image encoding
        self.formats = [
            f.text for f in cap.findall("Capability/Request/GetMap/Format")
        ]

        # Spatial reference system
        self.systems = [s.text for s in cap.findall("Capability/Layer/SRS")]

        for layer in cap.findall("Capability/Layer/Layer"):
#            print "LAYER:", tostring(layer)

            # Create a content layer
            content_layer = ContentLayer()
            content_layer.name = layer.findtext("Name")
            content_layer.title = layer.findtext("Title")

            # Layer abstract
            abstract = layer.findtext("Abstract")
            if abstract is not None:
                # Turn paragraph into one long line
                lines = [line.strip() for line in abstract.split("\n")]
                content_layer.abstract = string.join(lines).strip()

            # Bounding box
            bbox = layer.find("LatLonBoundingBox")
            if bbox is not None:
                content_layer.bbox = (
                    float(bbox.get("maxx")), float(bbox.get("maxy")),
                    float(bbox.get("minx")), float(bbox.get("miny"))
                )

            # Layer styles
            styles = {}
            for style in layer.findall("Style"):
                name = style.findtext("Name")
                style_dict = {}
                title = style.findtext("Title")
                if title is not None:
                    style_dict["title"] = title
                styles[name] = style_dict
            content_layer.styles = styles


            # Add to the list of available layers
            self.layers.append(content_layer)

#------------------------------------------------------------------------------
#  Stand-alone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":

    wms_request = "http://labs.metacarta.com/wms-c/tilecache.py?LAYERS=basic&FORMAT=image/png&SERVICE=WMS&VERSION=1.1.1&REQUEST=GetMap&STYLES=&EXCEPTIONS=application/vnd.ogc.se_inimage&SRS=EPSG:4326&BBOX=-90,0,0,90&WIDTH=256&HEIGHT=256"
    worldwind_request = "http://labs.metacarta.com/wms-c/tilecache.py?T=basic&L=5&X=32&Y=23"
    tms_request = "http://labs.metacarta.com/wms-c/tilecache.py/1.0.0/basic/5/32/23.png"

    nasa = ServerConnection(
        name="NASA (JPL)", url="http://wms.jpl.nasa.gov/wms.cgi"
    )
    gmap = ServerConnection(
        name="DM Solutions GMap",
        url="http://www2.dmsolutions.ca/cgi-bin/mswms_gmap"
    )
    lizard = ServerConnection(
        name="Lizardtech server",
        url="http://wms.lizardtech.com/lizardtech/iserv/ows"
    )
    nl = ServerConnection(
        name="NL Tile Server",
#        url="http://tile.openstreetmap.nl/"
        url="http://tile.openstreetmap.org/"
    )
    metacarta = ServerConnection(
        name="MetaCarta Labs",
        url="http://labs.metacarta.com/wms/vmap0"
    )
    worldmap = ServerConnection(
        name="World Map",
        url="http://world.freemap.in/cgi-bin/mapserv?"
    )

    delaware = ServerConnection(
        name="Delaware 2002 Aerial Imagery WMS Service",
        URL="http://datamil.delaware.gov/wmsconnector/com.esri.wms.Esrimap/DE_aerial02"
    )

    bc = ServerConnection(
        name="Ministry of Sustainable Resource Management, British Columbia, Canada",
        url="http://libcwms.gov.bc.ca/wmsconnector/com.esri.wsit.WMSServlet/ogc_layer_service"
    )

    gms = ServerConnection(
        name="GMS Remote Sensing Image Server",
        url="http://www.hondalab.star.ait.ac.th/cgi-bin/thaiwms?"
    )

    service = MapService(connections=[nasa, gmap, lizard, metacarta, worldmap])

    service.configure_traits()

#    map = Map(services=[service])
#
#    img_file = open("/tmp/map.jpg", "rb")
#    tile = Tile(
#        image=img_file, bounds=[512,512], position=[0,0]
#    )
#    map.canvas.add(tile)
#
#    map.configure_traits()
#
#    img_file.close()

#    for layer in service.selected_layers:
#        try:
#            img = service.wms.getmap(
#                layers=[layer.name],
#        #        styles=['visual_bright'],
#                srs=service.srs,
#                bbox=(-112, 36, -106, 42),
#                size=(512, 512),
#                format=service.format,
#                transparent=True
#            )
#        except ServiceException:
#            print "Service denied due to system overload."
#            break

#        img_file = StringIO()
#        img_file.write(img.read())
#
#        tile = Tile(
#            image=img_file, bounds=[512,512], position=[0,0]
#        )
#        map.canvas.add(tile)
#
#    map.configure_traits()

#    out = open("/tmp/map.jpg", "wb")
#    out.write(img.read())
#    out.close()

# EOF -------------------------------------------------------------------------
