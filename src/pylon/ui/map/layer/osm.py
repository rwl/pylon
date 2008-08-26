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

""" Defines a layer for the Open Street Map tile server """

#------------------------------------------------------------------------------
#  Imports:
#------------------------------------------------------------------------------

from math import pow, ceil, floor
from StringIO import StringIO

from urllib2 import \
    ProxyHandler, build_opener, OpenerDirector, HTTPError, URLError

from enthought.traits.api import implements, Int, Trait
from enthought.enable.api import Canvas, ColorTrait

from i_layer import ILayer
from tile import Tile

#------------------------------------------------------------------------------
#  Constants:
#------------------------------------------------------------------------------

MISSING_TILE_URL = "http://openstreetmap.org/openlayers/img/404.png"

#------------------------------------------------------------------------------
#  "OSM" class:
#------------------------------------------------------------------------------

class OSM(Canvas):
    """ Defines a layer for the Open Street Map tile server """

    implements(ILayer)

    #--------------------------------------------------------------------------
    #  "Canvas" interface:
    #--------------------------------------------------------------------------

    bgcolor = ColorTrait("darkturquoise")

    draw_axes = True

    #--------------------------------------------------------------------------
    #  "OSM" interface:
    #--------------------------------------------------------------------------

    zoom_level = Int

    # Tile resolution
    resolution = Int(256)

    # Opener of URLs
    opener = Trait(OpenerDirector)

    #--------------------------------------------------------------------------
    #  Trait initialisers:
    #--------------------------------------------------------------------------

    def _opener_default(self):
        """ Trait initialiser """

        proxies = {"http": "http://www-cache5.strath.ac.uk:8080"}
        proxy_handler = ProxyHandler(proxies)
#        proxy_auth_handler = HTTPBasicAuthHandler()
#        proxy_auth_handler.add_password('realm', 'host', 'username', 'password')

        return build_opener(proxy_handler)#, proxy_auth_handler)


    def add_tiles(self, pos, width, height):
        """ Filename(url) format is /zoom/x/y.png """

        res = self.resolution
        zoom = self.zoom_level

        # Viewport bounds
        minx, miny = pos
        maxx = minx + width
        maxy = miny + height

        print "BOUNDS: (%f, %f) (%f, %f)" % (minx, miny, maxx, maxy)

        n = int(pow(2, zoom)) # n-by-n map

        # Bounds of tiles visible in the viewport
        minx_tile = int(floor(minx/res))
        maxx_tile = int(ceil(maxx/res))
        miny_tile = int(floor(miny/res))
        maxy_tile = int(ceil(maxy/res))

        print "VISIBLE: (%d, %d) (%d, %d)" % (minx_tile, miny_tile, maxx_tile, maxy_tile)

        for x in range(minx_tile, maxx_tile):
            for y in range(miny_tile, maxy_tile):
                print "POSITION: (%d, %d)" % (x*res, y*res)
                if not self.components_at(x*res, y*res):
                    # Tile coords relative to map
                    x_tile = ((x % n) + n) % n

                    print "TILE: (%d, %d) %d %d" % (x, y, n, x_tile)

                    img = self.get_image(zoom, x_tile, n-(y+1), n)

                    img_file = StringIO()
                    img_file.write(img.read())

                    tile = Tile(
                        image=img_file, bounds=[res, res],
                        position=[x*res, y*res]
                    )
                    self.add(tile)

#                    from enthought.enable.primitives.api import Box
#
#                    box = Box(
#                        color="steelblue",
#                        border_color="darkorchid", border_size=2,
#                        bounds=[res, res],
#                        position=[x*res, y*res]
#                    )
#                    self.add(box)


    def get_image(self, zoom, x, y, limit):
        """ Returns an image from the OSM server as a file-like object """

        if (y < 0) or (y >= limit):
            url = MISSING_TILE_URL
        else:
            url = "http://tile.openstreetmap.org/%s/%s/%s.png" % (zoom, x, y)

        u = self.opener.open(url)

        return u

# EOF -------------------------------------------------------------------------
