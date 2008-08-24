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

""" Network visualisation using Graphviz """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

import uuid

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from tempfile import gettempdir
from os.path import join, dirname, exists

from enthought.traits.api import \
    HasTraits, Instance, String, Enum, Directory, Property, Bool, \
    cached_property, on_trait_change, Delegate, Event, Any, Trait

from enthought.traits.ui.api import \
    View, Group, HGroup, VGroup, Item, ImageEditor, spring

from enthought.pyface.image_resource import ImageResource
from enthought.enable.api import Component, Container, Viewport
from enthought.enable.tools.api import ViewportPanTool
from enthought.kiva.backend_image import Image

from network_dot import NetworkDot
from graph_editor import GraphEditor

#-----------------------------------------------------------------------------
#  Constants:
#-----------------------------------------------------------------------------

ICON_LOCATION = join(dirname(__file__), "../images")

frame_icon = ImageResource(join(ICON_LOCATION, "frame.ico"))

SPLASH_LOCATION = join(ICON_LOCATION, "python_powered.png")

#------------------------------------------------------------------------------
#  "ImageComponent" class:
#------------------------------------------------------------------------------

class ImageComponent(Component):
    """ Defines a component with an image drawn in the centre """

#    image_path = String(SPLASH_LOCATION)

    image_file = Any#Instance(StringIO)

    #---------------------------------------------------------------------------
    #  Draw component on the graphics context:
    #---------------------------------------------------------------------------

    def _draw_mainlayer(self, gc, view_bounds=None, mode="default"):
#        print "Drawing image component"
        gc.save_state()

        # Create a new Image object for the new file and then make
        # wx repaint the window
#        img = Image(self.image_path)

        self.image_file.seek(0)
        img = Image(self.image_file)

        x = gc.width()/2 - (img.width()/2)
        y = gc.height()/2 - (img.height()/2)

        # Use Image's ability to draw itself onto a gc to paint the window
        gc.draw_image(img, (x, y, img.width(), img.height()))

        gc.restore_state()


    def _image_file_default(self):
        """ Trait initialiser """

        image_file = StringIO()
        fd = open(SPLASH_LOCATION, "rb")
        image_file.write(fd.read())
        fd.close()

        return image_file

#------------------------------------------------------------------------------
#  "GraphImage" class:
#------------------------------------------------------------------------------

class GraphImage(HasTraits):
    """ Representation of a NetworkDot as a simple image """

    # The network being graphed
    network = Instance("pylon.network.Network")#, allow_none=False)

    # The Dot representation of the network
    network_dot = Instance(NetworkDot)

    # A component that draws an image of the dot representation
    image = Instance(ImageComponent)

    # Image format of Graphviz output
    image_format = Trait("PNG", {"PNG": "png", "JPEG": "jpg", "GIF": "gif"})

    # The Graphviz layout program
    program = Enum("dot", "circo", "neato", "twopi", "fdp")

    # A view into the image component
    viewport = Instance(Viewport)

    # The default view
    traits_view = View(
        HGroup(
            Item(name="network", show_label=False),
            Item(name="program", show_label=False),
            Item(name="image_format", show_label=False)
        ),
        Item(
            name="viewport",
            editor=GraphEditor(),
            show_label=False
        ),
        Item(name="network_dot", style="custom", show_label=False),
        id="pylon.ui.graph.graph_image",
        resizable=True
    )

    # A view for configuration of the graph
    config = View(
        Item(name="program"),
#        Item(name="image_dir"),
#        Item(name="image_name"),
        Item(name="image_format"),
#        Item(name="image_path", style="readonly"),
        Item(name="network_dot", style="custom", show_label=False),
        title="Configuration",
        icon=frame_icon,
        buttons=["OK"],
        close_result=True
    )


    def _network_dot_default(self):
        """ Trait initialiser """

        return NetworkDot(network=self.network)


    def _image_default(self):
        """ Trait initialiser """

        return ImageComponent()#image_path=self.image_path)


    def _viewport_default(self):
        """ Trait initialiser """

        viewport = Viewport(component=self.image, enable_zoom=True)
        viewport.view_position = [0,0]
        viewport.zoom_tool.max_zoom = 1.0
        viewport.bgcolor="lightsteelblue"
        viewport.tools.append(ViewportPanTool(viewport))
        return viewport


#    @cached_property
#    def _get_image_path(self):
#        """
#        Property getter. Forms the image path from the directory, the
#        name and the format.
#
#        """
#
#        file_name = self.image_name+"."+self.image_format
#
#        return join(self.image_dir, file_name)


    def _network_changed(self, old, new):
        """ Event handler """

        if self.network_dot is not None:
            self.network_dot.network = new


#    def _image_path_changed(self, new):
#        """ Keeps the image component path up-to-date """
#
#        self.image.image_path = new
#
#        self.image.request_redraw()


    @on_trait_change("network,image_format,program,network_dot.updated")
    def refresh_image(self):
        """ Redraw compute the image and request that it be redrawn """

#        self.network_dot.dot.write(
#            path=self.image_path,
#            prog=self.program,
#            format=self.image_format
#        )

        image_code = self.network_dot.dot.create(
            prog=self.program,
            format=self.image_format_
        )

        stream = StringIO()
        stream.write(image_code)
        self.image.image_file = stream

        self.image.request_redraw()

##        f = file("/tmp/pylon.dot", "wb")
##        f.write(self.dot.to_string())
#
#        #wx.ImageFromStream(f)
#
#        #wx.Image(GRAPH_IMAGE_FILE, wx.BITMAP_TYPE_ANY)
#        #wx.ImageFromStream(self.image, wx.BITMAP_TYPE_PNG)
#        #wx.ImageFromStreamMime(self.image, mimetype="image/gif")

#------------------------------------------------------------------------------
#  Standalone call:
#------------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    import logging
    logger = logging.getLogger()
    logger.addHandler(logging.StreamHandler(sys.stdout))
    logger.setLevel(logging.DEBUG)

    from pylon.api import Network, Bus, Branch
    n = Network()
    v1 = Bus(name="v_1")
    v2 = Bus(name="v_2")
    v3 = Bus(name="v_3")
    e1 = Branch(network=n, source_bus=v1, target_bus=v2, name="e_1")
    e2 = Branch(network=n, source_bus=v1, target_bus=v3, name="e_2")
    e3 = Branch(network=n, source_bus=v2, target_bus=v3, name="e_3")
    n.buses=[v1, v2]#, v3]
    n.branches=[e1]#, e2, e3]

    graph = GraphImage(network=n)
    graph.configure_traits()

# EOF -------------------------------------------------------------------------
